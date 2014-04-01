'use strict';

angular.module('term').controller('ReportController', 
  function($scope, $http, $compile) {

  //Список периодов для отчетов
  $scope.report_detaled_periods = [
    {name:'День', value:'day'},
    {name:'Неделя', value:'week'},
    {name:'Месяц', value:'month'},
  ];

  $scope.report_stack = {};

  $scope.getEmails = function() {
    if (!$scope.report_stack.email) return [];
    else return $scope.report_stack.email;
  };

  $scope.getEmailsBlock = function(key, value) {
    return '<span class="f-email-case g-radius-main">' + 
        value +
        '<i class="g-round" ng-click="removeEmailFromStack('+
        key +
        ', $event)"></i></span>';
  };

  //Добавляем email в список рассылки отчетов
  $scope.addEmailInStack = function(report_stack) {
    if (angular.isUndefined(report_stack.curent_email)) return false;
    
    var email = $scope.getEmails();
    email[email.length] = report_stack.curent_email;

    var new_email = $scope.getEmailsBlock(email.length, report_stack.curent_email);
    angular.element('.f-select-email').append($compile(new_email)($scope));
    $scope.report_stack.email = email;

    delete $scope.report_stack.curent_email;
  };

  //Удаляем email из списока рассылки отчетов
  $scope.removeEmailFromStack = function(key, e) {
    var email = $scope.getEmails();
    email.splice(key-1,1);
    $scope.report_stack.email = email;

    angular.element(e.currentTarget).parent().remove();
  }

});