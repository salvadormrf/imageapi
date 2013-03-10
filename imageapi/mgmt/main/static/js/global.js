$(document).ready(function(){
	$("img.image-link").click(function(){
		var url = $(this).attr("src");
		window.open(url);
	});
});
