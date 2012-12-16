


/*
 

Normal mode
<html class="aAX">

Popup mode
<body class="xE">

*/


// the semi-colon before function invocation is a safety net against concatenated 
// scripts and/or other plugins which may not be closed properly.
;(function($, window, undefined){

  // undefined is used here as the undefined global variable in ECMAScript 3 is
  // mutable (ie. it can be changed by someone else). undefined isn't really being
  // passed in so we can ensure the value of it is truly undefined. In ES5, undefined
  // can no longer be modified.

  // window and document are passed through as local variables rather than globals
  // as this (slightly) quickens the resolution process and can be more efficiently
  // minified (especially when both are regularly referenced in your plugin).

  // Create the defaults once
  var pluginName = 'gmail_bmm',
      document = window.document,
      defaults = {
        propertyName: "value", // add more
      };

  // The actual plugin constructor
  function Plugin(element, options){
    this.element = element;

    // jQuery has an extend method which merges the contents of two or 
    // more objects, storing the result in the first object. The first object
    // is generally empty as we don't want to alter the default options for
    // future instances of the plugin
    this.options = $.extend({}, defaults, options) ;
    this._defaults = defaults;
    this._name = pluginName;
    this.init();
  }
	
  
  // identify components
  Plugin.prototype.init = function(){
    // You already have access to the DOM element and the options via the instance, 
    // e.g., this.element and this.options
    
    var self = this;
    
    // since some elements take time to load, we need to register listeners 
    // for later notifying them
    this.listeners = [];
    this.components = {
    	"cc": function(){ return "user@gmail.com"; },
    	"bcc": function(){ return "user@gmail.com"; },
    	"subject": function(){ return "user@gmail.com"; },
    	"editor": function(){ return "user@gmail.com"; },
    	"editorToolbar": function(){ return "user@gmail.com"; },
    	"panelButtons": function(){
    		return $("div[role=navigation] div.Q4uFlf");
    	},
    	"sendButton": function(){
    		return $("div[role=navigation] div.Q4uFlf div.nS");
    	},
    };
	
	    
    this.addListener("compose", function(data){
   		this.log("Found compose Area");
   		
   		console.log(this.getComponent("panelButtons"));
   		console.log(this.getComponent("sendButton"));
   		
   		
   		var $panelButtons = this.getComponent("panelButtons");
   		var $sentButton = this.getComponent("sendButton").clone();
   		

   		$sentButton
   			.unbind()
   			.addClass("T-I-ax7")
   			.addClass("xxx-test")
   			.removeClass("T-I-KE")
   			.find("b")
   			.text("test");
   		
   		$panelButtons.prepend($sentButton);
   		
    });
    
    this.addListener("load", function(data){
    	this.log("GOT LOAD with data: " + data);
    	
    	// find mode
    	
    	// try to detect compose
    	// TODO milisec global
    	
    	

    	
    	
  		var detectComposeForm = function(){
    		var res = $("body").find("form[method=POST]");
    		if(res.length){
    			this.fireEvent("compose", {});
    			clearInterval(waitForComposeTimer);
    		}
    	};
    	var waitForComposeTimer = setInterval($.proxy(detectComposeForm, this), 500);
    	
    	/*
		$(window).bind('hashchange', function(el){
		  console.log(location.hash);
		  if(location.hash.split("#")[1] == "compose")
		  	self.fireEvent("compose", {});
		});*/
    	
    });
    
    // ???
    this.fireEvent("load", {});
    
  };
  
  
  // detect mode
  // find elements
  //Plugin.prototype._waitForCompose = function(){};
  
  
  Plugin.prototype.addEditorIcon = function(){};
  Plugin.prototype.addPanelButton = function(){};
  Plugin.prototype.pasteAtEnd = function(){};
  Plugin.prototype.pasteAtStart = function(){};
  Plugin.prototype.isCompose = function(){};
  
  
  Plugin.prototype.getComponent = function(name){
  	return this.components[name]();
  };
  
  Plugin.prototype.fireEvent = function(eventName, eventData){
  	var callFunction = function(i, l){
  		if(l.name == eventName){
			l.fn.call(this, eventData);
		}
	};
  	// call function with context "this" (check JQuery proxy)
	$.each(this.listeners, $.proxy(callFunction, this));
  };
  
  Plugin.prototype.addListener = function(name, fn){
  	this.listeners.push({"name": name, "fn": fn});
  };
  
  Plugin.prototype.removeListener = function(name, fn){
  	var updatedListeners = [];
  	$.each(this.listeners, function(i, l){
  		if(!((l.name == name) && (l.fn == fn))){
  			// only add if different listener name and function
  			updatedListeners.push(l);
  		}
  	});
  	// update listeners
  	this.listeners = updatedListeners;
  };
  
  // logger
  Plugin.prototype.log = function(msg){
 	console.log(this._name + ": " + msg);
  };

  // A really lightweight plugin wrapper around the constructor, 
  // preventing against multiple instantiations
  $.fn[pluginName] = function(options){
    return this.each(function(){
      if (!$.data(this, 'plugin_' + pluginName)) {
        $.data(this, 'plugin_' + pluginName, new Plugin(this, options));
      }
    });
  }

}(jQuery, window));


$(document).ready(function(){
	$("body").gmail_bmm();
});



/*
appAPI.ready(function($) {
		
	var tabId = appAPI.getTabId();
	
    //alert("My new Crossrider extension works! The current page is: " + document.location.href);
    console.log(document.location.href);
	console.log("hello from tab " + tabId);
	
});


//console.log(document.location.href);
//console.log(appAPI);


// NICE class here...

//init

var $res = $("body").find(".ata-asE").next("div");
var $composeArea = undefined;


var t = setInterval(function(){
			var $composeArea = $res.find("form[method=POST]");
			console.log($composeArea);
			clearInterval(t);
		}, 500);
		
		
		
// copy class methods...

//div[role=toolbar]

// need to create an mapping

addSignature
pasteAtSelection
getContentBody




var modes = {
	"normal": {
		"":  ""//$("body").find(".ata-asE").next("div")
	}
};


*/



























