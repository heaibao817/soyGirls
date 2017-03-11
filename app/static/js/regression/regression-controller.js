angular.module('stock_monitor').controller('RegController', ['$scope','$rootScope','$location','queryFactory',
    function($scope,$rootScope,$location,queryFactory) {
        var url = "reg/"
        $scope.query = {};
        $scope.seq_len = 60;
        $scope.table = {
            "table_head":[
                "No",
                "stock_no",
                "predict",
                "target",
                "reward",
                "predict - target"
            ]
        };
        function classify_date(datelist){
            var category = {};
            for(var i=0, l=datelist.length; i<l; i++){
                var d = parseInt(datelist[i]);
                var year = Math.floor(d/10000);
                var month = Math.floor((d - 10000 * year)/100);
                if(!(year in category)){
                    category[year] = {};
                }
                if(month in category[year]){
                    category[year][month].push(datelist[i]);
                }else{
                    category[year][month] = [datelist[i]];
                }
                
            }
            return category;
        }
        function fresh(){
            queryFactory.sendQuery(url + $scope.date, $scope.query).then(function(resp){
                if(resp.data["ok"]==1){
                    $scope.query_result = resp.data["data"];
                    delete $scope.query_result["date"]
                    $scope.stock_no = $scope.stock_id2no($scope.query_result[1]["stock_no"]);
                    $scope.query_price_seq();
                }
            });
        };
        queryFactory.sendQuery("datelist").then(function(resp){
            if(resp.data["ok"]==1){
                $scope.datelist = classify_date(resp.data["data"]);
                $scope.yearlist = Object.keys($scope.datelist);
                $scope.year = $scope.yearlist[0];
                $scope.monthlist = Object.keys($scope.datelist[$scope.year]);
                $scope.month = $scope.monthlist[0];
                $scope.date = $scope.datelist[$scope.year][$scope.month][0];
                fresh();
            }
        });
        $scope.stock_id2no = function(stock_id){
            stock_id = parseInt(stock_id);
            if(isFinite(stock_id)){
                var stock_no = String(stock_id);
                if(stock_no.length < 6)
                    stock_no = new Array(6-stock_no.length+1).join("0") + stock_no;
                if (stock_id >= 600000){
                    return "SH" + stock_no;
                }else{
                    return "SZ" + stock_no;
                }
            }
            return null
        };
        $scope.onClickDate = function(d){
            $scope.date = d;
            fresh();
        };
        $scope.onClickYear = function(y){
            alert(y);
            $scope.year = y;
            $scope.date = $scope.datelist[$scope.year][$scope.month][0];
            console.log($scope.date);
            fresh();
        };
        $scope.onClickMonth = function(m){
            $scope.month = m;
            $scope.date = $scope.datelist[$scope.year][$scope.month][0];
            console.log($scope.date);
            fresh();
        };
        $scope.onClickRow = function(stock_id){
            $scope.stock_no = $scope.stock_id2no(stock_id);
            $scope.query_price_seq();
        };
        $scope.isSelected = function(stock_id){
            if($scope.stock_id2no(stock_id) == $scope.stock_no){
                return "success";
            }
            return "";
        }
        $scope.isActive = function(value, target){
            if(value == target){
                return "active";
            }
            return "";
        }
        $scope.query_price_seq = function(){
            var price_url = "price_seq_by_len/" + $scope.stock_no + 
            "/" + $scope.date + "/" + $scope.seq_len;
            queryFactory.sendQuery(price_url,$scope.query).then(function(resp){
                if(resp.data["ok"]==1){
                    $scope.price_seq = resp.data["data"];
                    $scope.xkey = resp.data["xkey"];
                    $scope.ykeys = resp.data["ykeys"];
                    $scope.labels = resp.data["labels"];
                }
            });
        };
        
    }]);