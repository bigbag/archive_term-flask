'use strict';

angular.module('term').controller('UserController', 
  function($scope, $http, $compile, $timeout, contentService) {

  //Авторизация
  $scope.login = function(user, valid) {
    if (!valid) return false;
    $http.post('/login', user).success(function(data) {
      if (data.error === 'yes') {
        contentService.setModal(data.content, 'error');

        angular.element('.f-login input[name=email]').addClass('error');
        angular.element('.f-login input[name=password]').addClass('error');
      } else {
        $(location).attr('href','/');
      }
    });
  };

  //Удаляем класс error при изменении поля
  $scope.$watch('user.email + user.password', function(user) {

    if ($scope.user) {
      angular.element('.f-login input[name=email]').removeClass('error');
      angular.element('.f-login input[name=password]').removeClass('error');
    }
  });

  // Восстановление пароля
  $scope.forgot = function(user, valid){
    if (!valid) return false;

    $http.post('/forgot', user).success(function(data) {
      if (data.error === 'yes') {
        contentService.setModal(data.content, 'error');
      } else {
        contentService.setModal(data.content, 'none');
        setTimeout(function(){
          $(location).attr('href','/');
        }, 2000);
      }
    });
  };

  // Смена пароля
  $scope.change = function(user, valid){
    if (!valid) return false;

    $http.post('/change', user).success(function(data) {
      if (data.error === 'yes') {
        contentService.setModal(data.content, 'error');
      } else {
        contentService.setModal(data.content, 'none');
        setTimeout(function(){
          $(location).attr('href','/');
        }, 2000);
      }
    });
  };
});
