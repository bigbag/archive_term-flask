'use strict';
angular.module('term', ['ui.pagination', 'ngAnimate']);

angular.module('term').config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[{');
  $interpolateProvider.endSymbol('}]}');
});