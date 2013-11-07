'use strict';
angular.module('term', [
    'ui.keypress', 
    'ui.pagination',
    ]);

angular.module('term').config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[{');
  $interpolateProvider.endSymbol('}]}');
});