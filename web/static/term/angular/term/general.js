'use strict';

angular.module('term').controller('GeneralCtrl', function($scope, $http, $compile, $timeout) {
  var resultModal = angular.element('.m-result');
  var resultContent = resultModal.find('p');

  //Параметры по умолчанию для пагинации
  $scope.pagination = {
    cur: 1,
    total: 7,
    display: 15
  }

  //Вызываем модальное окно
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

  //Автоскролинг до нужного блока
  $scope.scrollPage = function(dom_name, speed){
    speed = typeof speed !== 'undefined' ? speed : 600;
    var scroll_height = $(dom_name).offset().top;
      $('html, body').animate({
        scrollTop: scroll_height
      }, speed);
  }

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

  //Тригер на запрос табличных данных по параметрам
  $scope.$watch('pagination.cur + search.period  + search.status', function() {
    if (!$scope.search) return false;
    var search = $scope.search;
    search.page = $scope.pagination.cur;

    if (search.action_type == 'get_grid_content') {
      $scope.getGridContent(search);
    }
  });

  //Список периодов для отчетов
  $scope.report_detaled_periods = [
    {name:'День', value:'day'},
    {name:'Неделя', value:'week'},
    {name:'Месяц', value:'month'},
  ];

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

  //Переадресация на страницу информации о терминале
  $scope.getTerminalView = function(term_id) {
    $(location).attr('href','/terminal/' + term_id);
  };

  //Тригер на изменение снятие ошибки при изменение полей, в форме добавления терминала
  $scope.$watch('term.id + term.name', function(term) {
    if ($scope.term) {
      angular.element('input[name=id]').removeClass('error');
      angular.element('input[name=name]').removeClass('error');
    }
  });


  //Добавляем новый или редактируем старый терминал
  $scope.saveTerminal = function(term, valid) {
    if (!valid) {
      angular.element('#add_term input[name=id]').addClass('error');
      angular.element('#add_term input[name=name]').addClass('error');
      $scope.scrollPage('.m-page-name');
      return false;
    };
    var url = '/terminal/' + term.id + '/' + term.action;
    term.csrf_token = $scope.token;
    $http.post(url, term).success(function(data) {
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

  //Блокируем и разблокируем терминал
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

  //Переадресация на страницу редактирования привязанного события
  $scope.getTermEventEdit = function(term_id, term_event_id) {
    $(location).attr('href','/terminal/' + term_id + '/event/' + term_event_id);
  };


  //Привязываем новое событие к терминалу или редактируем уже привязанное
  $scope.saveEventTerminal = function(term_event, valid){
    if (!valid) return false;

    if (term_event.id == undefined) term_event.id = 0;
    term_event.csrf_token = $scope.token;

    var url = '/terminal/' + term_event.term_id + '/event/' + term_event.id;
    $http.post(url, term_event).success(function(data) {
      $scope.scrollPage('.m-page-name');
      if (data.error == 'yes') {
        $scope.setModal(data.message, 'error');
      }
      else {
        $scope.setModal(data.message, 'success');
        setTimeout(function(){
          $(location).attr('href','/terminal/' + term_event.term_id);
        }, 2000);
      }
    });  
  }

  //Удаляем привязанное событие
  $scope.deleteEventTerminal = function(term_event){
    var url = '/terminal/' + term_event.term_id + '/event/' + term_event.id + '/delete';
    term_event.csrf_token = $scope.token;
    $http.post(url, term_event).success(function(data) {
      $scope.scrollPage('.m-page-name');
      if (data.error == 'yes') {
        $scope.setModal(data.message, 'error');
      }
      else {
        $scope.setModal(data.message, 'success');
        setTimeout(function(){
          $(location).attr('href','/terminal/' + term_event.term_id);
        }, 2000);
      }
    });  
  }

});
