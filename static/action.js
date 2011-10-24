$(document).ready(function() {
	$("#tab_container").tabs();
});

var req = null;

function submit() {
	try {
		// Mozilla, Opera, Safari, Chrome, IE7+
		req = new XMLHttpRequest();
	} catch(e) {
		try {
			// MS IE6
			req = new ActiveXObject("Microsoft.XMLHTTP");
		} catch(e) {
			try {
				// MS IE5
				req = new ActiveXObject("Msxml2.XMLHTTP");
			} catch(e) {
				req = null;
			}
		}
	}
	
	if (req) {
		informat = document.getElementById("in");
		outformat = document.getElementById("out");
		// selected tab
		var $tabs = $('#tab_container').tabs();
        var selected = $tabs.tabs('option', 'selected'); // => 0
        if(selected == 0) {
		    uri = document.getElementById("uri");
		    if(!uri.value)
			    uri.value = "http://www.ebusiness-unibw.org";
		    var query = "?url="+encodeURIComponent(uri.value)+"&if="+informat.options[informat.selectedIndex].value+"&of="+outformat.options[outformat.selectedIndex].value;
		    req.open("GET", "/parse"+query, true);
		    req.send(null);
		}
		else if(selected == 1) {
		    content = document.getElementById("textbox");
		    var query = "content="+encodeURIComponent(content.value)+"&if="+informat.options[informat.selectedIndex].value+"&of="+outformat.options[outformat.selectedIndex].value;
		    req.open("POST", "/parse", true);
		    req.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
		    req.send(query);
		}
		//alert(query);
		document.getElementById("serialization").innerHTML = "<center><progress></progress></center>";
		req.onreadystatechange = function() {
			//alert(req.readyState);
			if (req.readyState == 4) {
				//alert(req.status);
				if (req.status == 200) {
					document.getElementById("serialization").innerHTML = "<textarea>"+req.responseText+"</textarea>";
				}
				else document.getElementById("serialization").innerHTML = "<p style='color: red; font-weight: bold; padding-top: 12px'>No response</p>";
			}
		}
		//req.send(null);
	}
}