'use strict';
var term = angular.module('term', ['ui.keypress']);

term.config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[{');
  $interpolateProvider.endSymbol('}]}');
});

