'use strict';

angular.module('term').controller('PersonController', 
    function($scope, $http, $compile, contentService) {

  $scope.error = {};

  //Переадресация на страницу информации о человеке
  $scope.getPersonView = function(person_id) {
    $(location).attr('href','/person/' + person_id);
  };

   //Тригер на изменение снятие ошибки при изменение полей
  $scope.$watch('person.card_code + person.name', function(user) {
    $scope.error.name = false;
    $scope.error.card_code = false;
  });


  //Добавляем или редактируем человека
  $scope.savePerson = function(person, valid) {
    if (!valid) {
      $scope.error.name = true;
      contentService.scrollPage('.m-page-name');
      return false;
    };

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
    };
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

  //Отвязываем карту от человеку
  $scope.unbindCard = function(person) {
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
  };

  //Блокируем или разблокируем пользователя
  $scope.lockPerson = function(person) {
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
  };

  //Удаляем пользователя
  $scope.removePerson = function(person) {
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
  };


  //Привязываем новое событие к человеку или редактируем уже привязанное
  $scope.saveEventPerson = function(person_event, valid){
    if (!valid) return false;

    person_event.csrf_token = $scope.token;
    var url = '/person/' + person_event.person_id + '/event/' + person_event.id;
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
  }

  //Переадресация на страницу редактирования привязанного события
  $scope.getPesonEventEdit = function(person_id, person_event_id) {
    $(location).attr('href','/person/' + person_id + '/event/' + person_event_id);
  }

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
  }

  $scope.$watch('corp_wallet.limit', function(term) {
    $scope.error.limit = false;
  });

  //Добавляем корпоративный кошелёк
  $scope.saveCorpWallet = function(corp_wallet, valid){
    if (!valid) {
      $scope.error.limit = true;
      return false;
    };
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
  }

  //Редактируем кошелёк
  $scope.editCorpWallet = function(corp_wallet){
    $scope.corp_wallet.id = 0;
  }

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
  }
});
