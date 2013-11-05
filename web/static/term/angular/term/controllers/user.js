'use strict';

angular.module('term').controller('UserController', function($scope, $http, $compile, $timeout, alertService) {

  //Авторизация
  $scope.login = function(user, valid) {
    if (!valid) return false;
    $http.post('/login', user).success(function(data) {
      if (data.error == 'yes') {
        alertService.setModal(data.message, 'error');

        angular.element('.f-login input[name=email]').addClass('error');
        angular.element('.f-login input[name=password]').addClass('error');
      }
      else {
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
  $scope.recovery = function(recovery, valid){
    if (!valid) return false;

    var user = $scope.user;
    user.email = recovery.email;

    $http.post('/service/recoveryMail', user).success(function(data) {
      if (data.error == 'yes') {
        angular.element('#recPassForm input[name=email]').addClass('error');
        alertService.setModal(data.content, 'error');
      }
      else if (data.error == 'no'){
        angular.element('#recPassForm').slideUp(400, function() {
          alertService.setModal(data.content, 'none');
        });

        $scope.user.email="";
        $scope.recovery.email="";
        angular.element('#recPassForm input[name=email]').removeClass('error');
      }
    });
  };

  // Смена пароля
  $scope.change = function(user, valid){
    if (!valid) return false;

    $http.post('/service/changepassword', user).success(function(data) {
      if (data.error == 'yes') {
        angular.element('#changePassForm input[name=password]').addClass('error');
        angular.element('#changePassForm input[name=confirmPassword]').addClass('error');
      }
      else if (data.error == 'no'){
        $(location).attr('href','/wallet/');
      }
    });
  };
});
