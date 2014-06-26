$(function() {
	$("#version_form").submit(function() {
		ver = $("#fw_ver").val();
		alert("Hello, fw "+ver);
		return false;
	});
});
