$(function() {
	$("#version_form").submit(function() {
		ver = $("#fw_ver").val();
		code = $.ajax("/patches/"+ver);
		$("#patches").html(code);

		return false;
	});
});
