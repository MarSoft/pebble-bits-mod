$(function() {
	$("#version_form").submit(function() {
		ver = $("#fw_ver").val();
		code = $.ajax("/patches?ver="+ver);
		$("#patches").html(code);

		return false;
	});
});
