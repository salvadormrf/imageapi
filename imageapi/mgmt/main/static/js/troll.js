// for troll-a-face
var defaultImageUrl = "http://www.nunoteixeira.eu/fotos/200911664220.jpg";
var lastWorkingURL = defaultImageUrl;

$(document).ready(function(){
		
	$("#troll-btn").click(function(){
		trollImageURL($("#troll-url-input").val())
	});
	
	$("img.meme-face-option").click(function(){
		var apiMethod = $(this).data("apiMethod");
		trollImageURL(lastWorkingURL, apiMethod);
	});

	$('.alert .close').live('click',function(){
		$(".alert").addClass("hidden");
	});
});

function trollImageURL(url, method, error){
	var newUrl = "/api/v1/face/" + (method ? method : "troll") + "?url=" + $.trim(url);
	
	$("img.image-preview")
		.attr("src", newUrl)
		.load(function(){
			lastWorkingURL = url;
			$("#troll-url-input").val("");
			error ? $(".alert").removeClass("hidden") : $(".alert").addClass("hidden");
		}).error(function(){
			trollImageURL(defaultImageUrl, method, true);
		});
}
