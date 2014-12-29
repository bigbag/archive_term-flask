'use strict';

angular.module('term').controller('PersonController',
    function($scope, $http, $compile, contentService, dialogService) {

  $scope.error = {};

  //Переадресация на страницу информации о человеке
  $scope.getPersonView = function(person_id) {
  
    var current_list = {
        pagination_cur: $scope.pagination.cur,
        search_period: $scope.search.period, 
        search_status: $scope.search.status, 
        search_request: $scope.search.request,
        search_report_type: $scope.search.report_type,
        need_restore: false
    };
    $.cookie('current_list', angular.toJson(current_list, false), 
        {expires: 1, path:'/'});

    $(location).attr('href','/person/' + person_id);
  };
  
  //Тригер на изменение снятие ошибки при изменение полей
  $scope.$watch('person.card_code + person.name', function(user) {
    $scope.error.name = false;
    $scope.error.card_code = false;
  });
  
  $scope.persontTimeout = [];
  
  //Тригер, устанавливающий таймаут события по-умолчанию при выборе терминала
  $scope.$watch('person_event.term_event_id', function(newValue, oldValue) {
    if (!newValue || !oldValue || newValue == oldValue || angular.isUndefined($scope.persontTimeout[newValue]))
      return false;
      
    $scope.person_event.timeout = $scope.persontTimeout[newValue];
  });


  //Добавляем или редактируем человека
  $scope.savePerson = function(person, valid) {
    if (!valid) {
      $scope.error.name = true;
      contentService.scrollPage('.m-page-name');
      return false;
    }

    person.csrf_token = $scope.token;
    var url = '/person/' + person.id + '/' + person.action;

    $http.post(url, person).success(function(data) {
      contentService.scrollPage('.m-page-name');
      if (data.error === 'yes') {
        $scope.error.card_code = true;
        contentService.setModal(data.message, 'error');
      } else {
        contentService.setModal(data.message, 'success');
        setTimeout(function(){
          $(location).attr('href','/person/' + data.person_id);
        }, 2000);
      }
    });
  };

  //Привязываем карту к человеку
  $scope.bindCard = function(person, valid) {
    if (!valid) {
      $scope.error.card_code = true;
      return false;
    }
    person.action = 'bind_card';

    var url = '/person/' + person.id + '/' + person.action;
    person.csrf_token = $scope.token;
    $http.post(url, person).success(function(data) {
      contentService.scrollPage('.m-page-name');
      if (data.error === 'yes') {
        $scope.error.card_code = true;
        contentService.setModal(data.message, 'error');
      } else {
        contentService.setModal(data.message, 'success');
        setTimeout(function(){
          $(location).attr('href', '/person/' + person.id);
        }, 2000);
      }
    });
  };

  //Отвязываем карту от человека
  $scope.unbindCard = function(person) {
    dialogService.yesNoDialog(function(dialog_result) {
      if (dialog_result != 'yes')
        return false;
      
      var url = '/person/' + person.id + '/unbind_card';
      person.csrf_token = $scope.token;
      $http.post(url, person).success(function(data) {
        if (data.error === 'yes') {
          contentService.setModal(data.message, 'error');
        } else {
          contentService.setModal(data.message, 'success');
          setTimeout(function(){
            $(location).attr('href', '/person/' + person.id);
          }, 2000);
        }
      });
    },
    'Отвязать карту от пользователя<br>"' + person.name +'"?'
    );  
  };

  //Блокируем или разблокируем пользователя
  $scope.lockPerson = function(person) {
    var question = 'Заблокировать пользователя<br>"' + person.name +'"?';
    if (person.status == 0)
        question = 'Разблокировать пользователя<br>"' + person.name +'"?';
    
    dialogService.yesNoDialog(function(dialog_result) {
      if (dialog_result != 'yes')
        return false;
      
      person.csrf_token = $scope.token;
      $http.post('/person/' + person.id + '/lock', person).success(function(data) {
        if (data.error === 'no') {
          if ($scope.person.status === 0) {
            $scope.person.status = 1;
          } else {
            $scope.person.status = 0;
          }
          contentService.setModal(data.message, 'success');
        }
      });
    },
    question
    );
  };

  //Удаляем пользователя
  $scope.removePerson = function(person) {
    dialogService.yesNoDialog(function(dialog_result) {
      if (dialog_result != 'yes')
        return false;
      
      person.csrf_token = $scope.token;
      $http.post('/person/' + person.id + '/remove', person).success(function(data) {
        if (data.error === 'no') {
          contentService.setModal(data.message, 'success');
          setTimeout(function(){
            $(location).attr('href', '/person');
          });
        } else {
          contentService.setModal(data.message, 'error');
        }
      });
    },
    'Удалить пользователя<br>"' + person.name +'"?'
    );
  };


  //Привязываем новое событие к человеку или редактируем уже привязанное
  $scope.saveEventPerson = function(person_event, valid, edit_event_id){
    if (!valid) return false;

    person_event.csrf_token = $scope.token;
    var url = '/person/' + person_event.person_id + '/event/' + person_event.id;
    
    $http.post(url, person_event).success(function(data) {
      //contentService.scrollPage('.m-page-name');
      if (data.error === 'yes') {
        contentService.setModal(data.message, 'error');
      } else {
        contentService.setModal(data.message, 'success');
        if (edit_event_id) {
          setTimeout(function(){
            $(location).attr('href','/person/' + person_event.person_id);
          }, 2000);
        } else {
          var tbody = angular.element('#table_event tbody');
          tbody.append($compile(data.content)($scope));
          contentService.scrollPage('.nav-footer');
        }
      }
    });
  };

  //Переадресация на страницу редактирования привязанного события
  $scope.getPesonEventEdit = function(person_id, person_event_id) {
    $(location).attr('href','/person/' + person_id + '/event/' + person_event_id);
  };

  //Удаляем привязанное событие
  $scope.deleteEventPerson = function(person_event){
    var url = '/person/' + person_event.person_id + '/event/' + person_event.id + '/delete';
    person_event.csrf_token = $scope.token;
    $http.post(url, person_event).success(function(data) {
      contentService.scrollPage('.m-page-name');
      if (data.error === 'yes') {
        contentService.setModal(data.message, 'error');
      } else {
        contentService.setModal(data.message, 'success');
        setTimeout(function(){
          $(location).attr('href','/person/' + person_event.person_id);
        }, 2000);
      }
    });
  };

  $scope.$watch('corp_wallet.limit', function(term) {
    $scope.error.limit = false;
  });

  //Добавляем корпоративный кошелёк
  $scope.saveCorpWallet = function(corp_wallet, valid){
    if (!valid) {
      $scope.error.limit = true;
      return false;
    }
    if (corp_wallet.amount < 100) return false;

    corp_wallet.csrf_token = $scope.token;
    var url = '/person/' + corp_wallet.person_id + '/wallet/save';
    $http.post(url, corp_wallet).success(function(data) {
      if (data.error === 'yes') {
        $scope.error.limit = true;
        contentService.setModal(data.message, 'error');
      } else {
        contentService.setModal(data.message, 'success');
        angular.element('#wallet-info').html($compile(data.content)($scope));
        $scope.corp_wallet = data.corp_wallet;
      }
    });
  };

  //Редактируем кошелёк
  $scope.editCorpWallet = function(corp_wallet){
    $scope.corp_wallet.id = 0;
  };

  //Удаляем корпоративный кошелёк
  $scope.removeCorpWallet = function(corp_wallet){
    corp_wallet.csrf_token = $scope.token;
    var url = '/person/' + corp_wallet.person_id + '/wallet/remove';
    $http.post(url, corp_wallet).success(function(data) {
      if (data.error === 'yes') {
        contentService.setModal(data.message, 'error');
      } else {
        contentService.setModal(data.message, 'success');
        $scope.person.type = 0;
        $scope.corp_wallet.id = 0;
      }
    });
  };

  $scope.import_stage = 0;
  $scope.new_employers = []; //список импортируемых сотрудников
  $scope.added_forms = 0;
  $scope.wrong_forms = [];
  $scope.wrong_cards = [];

  $scope.sendFile = function(el) {
  //импорт сотрудников - парсинг xls
    var $form = $(el).parents('form');
    if ($(el).val() === '') {
        return false;
    }

    $scope.$apply(function() {
        $scope.progress = 0;
    });

    $form.ajaxSubmit({
        type: 'POST',
        success: function(data, statusText, xhr, form) {
            $scope.$apply(function() {
                if (data.error == 'yes'){
                  contentService.setModal(data.message, 'error');
                  return false;
                }

                $scope.new_employers = data.employers;
                $scope.import_stage = 1;
                $scope.added_forms = 0;
                $scope.wrong_forms = [];
                $scope.wrong_cards = [];
            });
        },
    });
  };

  $scope.saveNewEmployers = function(){
  //подтверждение импорта - сохранение новых сотрудников
    if ($scope.new_employers.length > 0)
    {
      var data = {
        csrf_token:$scope.token,
        employers:$scope.new_employers};
      contentService.scrollPage('.m-page-name');
      $http.post('/person/import', data).success(function(data) {
          if (data.error == 'no') {
              $scope.import_stage = 2;
              $scope.new_employers = [];
              $scope.added_forms = data.addedForms;
              $scope.wrong_forms = data.wrongForms;
              $scope.wrong_cards = data.wrongCards;
          }
      });
    }
  };
  
  $scope.setPersonTimeout = function(timeout) {
    $scope.person_event.timeout = timeout;
    alert(timeout);
  }
  
});
