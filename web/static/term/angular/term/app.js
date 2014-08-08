'use strict';

angular.module('term', ['ui.pagination', 'ngAnimate']);

angular.module('term').config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[{');
  $interpolateProvider.endSymbol('}]}');
});

angular.module('term').directive('jqdatepicker', function () {
    return {
        restrict: 'A',
        require: 'ngModel',
        link: function (scope, element, attrs, ngModelCtrl) {
            
            var reportIndex = scope.$eval(attrs.reportIndex);
        
            element.datepicker({
                dateFormat: 'dd.mm.yy',
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
                }
            });
            element.bind('blur keyup change', function(){
                var model = attrs.ngModel;
                if (model.indexOf(".") > -1) scope[model.replace(/\.[^.]*/, "")][model.replace(/[^.]*\./, "")] = element.val();
                else scope[model] = element.val();
            });
        }
    };
});