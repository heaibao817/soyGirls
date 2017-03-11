// Declare app level module which depends on filters, and services
angular.module('stock_monitor', ['ngResource', 'ngRoute', 'ui.bootstrap', 'ui.date'])
  .config(['$routeProvider', function ($routeProvider) {
    $routeProvider
      .when('/', {
        templateUrl: 'static/views/home/home.html', 
        controller: 'HomeController'})
      .when('/tests', {
        templateUrl: 'static/views/test/tests.html',
        controller: 'TestController'})
      .when('/regression', {
        templateUrl: 'static/views/regression/regression.html', 
        controller: 'RegController'})
      .otherwise({redirectTo: '/'});
  }]);
