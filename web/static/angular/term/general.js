'use strict';
function GeneralCtrl($scope, $http, $compile, $timeout) {
  var resultModal = angular.element('.m-result');
  var resultContent = resultModal.find('p');

  $scope.search = {};

  $scope.setModal = function(content, type){
    resultModal.removeClass('m-negative');
    if (type == 'error') {
        resultModal.addClass('m-negative');
    }
    resultModal.hide();
    resultModal.show();
    resultContent.text(content);
    setTimeout(function(){
      resultModal.hide();
    }, 5000);
  };

  $scope.$watch('pagination.cur', function(pagination) {
    var search = $scope.search;
    search.page = $scope.pagination.cur;
    if (search.type == 'person'){
      $scope.getReportbyPerson(search);
    }
  });

  //Отчет по сотрудникам
  $scope.getReportbyPerson = function(search) {
    if (search.page == undefined) search.page = 1;

    $http.post('/report/person/select', search).success(function(data) {
        $scope.reports = data.report;
        $scope.page_count = data.count;
    });
  };

  //Пагинация
  $scope.maxPages=function(){
    return Math.ceil($scope.page_count/$scope.search.limit);                
  }
  $scope.pagination = {
    cur: 1,
    total: $scope.maxPages(),
    display: 15
  }
}
