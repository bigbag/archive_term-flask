'use strict';

angular.module('term').controller('PersonController', 
    function($scope, $http, $compile, contentService) {

  //Переадресация на страницу информации о человеке
  $scope.getPersonView = function(person_id) {
    $(location).attr('href','/person/' + person_id);
  };

   //Тригер на изменение снятие ошибки при изменение полей, в форме добавления терминала
  $scope.$watch('person.last_name + person.first_name', function(term) {
    if ($scope.term) {
      angular.element('input[name=last_name]').removeClass('error');
      angular.element('input[name=first_name]').removeClass('error');
    }
  });


  //Добавляем или редактируем человека
  $scope.savePerson = function(person, valid) {
    if (!valid) {
      angular.element('#add_person input[name=last_name]').addClass('error');
      angular.element('#add_person input[name=first_name]').addClass('error');
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
          $(location).attr('href','/terminal');
        }, 2000);
      }
    });   
  };

});