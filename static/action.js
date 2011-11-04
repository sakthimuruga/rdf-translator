$(function() {
    $("#tab_container").tabs();
    $("#clip_button").hide();
    /*
    $("#example_rdfa").click(function(){
        $("#textbox").load("/static/examples/rdfa.tmpl");
        $("#in").val("rdfa");
        return false;
    });
    */
    $(".example").each(function() {
       $(this).click(function() {
          $.get("/static/examples/"+$(this).attr("name")+".tmpl", function(data) {
              $("#textbox").html(data);
          });
          //$("#textbox").load("/static/examples/"+$(this).attr("name")+".tmpl");
          $("#in").val($(this).attr("name"));
          return false; 
       });
    });
    
});

/*
$(document).ready(function() {
    $('#clip_button').mouseover(function(){
        ZeroClipboard.setMoviePath('/static/zeroclipboard/ZeroClipboard10.swf');
		clip = new ZeroClipboard.Client();
		clip.setHandCursor(true);
		var txt = $('#serialization').text();
		clip.setText(txt);
		clip.glue( this );
		//Add a complete event to let the user know the text was copied
		clip.addEventListener('complete', function(client, text) {
		    var txt = $('#serialization').text();
    		clip.setText(txt);
    		//alert("copied"+text);
		    $("#clip_button").html("copied to clipboard").fadeIn("slow").fadeOut(2000);
		});
    });
});
*/

/*
$(document).ready(function() {
	$("#tab_container").tabs();
	$("#clip_button").hide();
	
	// copy to clipboard
	ZeroClipboard.setMoviePath('/static/zeroclipboard/ZeroClipboard10.swf');
	$("#clip_button").click(function() {
        var clip = new ZeroClipboard.Client();
        //clip.setHandCursor( true );
        
        clip.glue( 'clip_button' );
        
        clip.setText($('#serialization').text());
        
    	//clip.addEventListener('load', function (client) {
    	//	debugstr("Flash movie loaded and ready.");
    	//});

    	//clip.addEventListener('mouseOver', function (client) {
    		// update the text on mouse over
    	//	clip.setText( $('#serialization').text() );
    	//});
	
    	clip.addEventListener('complete', function (client, text) {
    		debugstr("Copied text to clipboard: " + text );
    		$("#clip_button").html("copied to clipboard");
    	});
	});
});


function debugstr(msg) {
	var p = document.createElement('p');
	p.innerHTML = msg;
	$('#debug').append(p);
}
*/


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
        
        var query = ""
        if(selected == 0) {
		    uri = document.getElementById("uri");
		    if(!uri.value)
			    uri.value = "http://www.ebusiness-unibw.org";
		    query = "url="+encodeURIComponent(uri.value)+"&if="+informat.options[informat.selectedIndex].value+"&of="+outformat.options[outformat.selectedIndex].value;
		}
		else if(selected == 1) {
		    content = document.getElementById("textbox");
		    query = "content="+encodeURIComponent(content.value)+"&if="+informat.options[informat.selectedIndex].value+"&of="+outformat.options[outformat.selectedIndex].value;
		}
		req.open("POST", "/parse", true);
	    req.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
	    req.send(query);
		
		//alert(query);
		$("#clip_button").html("<strong>Copy To Clipboard...</strong>");
		document.getElementById("progressbar").innerHTML = "<center><progress></progress></center>";
		document.getElementById("progressbar").style.display = "block";
		document.getElementById("serialization").style.display = "none";
		document.getElementById("clip_button").style.display = "none";
		req.onreadystatechange = function() {
			//alert(req.readyState);
			if (req.readyState == 4) {
				//alert(req.status);
				if (req.status == 200) {
					document.getElementById("serialization").innerHTML = req.responseText;
					document.getElementById("serialization").style.display = "block";
					document.getElementById("progressbar").style.display = "none";
					document.getElementById("clip_button").style.display = "block";
				}
				else {
				    document.getElementById("progressbar").innerHTML = "<p style='color: red; font-weight: bold; padding-top: 12px; width: 910px; margin: 0 auto'>No response: Either the entered URI does not exist or the server is temporarily down. Please try again later or contact the developers by filling in the Feedback form.</p>";
				}
			}
		}
		//req.send(null);
	}
	return false;
}