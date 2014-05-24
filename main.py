# encoding: utf-8
"""
main.py

This file is part of RDF Translator.

Copyright 2011-2014 Alex Stolz. E-Business and Web Science Research Group, Universitaet der Bundeswehr Munich.

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


Main page of the converter, providing the necessary request handlers.

class TranslatorHandler: request handler
"""

import os
import logging
import webapp2
import traceback

import translator
import rdflib
from rdflib.parser import create_input_source

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

__author__ = "Alex Stolz"
__copyright__ = "Copyright 2011-2014, Universitaet der Bundeswehr Munich"
__credits__ = ["Martin Hepp", "Andreas Radinger"]
__license__ = "LGPL"
__version__ = "1.3.6"
__maintainer__ = "Alex Stolz"
__email__ = "alex.stolz@ebusiness-unibw.org"
__status__ = "Deployment"

debug = False

class TranslatorHandler(webapp2.RequestHandler):
    """Common request handler."""
    
    # (from)/(to)/(html?)/(url)
    def prepareArgs(self, arg1, arg2, arg3, arg4, arg5):
        """Read in arguments and prepare further processing."""
        args = [arg1, arg2, arg3, arg4, arg5]
        
        self.html = False
        self.page = None
        self.content = None
        self.three_oh_three = False
        
        if not args[0]:
            # old request using /parse?if=<if>&of=<of>&url=<uri><&html=1>
            self.page = self.request.get("url")
            self.source_format = self.request.get("if") or "detect"
            self.target_format = self.request.get("of")
            self.html_string = ""
            if self.request.get("html") == "1":
                self.html = True
                self.html_string = "/html"
            self.content = self.request.get("content")
            if not self.content:
                location = "/convert/%s/%s%s/%s" % (self.source_format, self.target_format, self.html_string, self.page)
                self.response.headers['Location'] = location.encode("utf-8")
                self.response.set_status(303)
                self.three_oh_three = True
            return
        
        self.source_format = args[0]
        self.target_format = args[1]
        
        if args[3]:
            self.page = args[3]
            if args[2] == "html":
                self.html = True
            elif args[2] == "pygmentize":
                self.do_pygmentize = True
        elif args[2]:
            self.page = args[2]
            
        if self.page == "content":
            if args[4]:
                self.content = args[4]
            else:
                self.content = self.request.get("content")
        else:
            if self.page and not self.page.find("://") > 0:
                self.page = "http://%s" % self.page
    
    def processRequest(self):
        """Interpret a request, relay to further processing and prepare response headers."""
        global debug
        if "rdf-translator-dev" in self.request.url:
            debug = True
        
        if self.html == True:
            self.do_pygmentize = True
            self.response.headers['Content-Type'] = "text/html"
        else:
            if self.target_format == "pretty-xml" or self.target_format == "xml":
                self.response.headers['Content-Type'] = "application/rdf+xml"
            elif self.target_format == "n3":
                self.response.headers['Content-Type'] = "text/n3"
            elif self.target_format == "turtle":
                self.response.headers['Content-Type'] = "text/turtle"
            elif self.target_format == "nquads":
                self.response.headers['Content-Type'] = "text/x-nquads"
            elif self.target_format == "nt":
                self.response.headers['Content-Type'] = "text/plain"
            elif self.target_format == "trix":
                self.response.headers['Content-Type'] = "application/xml"
            elif self.target_format == "rdf-json" or self.target_format == "rdf-json-pretty":
                self.response.headers['Content-Type'] = "application/json"
            elif self.target_format == "json-ld":
                self.response.headers['Content-Type'] = "application/ld+json"
            elif self.target_format == "rdfa" or self.target_format == "microdata":
                self.response.headers['Content-Type'] = "text/html"
            else:
                self.response.headers['Content-Type'] = "text/plain"
            
        if not self.source_format or self.source_format == "detect":
            if self.content:
                source = create_input_source(data=self.content, format=self.source_format)
                self.source_format = source.content_type
            elif self.page:
                source = create_input_source(location=self.page, format=self.source_format)
                self.source_format = source.content_type
                
            if self.source_format == "text/html":
                self.source_format = "rdfa" # microdata is fallback
                
        try:
            self.response_string = "<p style='color: red; font-weight: bold; padding-top: 12px'>Translation failed</p>"
            if self.content:
                self.response_string = translator.convert(self.content, do_pygmentize=self.do_pygmentize, file_format="string", source_format=self.source_format, target_format=self.target_format)
                if self.response_string.strip() == "" and self.source_format == "rdfa": # fix microdata test
                    self.response_string = translator.convert(self.content, do_pygmentize=self.do_pygmentize, file_format="string", source_format="microdata", target_format=self.target_format)
            elif self.page:
                self.response_string = translator.convert(self.page, do_pygmentize=self.do_pygmentize, file_format="file", source_format=self.source_format, target_format=self.target_format)
                if self.response_string.strip() == "" and self.source_format == "rdfa": # fix microdata test
                    self.response_string = translator.convert(self.page, do_pygmentize=self.do_pygmentize, file_format="file", source_format="microdata", target_format=self.target_format)
            if self.response_string.strip() == "":
                raise Exception("empty result returned")
        except Exception, e:
            self.response.set_status(500)
            if debug:
                tb = traceback.format_exc()
                e = "<pre style=\"color: red\">"+tb+"</pre>"
            error_message = "No error message available"
            if str(e).strip() != "":
                error_message = "Error message:<br>%s" % str(e)
            self.response_string = "<p style='color: red; font-weight: bold; padding-top: 12px'>Could not convert from %s to %s for provided resource...<br><br>%s</p>" % (self.source_format, self.target_format, error_message)
            
        #self.response.headers['Content-Length'] = str(len(self.response_string)) # disabled for security reasons by GAE, http://code.google.com/appengine/docs/python/tools/webapp/responseclass.html#Disallowed_HTTP_Response_Headers
        self.response.headers.add_header("Access-Control-Allow-Origin", "*") # enable CORS

        if self.html == True:
            header = """<!DOCTYPE html>
<html>
    <head>
    	<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    	<title>RDF Translator - %s of %s</title>
    	<link rel="stylesheet" type="text/css" href="/static/pygments.css"/>
    	<style type="text/css">
    	<!--
    	body {
    	  margin: 0 auto;
    	  paddin: 0
    	}
    	div, pre {
    	  margin: 0;
    	  padding: 0;
    	}
    	.highlight {
    	  padding: 12px;
    	  background-color: #FFFFFF;
    	}
    	-->
    	</style>
    	<meta name="author" content="Alex Stolz">
    </head>
    <body>
""" % (self.target_format, self.page)
            self.response_string = header + self.response_string + """
    </body>
</html>"""
              
    def head(self, arg1=None, arg2=None, arg3=None, arg4=None, arg5=None):
        """Handle HTTP HEAD requests."""
        self.do_pygmentize = False
        self.prepareArgs(arg1, arg2, arg3, arg4, arg5)
        self.processRequest()
    
    def get(self, arg1=None, arg2=None, arg3=None, arg4=None, arg5=None):
        """Handle HTTP GET requests."""
        logging.info("uri compontents = %s %s %s %s %s" % (arg1, arg2, arg3, arg4, arg5))
        self.do_pygmentize = False
        self.prepareArgs(arg1, arg2, arg3, arg4, arg5)
        self.processRequest()
        if not self.three_oh_three:
            self.response.out.write(self.response_string)  
        
    def post(self, arg1=None, arg2=None, arg3=None, arg4=None, arg5=None):
        """Handle HTTP POST requests."""
        self.do_pygmentize = False
        self.prepareArgs(arg1, arg2, arg3, arg4, arg5)
        self.processRequest()
        if not self.three_oh_three:
            self.response.out.write(self.response_string)  

# set log level
logging.getLogger().setLevel(logging.INFO)
# run application
# rewrite URLs like /(from)/(to)/(html?)/(url)
application = webapp2.WSGIApplication([
    ('/parse', TranslatorHandler),
    (r'/convert/([^/]*)/([^/]*)/(html)/(content)/(.*)', TranslatorHandler),
    (r'/convert/([^/]*)/([^/]*)/(html|pygmentize)/(.*)', TranslatorHandler),
    (r'/convert/([^/]*)/([^/]*)/(.*)', TranslatorHandler)],
    debug=True)


# hack: quoted os.getpid() in rdflib.plugins.parsers.notation3
# set cache-control header in rdflib.parser headers dict to: 'Cache-Control': 'max-age=10' # set by AS
# minor changes to rdflib/rdflib-microdata
# rdfextras.serializers.rdfjson.py:141
## srlzd = json.dumps(self.jsonObj, indent=2)
## -->
## srlzd = json.dumps(self.jsonObj, indent=2, ensure_ascii=False)
# microdata.py:18:
## tree = parser.parse(location)
## -->
## tree = parser.parse(location, encoding="utf-8")
# rdfextras/parsers/rdfjson.py:116, added val=None, because otherwise it raises sometimes the exception "local variable val referenced before assignment"
# rdflib/plugins/parsers/notation3.py:811
## langcode = re.compile(r'[a-zA-Z0-9]+(-[a-zA-Z0-9]+)?')
## -->
## langcode = re.compile(r'[a-zA-Z]+(-[a-zA-Z0-9]+){0,2}')
# rdflib/plugins/serializers/turtle.py:205
## commented lines for the creation of prefixes -> qnames for subjects and objects
# rdflib/parser.py:67
## user-agent string of http header to "Python RDF Translator (http://rdf-translator.appspot.com/)", otherwise certain web pages will obfuscate certain content, i.e. rich snippet code


# new:
# rdflib_rdfjson/rdfjson_parser.py:134
## val = BNode(value[2:])#val[2:])
# pyMicrodata/microdata.py:314-316
## # rdf-translator doesn't need this!
## #list = generate_RDF_collection( self.graph, item_list )
## #self.graph.add( (URIRef(self.base),self.ns_md["item"],list) )
# pyMicrodata/__init__.py:
##if rdflib.__version__ >= "3.0.0" :
##	from rdflib	import RDF  as ns_rdf
##	from rdflib	import RDFS as ns_rdfs
##	from rdflib import Graph # added by AS
##else :
##	from rdflib.RDFS	import RDFSNS as ns_rdfs
##	from rdflib.RDF		import RDFNS  as ns_rdf
##	from rdflib.Graph import Graph # added by AS

# pyRDFa/initialcontext.py:
## comment out initial_context.ns
# pyMicrodata/__init__.py:
## comment out _bindings