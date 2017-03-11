var conv1djs = conv1djs || {};
// Common Functinos
(function(global){
	  // return max and min of a given non-empty array.
  var maxmin = function(tensor) {
  	if(!(tensor && tensor.storage)){
  		return {};
  	}
  	var w = tensor.storage;
    if(w.length === 0) { return {}; } // ... ;s
    var maxv = w[0];
    var minv = w[0];
    var maxi = 0;
    var mini = 0;
    var n = w.length;
    for(var i=1;i<n;i++) {
      if(w[i] > maxv) { maxv = w[i]; maxi = i; } 
      if(w[i] < minv) { minv = w[i]; mini = i; } 
    }
    return {maxi: maxi, maxv: maxv, mini: mini, minv: minv, dv:maxv-minv};
  }

	var randf = function(a, b) { return Math.random()*(b-a)+a; }
	var randi = function(a, b) { return Math.floor(Math.random()*(b-a)+a); }
	var randn = function(mu, std){ return mu+gaussRandom()*std; }
	  // Array utilities
	var zeros = function(n) {
		if(typeof(n)==='undefined' || isNaN(n)) { return []; }
		if(typeof ArrayBuffer === 'undefined') {
			// lacking browser support
			var arr = new Array(n);
			for(var i=0;i<n;i++) { arr[i]= 0; }
			return arr;
		} else {
			return new Float64Array(n);
		}
	}
	function assert(condition, message) {
    if (!condition) {
      	message = message || "Assertion failed";
    	if (typeof Error !== "undefined") {
        	throw new Error(message);
    	}
    		throw message; // Fallback
    	}
  	}
  	global.assert = assert;
	global.zeros = zeros;
	global.randf = randf;
	global.randi = randi;
	global.randn = randn;
	global.maxmin = maxmin;
})(conv1djs);
// Tensor
(function(global){
	var Tensor = function(size, storage){
		this.size = size;
		this.n_dimension = size.length;
		this.n_element = (function(){
			var n = 1;
			for(var i=0; i<size.length;i++){
				n *= size[i];
			}
			return n;
		})();
		this.storage = storage || global.zeros(this.n_element);
	};
	Tensor.prototype = {
		reshape: function(size){
			var n_element = 1;
			for(var i=0;i<size.length;i++)
				n_element *= size[i];
			global.assert(n_element == this.n_element, "ReshapeLayer.forward: n_element does not match")
			this.size = size;
			this.n_dimension = size.length;
		},
		get: function(...args){
			global.assert(this.n_dimension == arguments.length, "Tensor.get: wrong para number");
			var ix = 0;
			var step = 1;
			for(var i=this.n_dimension-1;i>=0;i--){
				ix += arguments[i] * step;
				step *= this.size[i];
			}
			global.assert(ix<this.n_element, "Tensor.get: index accross the border"+ ix + " " + this.n_element + arguments[0] + " " + arguments[1]);
			return this.storage[ix];
		},
		set: function(...args){
			global.assert(this.n_dimension == (arguments.length - 1), "Tensor.set: wrong para number");
			var value = arguments[arguments.length - 1];
			var ix = 0;
			var step = 1;
			for(var i=this.n_dimension-1;i>=0;i--){
				ix += arguments[i] * step;
				step *= this.size[i];
			}
			global.assert(ix<this.n_element,"Tensor.set: index accross the border")
			this.storage[ix] = value;
		},
		addFrom: function(tensor){
			for(var i=0;i<this.storage.length;i++){
				this.storage[i] += tensor.storage[i];
			}
		},
		select: function(dim, index){
			global.assert(this.n_dimension>dim, "Tensor.select: dim too big");
			global.assert(this.size[dim]>index, "Tensor.select: index too big");
			var size = [];
			var n_element = 1;
			for(var i=dim+1;i<this.n_dimension;i++){
				size.push(this.size[i]);
				n_element *= this.size[i];
			}
			var storage = global.zeros(n_element);
			var begin = index * n_element;
			for(var i=0;i<n_element;i++){
				storage[i] = this.storage[begin+i];
			}
			return new Tensor(size, storage);
		},
		clone: function(){
			return new Tensor(this.size.slice(), this.storage.slice());
		} 
	};
	global.Tensor = Tensor;
})(conv1djs);
// ConvLayer
(function(global){
	var Tensor = global.Tensor;

	var TempConvLayer = function(opt){
		var opt = opt || {};
		this.layer_type = "conv";
		this.name = opt.name;
		this.kW = opt.kW; // kernel width
		this.dW = opt.dW; // step of the convolution
		this.inputFrameSize = opt.inputFrameSize;
		this.outputFrameSize = opt.outputFrameSize;
		this.weight = new Tensor(opt.weight.size, opt.weight.storage);
		// this.weight = new Tensor([opt.outputFrameSize, opt.kW, opt.inputFrameSize], opt.weight.storage); //outputFrameSize x (inputFrameSize x kW)
		this.bias = new Tensor(opt.bias.size, opt.bias.storage); 
	};
	TempConvLayer.prototype = {
		// x should be 2-dim Tensor, nInputFrame * inputFrameSize
		// output should be 2-dim Tensor, nOutputFrame * outputFrameSize
		forward: function(x){
			global.assert(x.size[1] == this.inputFrameSize, "ConvLayer.forward: inputFrameSize does not match");
			var nInputFrame = x.size[0];
			var nOutputFrame = (nInputFrame - this.kW) / this.dW + 1;
			global.assert(nOutputFrame > 0, "ConvLayer.forward: nOutputFrame should > 0, seqlen x too short")
			var output = new Tensor([nOutputFrame, this.outputFrameSize]);
			for(var t=0;t<nOutputFrame;t++){
				for(var i=0;i<this.outputFrameSize;i++){
					var value = 0.0;
					for(var j=0;j<this.inputFrameSize;j++){
						for(var k=0;k<this.kW;k++){
							value += this.weight.get(i, k * this.inputFrameSize + j) * x.get(this.dW * t + k, j);
						}
					}
					value += this.bias.get(i);
					output.set(t, i, value);
					
				}
			}
			this.output = output;
			return this.output;
		}	
	};
	var LinearLayer = function(opt){
		var opt = opt || {};
		this.layer_type = "fc";
		this.name = opt.name;
		this.weight = new Tensor(opt.weight.size, opt.weight.storage); //outputFrameSize x (inputFrameSize x kW)
		this.bias = new Tensor(opt.bias.size, opt.bias.storage); 
	};
	LinearLayer.prototype = {
		forward: function(x){
			var output = new Tensor(this.bias.size.slice());
			global.assert(x.size[0]==this.weight.size[1], "Linear.forward matrix degree does not match")
			for (var i = 0; i < this.weight.size[0]; i++) {
				var value = 0.0;
				for(var j = 0; j < this.weight.size[1]; j++){
					var xx = (x.n_dimension == 1)?x.get(j):x.get(0,j);
					value += this.weight.get(i, j) * xx;
				}
				if(output.n_dimension==1){
					output.set(i, value);
				}else{
					output.set(0, i, value);
				}
			}
			output.addFrom(this.bias);
			this.output = output;
			return this.output;
		}
	};
	var ReluLayer = function(opt){
		var opt = opt || {};
		this.name = opt.name;
		this.layer_type = "relu";
	};
	ReluLayer.prototype = {
		forward: function(x){
			this.output = x.clone();
			var N = x.storage.length;
			var data = this.output.storage;
			for(var i = 0; i < N; i++){
				if(data[i] == NaN || data[i] < 0){
					data[i] = 0;
				}
			}
			return this.output;
		}
	};
	var ReshapeLayer = function(opt){
		var opt = opt || {};
		this.output_size = opt.size;
		this.name = opt.name;
		this.layer_type = "reshape";
		this.n_element = (function(){
			var n = 1;
			for(var i=0;i<opt.size.length;i++)
				n *= opt.size[i];
			return n})();
	};
	ReshapeLayer.prototype = {
		forward: function(x){
			this.output = x.clone();
			this.output.reshape(this.output_size.slice());
			return this.output;
		}
	};
	var SoftmaxLayer = function(opt){
		var opt = opt || {};
		this.layer_type = "softmax";
		this.name = opt.name;
	};
	SoftmaxLayer.prototype = {
		forward: function(x){
			var outlen = x.storage.length;
			var amax = x.storage[0];
			for(var i=0; i<outlen; i++){
				if(x.storage[i] > amax)
					amax = x.storage[i];
			}
			var es = global.zeros(outlen);
			var esum = 0.0;
	    	for(var i=0; i<outlen; i++) {
	    		var e = Math.exp(x.storage[i] - amax);
				esum += e;
				es[i] = e;
			}
			for(var i=0; i<outlen; i++){
				es[i] /= esum;
			}
			this.output = new Tensor(x.size.slice(), es);
			return this.output;
		}
	};
	global.ReshapeLayer = ReshapeLayer;
	global.TempConvLayer = TempConvLayer;
	global.ReluLayer = ReluLayer;
	global.SoftmaxLayer = SoftmaxLayer;
	global.LinearLayer = LinearLayer;
})(conv1djs);
// network
(function(global){
	var Net = function(netjson) {
    	this.layers = [];
    	for(var i=0;i<netjson.length;i++){
    		var layer = netjson[i];
    		switch(layer["name"]){
    			case "nn.Reshape":
    				this.layers.push(new global.ReshapeLayer(layer));
    				break;
    			case "nn.TemporalConvolution":
    				this.layers.push(new global.TempConvLayer(layer));
    				break;
    			case "nn.Rectifier":
    				this.layers.push(new global.ReluLayer(layer));
    				break;
    			case "nn.SoftMax":
    				this.layers.push(new global.SoftmaxLayer(layer));
    				break;
    			case "nn.Linear":
    				this.layers.push(new global.LinearLayer(layer));
    				break;
    			default:
    				break;
    		}
    	}
	};
	Net.prototype = {
		forward: function(x){
			var act = this.layers[0].forward(x);
	    	for(var i=1;i<this.layers.length;i++) {
	        	act = this.layers[i].forward(act);
	    	}
	    	return act;
		}
	};
	global.Net = Net;
})(conv1djs);
