$(function() {
	$("#version_form").submit(function() {
		ver = $("#fw_ver").val();
		$("#patches").text("Loading...");
		$.ajax("/patches?ver="+ver)
		.done(function(code) {
			if(code)
				$("#patches").html(code);
			else
				$("#patches").html("No compatible patches for this version");
		})
		.fail(function(x, s) {
			$("#patches").text("Error: "+s);
		});

		return false;
	});
});
