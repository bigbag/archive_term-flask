'use strict';

angular.module('term').controller('GeneralController', 
    function($scope, $http, $compile) {
  
  //Параметры по умолчанию для пагинации
  $scope.pagination = {
      cur: 1,
      total: 7,
      display: 15
    };

  //Загружаем динамический шаблон
  $scope.getContent = function(e, parent, action){
    if (!parent) return false;
    if (!action) return false;
    if (!e) {
      var content_div = angular.element('.section-container').find('.content');
    }
    else {
      var content_div = angular.element(e.currentTarget).next('.content');
    }

    var url = '/' + parent + '/content/' + action;
    $http.post(url, $scope.search).success(function(data) {
      if (data.error == 'no') {
        content_div.html($compile(data.content)($scope));    
      }
    });
  }

  //Запрос на отображение табличных данных
  $scope.getGridContent = function(search) {
    if (search.page == undefined) search.page = 1;

    var url = window.location.pathname;
    $http.post(url, search).success(function(data) {
      $scope.result = data.result;
      $scope.search.page_count = data.count;
      $scope.pagination.total = Math.ceil(data.count/$scope.search.limit);
    });
  };

  //Тригер на запрос табличных данных по параметрам
  $scope.$watch('pagination.cur + search.period  + search.status', function() {
    if (!$scope.search) return false;
    var search = $scope.search;
    search.page = $scope.pagination.cur;

    if (search.action_type == 'get_grid_content') {
      $scope.getGridContent(search);
    }
  });
});
