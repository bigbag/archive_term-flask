'use strict';

angular.module('term').controller('PersonController', 
    function($scope, $http, $compile, contentService) {

  //Переадресация на страницу информации о человеке
  $scope.getPersonView = function(person_id) {
    $(location).attr('href','/person/' + person_id);
  };

   //Тригер на изменение снятие ошибки при изменение полей, в форме добавления терминала
  $scope.$watch('person.name', function(person) {
    if ($scope.person) {
      angular.element('input[name=user_name]').removeClass('error');
    }
  });


  //Добавляем или редактируем человека
  $scope.savePerson = function(person, valid) {
    if (!valid) {
      angular.element('#add_person input[name=user_name]').addClass('error');
      contentService.scrollPage('.m-page-name');
      return false;
    };
    var url = '/person/' + person.id + '/' + person.action;
    person.csrf_token = $scope.token;
    $http.post(url, person).success(function(data) {
      contentService.scrollPage('.m-page-name');
      if (data.error == 'yes') {
        contentService.setModal(data.message, 'error');
      }
      else {
        contentService.setModal(data.message, 'success');
        setTimeout(function(){
          $(location).attr('href','/person');
        }, 2000);
      }
    });   
  };

  //Тригер на изменение снятие ошибки при изменение полей, в форме добавления кода карты
  $scope.$watch('person.card_code', function(person) {
    if ($scope.person) {
      angular.element('input[name=card_code]').removeClass('error');
    }
  });

  //Привязываем карту к человеку
  $scope.saveCard = function(person, valid) {
    if (!valid) {
      angular.element('input[name=card_code]').addClass('error');
      return false;
    };
    person.action = 'add_card';
    
    var url = '/person/' + person.id + '/' + person.action;
    person.csrf_token = $scope.token;
    $http.post(url, person).success(function(data) {
      contentService.scrollPage('.m-page-name');
      if (data.error == 'yes') {
        contentService.setModal(data.message, 'error');
      }
      else {
        contentService.setModal(data.message, 'success');
        setTimeout(function(){
          $(location).attr('href', '/person/' + person.id);
        }, 2000);
      }
    });  
  };
});