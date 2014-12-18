'use strict';

angular.module('term').controller('GeneralController',
    function($scope, $http, $compile) {

  //Параметры по умолчанию для пагинации
  $scope.pagination = {
      cur: 1,
      total: 7,
      display: 12,
      saved:1
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
  
  //Тригер на сброс пагинации при поиске по фразе
  $scope.$watch('search.request', function(newValue, oldValue) {
    if (!oldValue && newValue) {
      //начало поиска
      //сохраняем номер страницы, установленный до начала поиска
      $scope.pagination.saved = $scope.pagination.cur;
      //и сбрасываем номер страницы для результата поиска
      $scope.pagination.cur = 1;
    } else if (oldValue && newValue) {
      //в процессе поиска
      $scope.pagination.cur = 1;
    } else if (oldValue && !newValue) {
      //выход из поиска
      $scope.pagination.cur = $scope.pagination.saved;
      $scope.pagination.saved = 1;
    }
  });

  //Тригер на запрос табличных данных по параметрам
  $scope.$watch('pagination.cur + search.period  + search.status + search.request + search.report_type', function() {
    if (!$scope.search) return false;
    var search = $scope.search;
    search.page = $scope.pagination.cur;

    if (!angular.isUndefined($scope.search.request)){
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
