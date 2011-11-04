#!/usr/bin/env python
# encoding: utf-8
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
from pygments.lexers import guess_lexer, get_lexer_for_mimetype, sw, XmlLexer, JavascriptLexer

from google.appengine.api import urlfetch

import urllib
import httplib

def createSnippet(inputrdf, format="rdfa"):
    # test connection
    HOST1 = False
    result = urlfetch.fetch(url="http://rhizomik.net:80/")
    if result.status_code == 200:
        HOST1 = True
    
    # prepare form fields and headers
    form_fields = {
        "rdf": inputrdf,
        "mode": "snippet"
    }
    form_data = urllib.urlencode(form_fields)
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/plain"
    }
    
    response = None
    if HOST1:
        response = urlfetch.fetch(url="http://rhizomik.net:80/redefer-services/rdf2%s" % format,
            payload=form_data,
            method=urlfetch.POST,
            headers=headers)
    else:
        response = urlfetch.fetch(url="http://rhizomik-redefer.appspot.com:80/rdf2%s" % format,
            payload=form_data,
            method=urlfetch.POST,
            headers=headers)
            
    if response and response.status_code == 200:
        return response.content
    return ""


def pygmentize(text, format):
    if format == "n3" or format == "nt":
        lexer = sw.Notation3Lexer()
    elif format == "pretty-xml" or format == "xml" or format == "trix":
        lexer = XmlLexer()
    elif format == "rdf-json" or format == "rdf-json-pretty":
        lexer = JavascriptLexer()
    else:
        lexer = guess_lexer(text)
    return highlight(text, lexer, HtmlFormatter())

def parse(f, do_pygmentize=False, file_format="file", input_format="rdfa", output_format="pretty-xml"):
    
    final_format = None
    if output_format == "rdfa" or output_format == "microdata":
        final_format = output_format
        output_format = "pretty-xml"
    
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
        serialization = g.serialize(format=output_format).decode("UTF-8")
        if final_format:
            rdf = g.serialize(format=output_format).decode("UTF-8")
            serialization = createSnippet(rdf, final_format)
        
        if do_pygmentize:
            return pygmentize(serialization, output_format)
        else:
            return serialization
    else:
        return ""