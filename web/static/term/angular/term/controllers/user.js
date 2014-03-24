'use strict';

angular.module('term').controller('UserController', 
  function($scope, $http, $compile, $timeout, contentService) {

  $scope.error = {};

  //Авторизация
  $scope.login = function(user, valid) {
    if (!valid) return false;
    $http.post('/login', user).success(function(data) {
      if (data.error === 'yes') {
        $scope.error.email = true;
        $scope.error.password = true;
        contentService.setModal(data.content, 'error');
      } else {
        $(location).attr('href','/');
      }
    });
  };

  //Удаляем класс error при изменении поля
  $scope.$watch('user.email + user.password', function(user) {
    $scope.error.email = false;
    $scope.error.password = false;
  });

  // Восстановление пароля
  $scope.forgot = function(user, valid){
    if (!valid) return false;

    $http.post('/forgot', user).success(function(data) {
      if (data.error === 'yes') {
        $scope.error.email = true;
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
