'use strict';
function GeneralCtrl($scope, $http, $compile, $timeout) {
  var resultModal = angular.element('.m-result');
  var resultContent = resultModal.find('p');

  $scope.setModal = function(content, type){
    resultModal.removeClass('m-negative');
    if (type == 'error') {
        resultModal.addClass('m-negative');
    }
    resultModal.hide();
    resultModal.show();
    resultContent.text(content);
    setTimeout(function(){
      resultModal.hide();
    }, 5000);
  };

  $scope.scrollPage = function(dom_name, speed){
    speed = typeof speed !== 'undefined' ? speed : 600;
    var scroll_height = $(dom_name).offset().top;
      $('html, body').animate({
        scrollTop: scroll_height
      }, speed);
  }

  $scope.$watch('pagination.cur + search.period', function() {
    if (!$scope.search) return false;
    
    var search = $scope.search;
    search.page = $scope.pagination.cur;

    if (search.action_type == 'get_grid_content') {
      $scope.getGridContent(search);
    }
  });

  $scope.report_detaled_periods = [
    {name:'День', value:'day'},
    {name:'Неделя', value:'week'},
    {name:'Месяц', value:'month'},
  ];

  $scope.getGridContent = function(search) {
    if (search.page == undefined) search.page = 1;

    var url = window.location.pathname;
    $http.post(url, search).success(function(data) {
      $scope.result = data.result;
      $scope.search.page_count = data.count;
      $scope.pagination.total = Math.ceil(data.count/$scope.search.limit);
    });
  };

  $scope.getTerminalInfo = function(term_id) {
    $(location).attr('href','/terminal/' + term_id);
  };

  //Добавляем терминал
  $scope.addTerminal = function(term, valid) {
    if (!valid) {
      angular.element('#add_term input[name=id]').addClass('error');
      angular.element('#add_term input[name=name]').addClass('error');
      $scope.scrollPage('.m-page-name');
      
      return false;
    };
    term.csrf_token = $scope.token;
    $http.post('/terminal/add', term).success(function(data) {
      $scope.scrollPage('.m-page-name');
      if (data.error == 'yes') {
        $scope.setModal(data.message, 'error');
      }
      else {
        $scope.setModal(data.message, 'success');
        setTimeout(function(){
          $(location).attr('href','/terminal');
        }, 2000);
      }
    });
    
  };

  //Добавление терминала, удаляем класс ошибки
  $scope.$watch('term.id + term.name', function(term) {
    if ($scope.term) {
      angular.element('input[name=id]').removeClass('error');
      angular.element('input[name=name]').removeClass('error');
    }
  });

  //Редактируем терминал
  $scope.editTerminal = function(term, valid) {
    if (!valid) {
      angular.element('#add_term input[name=name]').addClass('error');
      $scope.scrollPage('.m-page-name');
      return false;
    };
    var url = '/terminal/' + term.id;
    term.csrf_token = $scope.token;
    $http.post(url, term).success(function(data) {
      $scope.scrollPage('.m-page-name');
      if (data.error == 'yes') {
        $scope.setModal(data.message, 'error');
      }
      else {
        $scope.setModal(data.message, 'success');
      }
    });   
  };

  //Блокировка и разблокировка терминал
  $scope.lockingTerminal = function(term) {
    term.csrf_token = $scope.token;
    if ($scope.term.status == 0) {
      $scope.term.status = 1;
    }
    else {
      $scope.term.status = 0;
    }
    $http.post('/terminal/locking', term).success(function(data) {
      if (data.error == 'no') {
        $scope.setModal(data.message, 'success');
      }
    });  
  }

  $scope.pagination = {
    cur: 1,
    total: 7,
    display: 15
  }
}
