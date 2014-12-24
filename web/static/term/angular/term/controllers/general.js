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
  $scope.$watch('pagination.cur + search.order + search.order_desc + search.period  + search.status + search.request + search.report_type', function() {
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
  
  $scope.sortBy = function(order, desc, e) {
    if ($scope.search.order != order) {
      $scope.search.order_desc = desc;
      $scope.search.order = order;
    } else {
      $scope.search.order_desc = !$scope.search.order_desc;
    }
    
    var current = angular.element(e.currentTarget);
    var headers = current.parents('tr').children('.sortable');
    headers.removeClass('asc').removeClass('desc');
    
    if ($scope.search.order_desc)
      current.addClass('desc');
    else 
      current.addClass('asc');    
  }
  
  //восстановление положения таблицы
  $scope.restoreList = function() {
    var current_list = angular.fromJson($.cookie('current_list'));
    
    if (!current_list || !current_list.need_restore)
      return false;
    
    $scope.pagination.cur = current_list.pagination_cur;
    $scope.search.period = current_list.search_period;
    $scope.search.status = current_list.search_status;
    $scope.search.request = current_list.search_request;
    $scope.search.report_type = current_list.search_report_type;
    $.removeCookie('current_list');
  }
  
  //поднять флаг на восстановление положения таблицы
  $scope.needRestoreList = function() {
    var current_list = angular.fromJson($.cookie('current_list'));
    
    if (!current_list)
      return false;
    
    current_list.need_restore = true;
    $.cookie('current_list', angular.toJson(current_list, false), 
      {expires: 1, path:'/'});
  }
});
