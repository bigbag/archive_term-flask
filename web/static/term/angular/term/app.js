'use strict';

angular.module('term', ['ui.pagination', 'ngAnimate', 'ui.autocomplete']);

angular.module('term').config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[{');
  $interpolateProvider.endSymbol('}]}');
});

angular.module('term').directive('jqdatepicker', function () {
  return {
    restrict: 'A',
    require: 'ngModel',
    link: function (scope, element, attrs) {
      var reportIndex = scope.$eval(attrs.reportIndex);
      element.datepicker({
        beforeShow: function (textbox, instance) {
          instance.dpDiv.css({
            marginLeft: (element.width() / 2 - 50) + 'px'
          });
        },
        beforeShowDay: function (date) {
          if (angular.isUndefined(reportIndex) || angular.isUndefined(scope.result[reportIndex].page_dates))
            return [true, "","Available"];

          var day = date.getDate();
          if (day < 10)
            day = '0' + day;
          var month = date.getMonth() + 1;
          if (month < 10)
            month = '0' + month;
          var date_string = day + "." + month + "." + date.getFullYear();
          if ($.inArray(date_string, scope.result[reportIndex].page_dates) != -1) {
            return [true, "","Available"];
          } else {
            return [false,"","unAvailable"];
          }
        },
        // Локализация:
        closeText: 'Закрыть',
        prevText: '&#x3C;Пред',
        nextText: 'След&#x3E;',
        currentText: 'Сегодня',
        monthNames: ['Январь','Февраль','Март','Апрель','Май','Июнь',
        'Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь'],
        monthNamesShort: ['Янв','Фев','Мар','Апр','Май','Июн',
        'Июл','Авг','Сен','Окт','Ноя','Дек'],
        dayNames: ['воскресенье','понедельник','вторник','среда','четверг','пятница','суббота'],
        dayNamesShort: ['вск','пнд','втр','срд','чтв','птн','сбт'],
        dayNamesMin: ['Вс','Пн','Вт','Ср','Чт','Пт','Сб'],
        weekHeader: 'Нед',
        dateFormat: 'dd.mm.yy',
        firstDay: 1,
        isRTL: false,
        showMonthAfterYear: false,
        yearSuffix: ''
      });
      element.bind('blur keyup change', function(){
        var model = attrs.ngModel;
        if (model.indexOf(".") > -1) scope[model.replace(/\.[^.]*/, "")][model.replace(/[^.]*\./, "")] = element.val();
        else scope[model] = element.val();
      });
    }
  };
});