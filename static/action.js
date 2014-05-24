/*
 This file is part of RDF Translator, available at http://rdf-translator.appspot.com/.

 Copyright 2011, 2012 Alex Stolz. E-Business and Web Science Research Group, Universitaet der Bundeswehr Munich.

 RDF Translator is free software: you can redistribute it and/or modify
 it under the terms of the GNU Lesser General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 RDF Translator is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Lesser General Public License for more details.

 You should have received a copy of the GNU Lesser General Public License
 along with RDF Translator.  If not, see <http://www.gnu.org/licenses/>.
*/
 
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
              $("#textbox").val(data);
          });
          //$("#textbox").load("/static/examples/"+$(this).attr("name")+".tmpl");
          $("#in").val($(this).attr("name"));
          return false; 
       });
    });
    
    $("#tabs_uri_link").click(function() {
        $("#uri").focus();
    });
    
    $("#tabs_box_link").click(function() {
        $("#textbox").focus();
    });
    
    $(document).keypress(function(e) {
        var focus = $("*:focus").attr('id')
        if(e.keyCode == 13 && focus in {"uri":1, "in":1, "out":1}) {
            submit();
        }
    });
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
		informat = informat.options[informat.selectedIndex].value;
		outformat = outformat.options[outformat.selectedIndex].value;
		if(!informat) {
		    informat = "detect";
		}
		
		// selected tab
		var $tabs = $('#tab_container').tabs();
        var selected = $tabs.tabs('option', 'selected'); // => 0
        
        var query = ""
        var link = ""
        if(selected == 0) {
		    uri = document.getElementById("uri");
		    if(!uri.value)
			    uri.value = "http://www.ebusiness-unibw.org";
		    query_p1 = "/"+informat+"/"+outformat;
		    query_p2 = "/pygmentize";
		    query_p3 = "/"+encodeURIComponent(uri.value);
            link = "<section><div class=\"shade_box\"><p>You might pick one of the following <strong>persistent URIs</strong> of the output above to share with others or to integrate into your own applications:</p><ul><li><a href='/convert"+query_p1+"/html"+query_p3+"'>highlighted</a> (HTML-rendered)</li><li><a href='/convert"+query_p1+query_p3+"'>raw</a> (delivered with respective media type)</li></ul></div></section>";
            req.open("GET", "/convert"+query_p1+query_p2+query_p3, true);
            req.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    	    req.send(null);
		}
		else if(selected == 1) {
		    content = document.getElementById("textbox");
		    query = informat+"/"+outformat+"/pygmentize/content";
            // link = "Link to <a href='/convert/"+informat+"/"+outformat+"/html/content/"+encodeURIComponent(content.value.replace("'", "%27").replace(/(\n\r|\n|\r)/gm, " "))+"'>Persistent URI</a>.";
            req.open("POST", "/convert/"+query, true);
            req.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    	    req.send("content="+encodeURIComponent(content.value));
		}
		
		//alert(query);
		$("#clip_button").html("<strong>Copy To Clipboard...</strong>");
		$("#converter_link").html("");
		$("#converter_link").css({"display":"none"});
		$("#progressbar").html("<center><progress></progress></center>");
		$("#progressbar").css({"display":"block"});
		$("#serialization").css({"display":"none"});
		$("#clip_button").css({"display":"none"});
		req.onreadystatechange = function() {
			//alert(req.readyState);
			if (req.readyState == 4) {
				//alert(req.status);
				if (req.status == 200) {
				    $("#serialization").html(req.responseText);
				    $("#serialization").slideDown("slow", function() {
				        $("#converter_link").html(link);
                        $("#converter_link").slideDown("slow");
				    });
				    $("#clip_button").fadeIn("slow");
				    $("#progressbar").css({"display":"none"});
				}
				else {
					$("#serialization").html(req.responseText);
				    $("#serialization").slideDown("slow");
					$("#progressbar").css({"display":"none"});
				    //$("#progressbar").html("<p style='color: red; font-weight: bold; padding-top: 12px; width: 910px; margin: 0 auto'>No response: Either the entered URI does not exist or the service is temporarily unavailable. Please try again later or contact the developers by filling in the Feedback form.</p>");
				}
			}
		}
	}
	return false;
}