# encoding: utf-8
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

import translator
from rdflib.parser import create_input_source
import logging

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

class ParserHandler(webapp.RequestHandler):
    def processRequest(self):
        self.page = self.request.get("url")
        if self.page and not self.page.find("://") > 0:
            self.page = "http://%s" % self.page
        self.content = self.request.get("content")
        self.input_format = self.request.get("if")
        self.output_format = self.request.get("of", default_value="pretty-xml")
        
        if self.output_format == "pretty-xml" or self.output_format == "xml":
            self.response.headers['Content-Type'] = "application/rdf+xml"
        elif self.output_format == "n3":
            self.response.headers['Content-Type'] = "text/n3"
        elif self.output_format == "nt":
            self.response.headers['Content-Type'] = "text/plain"
        elif self.output_format == "trix":
            self.response.headers['Content-Type'] = "application/xml"
        elif self.output_format == "rdf-json" or self.output_format == "rdf-json-pretty":
            self.response.headers['Content-Type'] = "application/json"
        else:
            self.response.headers['Content-Type'] = "text/plain"
            
        if not self.input_format:
            if self.content:
                source = create_input_source(data=self.content, format=self.input_format)
                self.input_format = source.content_type
            elif self.page:
                source = create_input_source(location=self.page, format=self.input_format)
                self.input_format = source.content_type
                
        try:
            self.response_string = self.response_string = "<p style='color: red; font-weight: bold; padding-top: 12px'>Translation failed</p>"
            if self.content:
                self.response_string = translator.parse(self.content, do_pygmentize=self.do_pygmentize, file_format="string", input_format=self.input_format, output_format=self.output_format)
                if self.response_string.strip() == "" and self.input_format == "text/html": # fix microdata test
                    self.response_string = translator.parse(self.content, do_pygmentize=self.do_pygmentize, file_format="string", input_format="microdata", output_format=self.output_format)
            elif self.page:
                self.response_string = translator.parse(self.page, do_pygmentize=self.do_pygmentize, file_format="file", input_format=self.input_format, output_format=self.output_format)
                if self.response_string.strip() == "" and self.input_format == "text/html": # fix microdata test
                    self.response_string = translator.parse(self.page, do_pygmentize=self.do_pygmentize, file_format="file", input_format="microdata", output_format=self.output_format)
            if self.response_string.strip() == "":
                raise Exception
        except Exception, e:
            self.response_string = "<p style='color: red; font-weight: bold; padding-top: 12px'>Could not convert from %s to %s for provided resource...<br><br>Error Message:<br>%s</p>" % (self.input_format, self.output_format, str(e))
            
        self.response.headers['Content-Length'] = len(self.response_string) # disabled for security reasons by GAE, http://code.google.com/appengine/docs/python/tools/webapp/responseclass.html#Disallowed_HTTP_Response_Headers
    
    def headandget(self):
        self.do_pygmentize = False
        self.processRequest()
        
    def head(self):
        self.headandget()
        
    def get(self):
        self.headandget()
        self.response.out.write(self.response_string)
        
    def post(self):
        self.do_pygmentize = True
        self.processRequest()
        self.response.out.write(self.response_string)       


application = webapp.WSGIApplication([
    ('/parse', ParserHandler)],
             debug=True)

def main():
    logging.getLogger().setLevel(logging.INFO)
    util.run_wsgi_app(application)


# not needed in python 2.7 appengine (http://blog.notdot.net/2011/10/Migrating-to-Python-2-7-part-1-Threadsafe)
#if __name__ == '__main__':
#    main()
    
    
    
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
