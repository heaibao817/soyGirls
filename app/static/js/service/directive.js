angular.module('stock_monitor')
    .directive('fundLine', function() {
        return {
            restrict: 'AE',
            scope: {
                data: '=',
                xkey: '=',
                ykeys: '=',
                labels: '=',
                colors: '@'
            },
            link: function (scope, elem, attrs) {
                var colors;
                if (scope.colors === void 0 || scope.colors === '') {
                    colors = null;
                }else{
                    colors = scope.colors;
                }
                scope.$watch('data', function () {
                    if (scope.data) {
                        if (!scope.morris) {
                            scope.morris = new Morris.Line({
                                element: elem,
                                data: scope.data,
                                xkey: scope.xkey,
                                ykeys: scope.ykeys,
                                ymin: "auto",
                                yLabelFormat:function(y){var num = new Number(y);return num.toFixed(4)},
                                labels: scope.labels,
                                lineColors: colors || ['#0b62a4', '#7a92a3', '#4da74d', '#afd8f8', '#edc240', '#cb4b4b', '#9440ed']
                            });
                        } else {
                            scope.morris.setData(scope.data);
                        }
                    }
                });
            }
        };
    })
    .directive('fundArea', function() {
        return {
            restrict: 'AE',
            scope: {
                data: '=',
                xkey: '=',
                ykeys: '=',
                labels: '=',
                colors: '@'
            },
            link: function (scope, elem, attrs) {
                var colors;
                if (scope.colors === void 0 || scope.colors === '') {
                    colors = null;
                } else {
                    colors = JSON.parse(scope.lineColors);
                }
                scope.$watch('data', function () {
                    if (scope.data) {
                        if (!scope.morris) {
                            scope.morris = new Morris.Area({
                                element: elem,
                                data: scope.data,
                                xkey: scope.xkey,
                                ykeys: scope.ykeys,
                                ymin: "auto",
                                yLabelFormat:function(y){var num = new Number(y);return num.toFixed(4)},
                                labels: ['total'],
                                colors: colors || ['#0b62a4', '#7a92a3', '#4da74d', '#afd8f8', '#edc240', '#cb4b4b', '#9440ed']
                            });
                        } else {
                            scope.morris.setData(scope.data);
                        }
                    }
                });
            }
        };
    });