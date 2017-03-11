angular.module('stock_monitor')
  .controller('HomeController', ['$scope', 'queryFactory', 
    function ($scope, queryFactory) { 
    	$scope.stock_no ="SZ002002";
    	$scope.date = "20100105";
    	$scope.seq_len = 60;

	    function init_network(netjson){
	    	var network = new conv1djs.Net(netjson);
	    	var vis_elt = document.getElementById("visnet");
			return network;
	    }
	    queryFactory.sendQuery("network").then(function(resp){
		    if(resp.data["ok"]==1){
		        $scope.network = init_network(resp.data["data"]["net"]);
		        $scope.config = resp.data["data"]["args"];
		        $scope.query_price_seq();
		    }
	    });

		$scope.query_price_seq = function(){
	        var price_url = "price_seq_by_len/" + $scope.stock_no + 
	        "/" + $scope.date + "/" + $scope.seq_len;
	        queryFactory.sendQuery(price_url,$scope.query).then(function(resp){
	            if(resp.data["ok"]==1){
	            	$scope.price_seq = resp.data["data"];
	            	var size = [$scope.seq_len, 1];
	            	var storage = conv1djs.zeros($scope.seq_len);
	            	for(var i=0;i<$scope.seq_len;i++){
	            		storage[i] = $scope.price_seq[$scope.seq_len - i -1]["close"];
	            	}
	            	var tensor = new conv1djs.Tensor(size, storage);
	            	var res = $scope.network.forward(tensor);
	            }
	        });
	    };

	   $scope.layer_class = function(layer_type){
    		switch(layer_type){
    			case "reshape":
    				return "";
    			case "conv":
    				return "ltconv";
    			case "relu":
    				return "ltrelu";
    			case "sofmax":
    				return "ltsoftmax";
    			case "fc":
    				return "ltfc";
    			case "reshape":
    				return "ltpool";
    			default:
    				return "";
    		}
	   };
}]);
