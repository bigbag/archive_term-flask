'use strict';

angular.module('term').controller('ReportController',
  function($scope, $http, $compile, contentService, dialogService) {

  //Список периодов для отчетов
  $scope.report_detaled_periods = [
    {name:'День', value:'day'},
    {name:'Неделя', value:'week'},
    {name:'Месяц', value:'month'},
  ];

  moment.lang('ru');

  $('#report_interval').daterangepicker({
      format: 'DD.MM.YY',
      // startDate:
      maxDate: moment().endOf('day'),
      locale: {
          applyLabel: 'Применить',
          cancelLabel: 'Отменить',
          monthNames: ['Январь','Февраль','Март','Апрель','Май','Июнь', 'Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь'],
          monthNamesShort: ['Янв','Фев','Мар','Апр','Май','Июн',
            'Июл','Авг','Сен','Окт','Ноя','Дек'],
          dayNames: ['воскресенье','понедельник','вторник','среда','четверг','пятница','суббота'],
          dayNamesShort: ['вск','пнд','втр','срд','чтв','птн','сбт'],
          dayNamesMin: ['Вс','Пн','Вт','Ср','Чт','Пт','Сб'],
          weekHeader: 'Нед',
          firstDay: 1,
          isRTL: false,
          showMonthAfterYear: false,
          yearSuffix: ''
      },
    },
    function(start, end) {
      var pattern = 'YYYY-MM-DD';
      var data = {start:moment(start).format(pattern), end:moment(end).format(pattern)};
      $scope.$apply(function () {
          $scope.report_stack.details = {};
          $scope.report_stack.details.period = data;
      });
    }
  );

  $scope.error = {};
  $scope.report_stack = {};

  //Тригер на изменение снятие ошибки при изменение полей
  $scope.$watch('report_stack.curent_email', function() {
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
  };

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
    if (report_stack.emails.length === 0) return false;

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
  };

  //Переадресация на страницу информации об отчете
  $scope.getReportView = function(report_id) {
    $(location).attr('href','/report/' + report_id);
  };

  //Удаляем отчет
  $scope.removeReport = function(id) {
    dialogService.yesNoDialog(function(dialog_result) {
      if (dialog_result != 'yes')
        return false;
      
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
    },
    'Удалить отчет?'
    );  
  };

  $scope.reportDates = [];

  //Переход к странице отчета по людям из календаря
  $scope.personByDate = function(index, date) {
    if (angular.isUndefined(index) || angular.isUndefined(date))
      return false;

    var page = -1;
    for (var i = 0; i < $scope.result[index].page_dates.length; i++) {
        if ($scope.result[index].page_dates[i] == date) {
            page = i + 1;
            break;
        }
    }

    if (page > 0)
        $scope.pagination.cur = page;
  };

  //Тригер на ввод имени сотрудника
  $scope.$watch('report_stack.request', function() {
    if (angular.isUndefined($scope.report_stack.request)) {
      return false;
    }
    if ($scope.report_stack.request.length < 2)
      {
      return false;
    }
    $scope.report_stack.limit = 1;
    $http.post('/person',$scope.report_stack).success(function(data) {
      $scope.persons = data.result;
    });
  });

  $scope.myOption = {
    options: {
      minLength: 2,
      messages: {
          noResults: '',
          results: function() {}
      },
      source: function (request, response) {
        var search = {
          'token': $scope.token,
          'request': request.term,
          'limit': 5
        };
        $http.post('/person/search',search).success(function(data) {
          if (data.error === 'no') {
            response(data.result);
          }
        });
      }
    },
  };
});