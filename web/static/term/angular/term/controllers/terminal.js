'use strict';

angular.module('term').controller('TerminalController', 
    function($scope, $http, $compile, contentService) {

  //Переадресация на страницу информации о терминале
  $scope.getTerminalView = function(term_id) {
    $(location).attr('href','/terminal/' + term_id);
  };

  //Тригер на изменение снятие ошибки при изменение полей, в форме добавления терминала
  $scope.$watch('term.name', function(term) {
    if ($scope.term) {
      angular.element('input[name=name]').removeClass('error');
    }
  });


  //Добавляем новый или редактируем старый терминал
  $scope.saveTerminal = function(term, valid) {
    console.log(valid);
    if (!valid) {
      angular.element('#add_term input[name=name]').addClass('error');
      contentService.scrollPage('.m-page-name');
      return false;
    };

    if (!term.id) term.id = 0;

    var url = '/terminal/' + term.id + '/' + term.action;
    term.csrf_token = $scope.token;
    $http.post(url, term).success(function(data) {
      contentService.scrollPage('.m-page-name');
      if (data.error === 'yes') {
        contentService.setModal(data.message, 'error');
      } else {
        contentService.setModal(data.message, 'success');
        setTimeout(function(){
          $(location).attr('href','/terminal');
        }, 2000);
      }
    });   
  };

  //Блокируем и разблокируем терминал
  $scope.lockingTerminal = function(term) {
    term.csrf_token = $scope.token;
    $http.post('/terminal/' + term.id + '/locking', term).success(function(data) {
      if (data.error === 'no') {
        if ($scope.term.status === 0) {
          $scope.term.status = 1;
        } else {
          $scope.term.status = 0;
        }
        contentService.setModal(data.message, 'success');
      }
    });  
  }

  $scope.removeTerminal = function(term) {
    term.csrf_token = $scope.token;
    $http.post('/terminal/' + term.id + '/remove', term).success(function(data) {
      if (data.error === 'no') {
        contentService.setModal(data.message, 'success');
        setTimeout(function(){
          $(location).attr('href','/terminal');
        }, 2000);
      } else {
        contentService.setModal(data.message, 'error');
      }
    });  
  }

  //Переадресация на страницу редактирования привязанного события
  $scope.getTermEventEdit = function(term_id, term_event_id) {
    $(location).attr('href','/terminal/' + term_id + '/event/' + term_event_id);
  }


  //Привязываем новое событие к терминалу или редактируем уже привязанное
  $scope.saveEventTerminal = function(term_event, valid){
    if (!valid) return false;

    term_event.csrf_token = $scope.token;

    var url = '/terminal/' + term_event.term_id + '/event/' + term_event.id;
    $http.post(url, term_event).success(function(data) {
      contentService.scrollPage('.m-page-name');
      if (data.error === 'yes') {
        contentService.setModal(data.message, 'error');
      } else {
        contentService.setModal(data.message, 'success');
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
      contentService.scrollPage('.m-page-name');
      if (data.error === 'yes') {
        contentService.setModal(data.message, 'error');
      } else {
        contentService.setModal(data.message, 'success');
        setTimeout(function(){
          $(location).attr('href','/terminal/' + term_event.term_id);
        }, 2000);
      }
    });  
  }

  //Запрос на информацию об сдаче в аренду терминала
  $scope.getRentTerminal= function(){
    var url = window.location.pathname + '/rent/info';
    $http.post(url, {}).success(function(data) {
      if (data.error === 'yes') {
        contentService.setModal(data.message, 'error');
      } else {
        $scope.rents = data.rents;
      }
    });  
  }

  //Сохраняем аренду терминала
  $scope.addRentTerminal = function(info, valid) {
    if (!valid) return false;
    var url = window.location.pathname + '/rent/add';
    info.csrf_token = $scope.token;
    $http.post(url, info).success(function(data) {
      if (data.error === 'yes') {
        contentService.setModal(data.message, 'error');
      } else {
        contentService.setModal(data.message, 'success');
        setTimeout(function(){
          $(location).attr('href', window.location.pathname);
        }, 2000);
      }
    });  
  } 

  //Удаляем аренду терминала
  $scope.removeRentTerminal = function(id) {
    var url = window.location.pathname + '/rent/remove';
    var data = {csrf_token: $scope.token, id: id};
    $http.post(url, data).success(function(data) {
      if (data.error === 'yes') {
        contentService.setModal(data.message, 'error');
      } else {
        contentService.setModal(data.message, 'success');
        $scope.getRentTerminal();
      }
    });  
  } 

});
