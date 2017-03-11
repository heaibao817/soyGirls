angular.module('stock_monitor').factory('queryFactory',
    function ($http,$location) {
        var baseUrl = "/api/";
        var service = {};
        service.sendQuery = function(url,query){
            return $http({
                method : 'GET',
                url : baseUrl + url,
                params : query
            }).then(function successCallback(resp){
                return resp;
            });
        };
        return service;
    });