'use strict';

angular.module('term').controller('GeneralController',
    function($scope, $http, $compile) {

  //Параметры по умолчанию для пагинации
  $scope.pagination = {
      cur: 1,
      total: 7,
      display: 12
    };

  //Обнуление результата
  $scope.setEmptyResult = function() {
    $scope.result = {};
    $scope.pagination.total = 7;
    $scope.search.page_count = 7;
  };

  //Запрос на отображение табличных данных
  $scope.getGridContent = function(search) {
    var url;
    if (angular.isUndefined(search.page)) search.page = 1;
    if (!angular.isUndefined(search.action)){
      url = window.location.pathname + '/' + search.action + '/';
    } else {
      url = window.location.pathname;
    }

    search.csrf_token = $scope.token;

    $http.post(url, search).success(function(data) {
      $scope.result = data.result;
      $scope.search.page_count = data.count;
      $scope.pagination.total = Math.ceil(data.count/$scope.search.limit);
    });
  };

  //Тригер на запрос табличных данных по параметрам
  $scope.$watch('pagination.cur + search.period  + search.status + search.person_name + search.report_type', function() {
    if (!$scope.search) return false;
    var search = $scope.search;
    search.page = $scope.pagination.cur;

    if (!angular.isUndefined($scope.search.person_name)){
      $scope.search.custom_filer = 1;
    }
    if (search.status < 0){
      return false;
    }
    if (search.action_type === 'get_grid_content') {
      $scope.setEmptyResult();
      $scope.getGridContent(search);
    }
  });
});
