'use strict';
function GeneralCtrl($scope, $http, $compile, $timeout) {
  var resultModal = angular.element('.m-result');
  var resultContent = resultModal.find('p');

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

  // $scope.menu = [
  //   {
  //     name:'Главное',
  //     id:'general',
  //     items: [
  //       {id:'person', name:'Сотрудники', url:'/#'},
  //       {id:'terminal', name:'Терминалы', url:'/#'},
  //       {id:'card', name:'Карты', url:'/#'},
  //     ]
  //   },
  //   {
  //     name:'Отчеты',
  //     id:'report',
  //     items: [
  //       {id:'person', name:'По людям', url:'/report/person'},
  //       {id:'terminal',name:'По терминалам', url:'/report/terminal'},
  //       {id:'summ',name:'Платежный оборот', url:'/report/summ'},
  //     ]
  //   },
  //   {
  //     name:'Настройка',
  //     id:'setting',
  //     items: [
  //       {id:'firm', name:'Компания', url:'/#'},
  //     ]
  //   }
  // ];

  $scope.$watch('pagination.cur + search.period', function() {
    var search = $scope.search;
    search.page = $scope.pagination.cur;

    if (search.action_type == 'online'){
      $scope.getReport(search);
    }
  });

  $scope.report_detaled_periods = [
    {name:'День', value:'day'},
    {name:'Неделя', value:'week'},
    {name:'Месяц', value:'month'},
  ];

  //Запрос отчета
  $scope.getReport = function(search) {
    if (search.page == undefined) search.page = 1;
    
    var url = window.location.pathname;
    $http.post(url, search).success(function(data) {
      $scope.reports = data.report;
      $scope.search.page_count = data.count;
      $scope.pagination.total = Math.ceil(data.count/$scope.search.limit);
    });
  };

  $scope.pagination = {
    cur: 1,
    total: 7,
    display: 15
  }
}
