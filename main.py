#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#	  http://www.apache.org/licenses/LICENSE-2.0
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
from google.appengine.ext.webapp import template

import translator
from rdflib.parser import create_input_source

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

class ParserHandler(webapp.RequestHandler):
	def headandget(self):
		self.page = self.request.get("url")
		self.input_format = self.request.get("if", default_value="")
		self.output_format = self.request.get("of", default_value="pretty-xml")
		
		if self.output_format == "pretty-xml" or self.output_format == "xml":
			self.response.headers['Content-Type'] = "application/rdf+xml"
		elif self.output_format == "n3":
			self.response.headers['Content-Type'] = "text/n3"
		elif self.output_format == "nt":
			self.response.headers['Content-Type'] = "text/plain"
		elif self.output_format == "trix":
			self.response.headers['Content-Type'] = "application/xml"
		else:
			self.response.headers['Content-Type'] = "text/plain"
			
		if not self.input_format:
			source = create_input_source(location=self.page, format=self.input_format)
			self.input_format = source.content_type
		
		try:
			self.response_string = translator.parse(self.page, file_format="file", input_format=self.input_format, output_format=self.output_format)
			if self.response_string.strip() == "" and self.input_format == "text/html": # fix microdata test
				self.response_string = translator.parse(self.page, file_format="file", input_format="microdata", output_format=self.output_format)
			if self.response_string.strip() == "":
				raise Exception
		except Exception, e:
			self.response_string = "<p style='color: red; font-weight: bold; padding-top: 12px'>Could not convert from %s to %s for provided resource...<br><br>Error Message:<br>%s</p>" % (self.input_format, self.output_format, e)
			
		self.response.headers['Content-Length'] = len(self.response_string) # disabled for security reasons by GAE, http://code.google.com/appengine/docs/python/tools/webapp/responseclass.html#Disallowed_HTTP_Response_Headers
		
	def head(self):
		self.headandget()
		
	def get(self):
		self.headandget()
			
		self.response.out.write(self.response_string)
		
	def post(self):
		self.content = self.request.get("content")
		self.input_format = self.request.get("if", default_value="")
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
			source = create_input_source(data=self.content, format=self.input_format)
			self.input_format = source.content_type
		
		try:
			#self.response.out.write(self.content)
			self.response_string = translator.parse(self.content, file_format="string", input_format=self.input_format, output_format=self.output_format)
			if self.response_string.strip() == "" and self.input_format == "text/html": # fix microdata test
				self.response_string = translator.parse(self.content, file_format="string", input_format="microdata", output_format=self.output_format)
			if self.response_string.strip() == "":
				raise Exception
		except Exception, e:
			self.response_string = "<p style='color: red; font-weight: bold; padding-top: 12px'>Could not convert from %s to %s for provided resource...<br><br>Error Message:<br>%s</p>" % (self.input_format, self.output_format, e)
			
		self.response.headers['Content-Length'] = len(self.response_string) # disabled for security reasons by GAE, http://code.google.com/appengine/docs/python/tools/webapp/responseclass.html#Disallowed_HTTP_Response_Headers
		
		self.response.out.write(self.response_string)

		
class MainHandler(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = "text/html"
		template_values = {
			"title": "RDF Translator"
		}
		path = os.path.join(os.path.dirname(__file__), "index.html")
		self.response.out.write(template.render(path, template_values))
		

def main():
	application = webapp.WSGIApplication([
										('/', MainHandler),
										('/parse', ParserHandler)],
										 debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
	
	
	
# hack: quoted os.getpid() in rdflib.plugins.parsers.notation3
