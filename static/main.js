$(function() {
	$("#version_form").submit(function() {
		ver = $("#fw_ver").val();
		$("#patches").text("Loading...");
		$.ajax("/patches?ver="+ver)
		.done(function(code) {
			if(code) {
				$("#patches").html(code);
				$(".patch_box").change(function(e) {
					id = this.id;
					opts = "#"+id+"_options";
					if($(this).is(":checked")) {
						if(!$(opts).is(".loaded")) {
							$.ajax("/options?patch="+id)
							.done(function(code) {
								if(code)
									$(opts).html(code);
								else
									$(opts).text("No options");
								$(opts).addClass("loaded");
							})
							.fail(function(x,y,s) {
								$(opts).text("Error: "+s);
							});
						}
						$(opts).show();
					} else {
						$(opts).hide();
					}
				});
				$("#gen_btn").removeAttr("disabled");
			} else {
				$("#patches").html("No compatible patches for this version");
				$("#gen_btn").addAttr("disabled");
			}
		})
		.fail(function(x,y,s) {
			$("#patches").text("Error: "+s);
			$("#gen_btn").addAttr("disabled");
		});

		return false;
	});
	$("#load_btn").removeAttr("disabled");
});
