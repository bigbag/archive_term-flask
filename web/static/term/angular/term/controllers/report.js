'use strict';

angular.module('term').controller('ReportController', 
  function($scope, $http, $compile, contentService) {

  //Список периодов для отчетов
  $scope.report_detaled_periods = [
    {name:'День', value:'day'},
    {name:'Неделя', value:'week'},
    {name:'Месяц', value:'month'},
  ];

  $scope.report_stack = {};

  $scope.getEmails = function() {
    if (!$scope.report_stack.emails) return [];
    else return $scope.report_stack.emails;
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
    
    var emails = $scope.getEmails();
    emails[emails.length] = report_stack.curent_email;

    var new_email = $scope.getEmailsBlock(emails.length, report_stack.curent_email);
    angular.element('.f-select-email').append($compile(new_email)($scope));
    $scope.report_stack.emails = emails;

    delete $scope.report_stack.curent_email;
  };

  //Удаляем email из списока рассылки отчетов
  $scope.removeEmailFromStack = function(key, e) {
    var emails = $scope.getEmails();
    emails.splice(key-1,1);
    $scope.report_stack.emails = emails;

    angular.element(e.currentTarget).parent().remove();
  }

  //Сохраняем новый отчет
  $scope.saveReportStack = function(report_stack) {
    if (angular.isUndefined(report_stack.emails)) return false;
    if (report_stack.emails.length == 0) return false;

    report_stack.csrf_token = $scope.token;
    var url = '/report/new';
    $http.post(url, report_stack).success(function(data) {
      if (data.error === 'yes') {
        contentService.setModal(data.message, 'error');
      } else {
        contentService.setModal(data.message, 'none');
        setTimeout(function(){
          $(location).attr('href', '/report/list');
        }, 2000);
      }
    });  
  }

});