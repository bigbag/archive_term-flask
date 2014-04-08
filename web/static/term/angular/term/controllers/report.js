'use strict';

angular.module('term').controller('ReportController', 
  function($scope, $http, $compile, contentService) {

  //Список периодов для отчетов
  $scope.report_detaled_periods = [
    {name:'День', value:'day'},
    {name:'Неделя', value:'week'},
    {name:'Месяц', value:'month'},
  ];

  $scope.error = {};
  $scope.report_stack = {};

  //Тригер на изменение снятие ошибки при изменение полей
  $scope.$watch('report_stack.curent_email', function(user) {
    $scope.error.curent_email = false;
    $scope.error.name = false;
  });

  $scope.getEmails = function() {
    if (!$scope.report_stack.emails) return [];
    else return $scope.report_stack.emails;
  };

  $scope.initEmails = function(json) {
    $scope.report_stack.emails = angular.fromJson(json);
  };

  $scope.setEmail = function(email) {
    var emails = $scope.getEmails();
    emails[emails.length] = email;
    return emails;
  };

  //Добавляем email в список рассылки отчетов
  $scope.addEmailInStack = function(report_stack) {
    if (angular.isUndefined(report_stack.curent_email)) return false;
    $scope.report_stack.emails = $scope.setEmail(report_stack.curent_email);

    delete $scope.report_stack.curent_email;
  };

  //Удаляем email из списока рассылки отчетов
  $scope.removeEmailFromStack = function(key, e) {
    var emails = $scope.getEmails();
    emails.splice(key,1);
    $scope.report_stack.emails = emails;

    angular.element(e.currentTarget).parent().remove();
  }

  //Сохраняем новый отчет
  $scope.saveReportStack = function(report_stack, valid) {
    if (!valid) {
      contentService.scrollPage('.m-page-name');
      $scope.error.name = true;
      return false;
    }
    if (angular.isUndefined(report_stack.emails)) {
      contentService.scrollPage('.m-page-name');
      $scope.error.curent_email = true;
      return false;
    }
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

  //Переадресация на страницу информации об отчете
  $scope.getReportView = function(report_id) {
    $(location).attr('href','/report/' + report_id);
  };

  //Удаляем отчет
  $scope.removeReport = function(id) {
    var report_stack = $scope.report_stack;
    report_stack.id = id;
    report_stack.csrf_token = $scope.token;
    $http.post('/report/' + report_stack.id + '/remove', report_stack).success(function(data) {
      if (data.error === 'no') {
        contentService.setModal(data.message, 'success');
        setTimeout(function(){
          $(location).attr('href', '/report/list');
        });
      } else {
        contentService.setModal(data.message, 'error');
      }
    }); 
  };

});