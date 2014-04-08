'use strict';

angular.module('term').controller('GeneralController', 
    function($scope, $http, $compile) {
  
  //Параметры по умолчанию для пагинации
  $scope.pagination = {
      cur: 1,
      total: 7,
      display: 12
    };

  //Загружаем динамический шаблон
  $scope.getContent = function(e, parent, action){
    if (!parent) return false;
    if (!action) return false;
    if (!e) {
      var content_div = angular.element('.section-container').find('.content');
    } else {
      var content_div = angular.element(e.currentTarget).next('.content');
    }

    var url = '/' + parent + '/content/' + action;
    $http.post(url, $scope.search).success(function(data) {
      if (data.error === 'no') {
        content_div.html($compile(data.content)($scope));    
      }
    });
  }

  //Обнуление результата
  $scope.setEmptyResult = function() {
    $scope.result = {};
    $scope.pagination.total = 7;
    $scope.search.page_count = 7;
  }

  //Запрос на отображение табличных данных
  $scope.getGridContent = function(search) {
    if (angular.isUndefined(search.page)) search.page = 1;
    if (!angular.isUndefined(search.action)){
      var url = window.location.pathname + '/' + search.action + '/';
    } else {
      var url = window.location.pathname
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
    
    if (search.action_type === 'get_grid_content') {
      $scope.setEmptyResult();
      $scope.getGridContent(search);
    }
  });
});
