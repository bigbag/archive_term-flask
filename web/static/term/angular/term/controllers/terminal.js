'use strict';

angular.module('term').controller('TerminalController', 
    function($scope, $http, $compile, contentService) {

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
      contentService.scrollPage('.m-page-name');
      return false;
    };
    var url = '/terminal/' + term.id + '/' + term.action;
    term.csrf_token = $scope.token;
    $http.post(url, term).success(function(data) {
      contentService.scrollPage('.m-page-name');
      if (data.error == 'yes') {
        contentService.setModal(data.message, 'error');
      }
      else {
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
    if ($scope.term.status == 0) {
      $scope.term.status = 1;
    }
    else {
      $scope.term.status = 0;
    }
    $http.post('/terminal/locking/' + term.id, term).success(function(data) {
      if (data.error == 'no') {
        contentService.setModal(data.message, 'success');
      }
    });  
  }

  $scope.removeTerminal = function(term) {
    term.csrf_token = $scope.token;
    $http.post('/terminal/remove/' + term.id, term).success(function(data) {
      if (data.error == 'no') {
        contentService.setModal(data.message, 'success');
        setTimeout(function(){
          $(location).attr('href','/terminal');
        }, 2000);
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

    if (term_event.id == undefined) term_event.id = 0;
    term_event.csrf_token = $scope.token;

    var url = '/terminal/' + term_event.term_id + '/event/' + term_event.id;
    $http.post(url, term_event).success(function(data) {
      contentService.scrollPage('.m-page-name');
      if (data.error == 'yes') {
        contentService.setModal(data.message, 'error');
      }
      else {
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
      if (data.error == 'yes') {
        contentService.setModal(data.message, 'error');
      }
      else {
        contentService.setModal(data.message, 'success');
        setTimeout(function(){
          $(location).attr('href','/terminal/' + term_event.term_id);
        }, 2000);
      }
    });  
  }

});