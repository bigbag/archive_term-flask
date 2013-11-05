'use strict';

angular.module('term').controller('ReportController', 
    function($scope, $http, $compile) {

  //Список периодов для отчетов
  $scope.report_detaled_periods = [
    {name:'День', value:'day'},
    {name:'Неделя', value:'week'},
    {name:'Месяц', value:'month'},
  ];

});