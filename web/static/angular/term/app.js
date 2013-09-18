'use strict';
var term = angular.module('term', ['ui.keypress', 'ui.pagination']);

term.config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[{');
  $interpolateProvider.endSymbol('}]}');
});

