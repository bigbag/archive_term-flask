'use strict';
function UserCtrl($scope, $http, $compile, $timeout) {

  var resultModal = angular.element('.m-result');
  var resultContent = resultModal.find('p');

  $scope.setModal = function(content, type){
    resultModal.removeClass('m-negative');
    if (type == 'error') {
        resultModal.addClass('m-negative');
    }
    resultModal.show();
    resultContent.text(content);
    setTimeout(function(){
      resultModal.hide();
    }, 5000);
  };

  //Авторизация
  $scope.login = function(user, valid) {
    if (!valid) return false;
    $http.post('/service/login', user).success(function(data) {
      if (data.error == 'yes') {
        $scope.setModal(data.content, 'error');

        angular.element('#sign-in input[name=email]').addClass('error');
        angular.element('#sign-in input[name=password]').addClass('error');
      }
      else if (data.error == 'no'){
        $(location).attr('href','/wallet/');
      }
      else {
        $(location).attr('href','/');
      }
    });
  };

  // Восстановление пароля
  $scope.recovery = function(recovery, valid){
    if (!valid) return false;

    var user = $scope.user;
    user.email = recovery.email;

    $http.post('/service/recoveryMail', user).success(function(data) {
      if (data.error == 'yes') {
        angular.element('#recPassForm input[name=email]').addClass('error');
        $scope.setModal(data.content, 'error');
      }
      else if (data.error == 'no'){
        angular.element('#recPassForm').slideUp(400, function() {
          $scope.setModal(data.content, 'none');
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
}
