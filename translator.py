#!/usr/bin/env python
import sys
sys.path.append("lib")

import rdflib
import rdflib_microdata
from rdflib.parser import Parser
from rdflib.serializer import Serializer

rdflib.plugin.register("rdf-json", Parser, "rdfextras.parsers.rdfjson", "RdfJsonParser")
rdflib.plugin.register("rdf-json", Serializer, "rdfextras.serializers.rdfjson", "RdfJsonSerializer")
rdflib.plugin.register("rdf-json-pretty", Serializer, "rdfextras.serializers.rdfjson", "PrettyRdfJsonSerializer")

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import guess_lexer, get_lexer_for_mimetype

def pygmentize(text):
    lexer = guess_lexer(text)
    return highlight(text, lexer, HtmlFormatter())

def parse(f, file_format="file", input_format="rdfa", output_format="pretty-xml"):
	#"""
	g = rdflib.Graph()
	
	if file_format == "string":
		g.parse(data=f, format=input_format)
	else:
		g.parse(f, format=input_format)
	
	if len(g) > 0:
		return pygmentize(g.serialize(format=output_format))
	else:
		return ""
	#"""