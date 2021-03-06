'use strict';

angular.module('term').controller('TerminalController',
    function($scope, $http, $compile, contentService, dialogService) {

  $scope.error = {};

  //Переадресация на страницу информации о терминале
  $scope.getTerminalView = function(term_id) {
    $(location).attr('href','/terminal/' + term_id);
  };

  //Тригер на изменение снятие ошибки при изменение полей, в форме добавления терминала
  $scope.$watch('term.name + term.hard_id', function(term) {
    $scope.error.name = false;
    $scope.error.hard_id = false;
  });


  //Добавляем новый или редактируем старый терминал
  $scope.saveTerminal = function(term, valid) {
    if (!valid) {
      $scope.error.name = true;
      contentService.scrollPage('.m-page-name');
      return false;
    }

    if (!term.id) term.id = 0;

    var url = '/terminal/' + term.id + '/' + term.action;
    term.csrf_token = $scope.token;
    $http.post(url, term).success(function(data) {
      contentService.scrollPage('.m-page-name');
      if (data.error === 'yes') {
        $scope.error.hard_id = true;
        contentService.setModal(data.message, 'error');
      } else {
        contentService.setModal(data.message, 'success');

        setTimeout(function(){
          $(location).attr('href','/terminal/' + data.id );
        }, 2000);
      }
    });
  };

  //Переадресация на страницу редактирования привязанного события
  $scope.getTermEventEdit = function(term_id, term_event_id) {
    $(location).attr('href','/terminal/' + term_id + '/event/' + term_event_id);
  };

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
  };

  //Удаляем привязанное событие
  $scope.deleteEventTerminal = function(term_event){
    dialogService.yesNoDialog(function(dialog_result) {
      if (dialog_result != 'yes')
        return false;
      
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
    },
    'Удалить событие?'
    );   
  };

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
  };

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
  };

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
  };

  $scope.alarm_stack = {};

  $scope.getEmails = function() {
    if (!$scope.alarm_stack.emails) return [];
    else return $scope.alarm_stack.emails;
  };

  $scope.initEmails = function(json) {
    $scope.alarm_stack.emails = angular.fromJson(json);
  };

  $scope.setEmail = function(email) {
    var emails = $scope.getEmails();
    emails[emails.length] = email;
    return emails;
  };

  //Тригер на изменение снятие ошибки при изменение полей
  $scope.$watch('alarm_stack.curent_email + alarm_stack.interval', function(user) {
      $scope.error.curent_email = false;
      $scope.error.interval = false;
  });

  //Добавляем email в список рассылки оповещений
  $scope.addEmailInStack = function(alarm_stack) {
      if (angular.isUndefined(alarm_stack.curent_email))
          return false;
      $scope.alarm_stack.emails = $scope.setEmail(alarm_stack.curent_email);

      delete $scope.alarm_stack.curent_email;
  };

  //Удаляем email из списока рассылки оповещений
  $scope.removeEmailFromStack = function(key, e) {
      var emails = $scope.getEmails();
      emails.splice(key,1);
      $scope.alarm_stack.emails = emails;

      angular.element(e.currentTarget).parent().remove();
  };

  //Сохранение оповещения
  $scope.saveAlarmStack = function(alarm_stack, valid) {
    $scope.addEmailInStack(alarm_stack);

    if (angular.isUndefined(alarm_stack.emails)) {
      contentService.scrollPage('#alarmForm');
      $scope.error.curent_email = true;
      return false;
    }
    if (!valid) {
      contentService.scrollPage('#alarmForm');
      $scope.error.interval = true;
      return false;
    }

    if (alarm_stack.emails.length === 0) return false;

    alarm_stack.csrf_token = $scope.token;
    alarm_stack.term_id = $scope.term.id;

    $http.post('/alarm/new', alarm_stack).success(function(data) {
      if (data.error === 'yes') {
          contentService.setModal(data.message, 'error');
      } else {
        contentService.setModal(data.message, 'none');
        setTimeout(function(){
          $(location).attr('href', window.location.pathname);
        }, 2000);
      }
    });
  };

  //Удаление оповещения
  $scope.removeAlarmStack = function(alarm_stack) {
    alarm_stack.csrf_token = $scope.token;
    alarm_stack.term_id = $scope.term.id;

    $http.post('/alarm/remove', alarm_stack).success(function(data) {
        if (data.error === 'yes') {
            contentService.setModal(data.message, 'error');
        } else {
          contentService.setModal(data.message, 'none');
          setTimeout(function(){
            $(location).attr('href', window.location.pathname);
          }, 2000);
        }
    });
  };

  //удаление терминала
  $scope.removeTerminal = function(term) {
    dialogService.yesNoDialog(function(dialog_result) {
      if (dialog_result != 'yes')
        return false;
    
      $http.post('/terminal/' + term.id + '/remove').success(function(data) {
        if (data.error === 'yes') {
            contentService.setModal(data.message, 'error');
        } else {
          contentService.setModal(data.message, 'none');
          setTimeout(function(){
            $(location).attr('href','/terminal');
          }, 2000);
        }
      });
    },
    'Терминал ' + term.hard_id + ', ' + term.name + ' и вся история операций по этому терминалу будет удалена. Вы уверены?'
    );    
  }

});
  
/*
  //Блокируем и разблокируем терминал
  $scope.lockingTerminal = function(term) {
    var question = 'Заблокировать терминал<br>"' + term.hard_id +', ' + term.name +'"?';
    if (term.status == 0)
        question = 'Разблокировать терминал<br>"' + term.hard_id +', ' + term.name +'"?';
    
    dialogService.yesNoDialog(function(dialog_result) {
      if (dialog_result != 'yes')
        return false;
      
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
    },
    question
    );
    
  };
*/