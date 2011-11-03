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
from pygments.lexers import guess_lexer, get_lexer_for_mimetype, sw

def pygmentize(text, format):
    if format == "n3" or format == "nt":
        lexer = sw.Notation3Lexer()
    else:
        lexer = guess_lexer(text)
    return highlight(text, lexer, HtmlFormatter())

def parse(f, file_format="file", input_format="rdfa", output_format="pretty-xml"):
    #"""
    g = rdflib.Graph()
    
    ontology_uris = {
        "eco": "http://www.ebusiness-unibw.org/ontologies/eclass/5.1.4/#",
        "owl": "http://www.w3.org/2002/07/owl#",
        "dbpedia": "http://dbpedia.org/resource/",
        "dc": "http://purl.org/dc/elements/1.1/",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "gr": "http://purl.org/goodrelations/v1#",
        "foaf": "http://xmlns.com/foaf/0.1/",
        "vcard": "http://www.w3.org/2006/vcard/ns#",
        "vso": "http://purl.org/vso/ns#",
        "tio": "http://purl.org/tio/ns#",
        "coo": "http://purl.org/coo/ns#",
        "vvo": "http://purl.org/vvo/ns#",
        "fab": "http://purl.org/fab/ns#",
        "xro": "http://www.stalsoft.com/ontologies/xro/ns#",
        "xhv": "http://www.w3.org/1999/xhtml/vocab#",
        "s": "http://schema.org/"}

    for key, value in dict.items(ontology_uris):
        g.bind(key, value)
    
    if file_format == "string":
        g.parse(data=f, format=input_format)
    else:
        g.parse(f, format=input_format)
    
    if len(g) > 0:
        return pygmentize(g.serialize(format=output_format), output_format)
    else:
        return ""
    #"""