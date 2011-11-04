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
import simplejson as json

import logging

known_vocabs = {
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
    "s": "http://schema.org/"
}

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

def getPrefixDict(url):
    global known_vocabs
    # add if not in dict of known vocabularies
    if not url in known_vocabs.values():
        #logging.info(url)
        params = {"uri": url, "format": "json"}
        result = urlfetch.fetch(url="http://prefix.cc/reverse?%s" % urllib.urlencode(params))
        if result.status_code == 200:
            #logging.info(result.content)
            return json.loads(result.content).items()
    return []

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
    global known_vocabs
    
    final_format = None
    if output_format == "rdfa" or output_format == "microdata":
        final_format = output_format
        output_format = "pretty-xml"
    
    g = rdflib.Graph()

    if not output_format == "trix": # trix should not display all these namespace definitions
        for key, value in dict.items(known_vocabs):
            g.bind(key, value)
    
    if file_format == "string":
        g.parse(data=f, format=input_format)
    else:
        g.parse(f, format=input_format)
    
    if len(g) > 0:
        serialization = g.serialize(format=output_format).decode("UTF-8")
        
        if output_format == "n3" or output_format == "pretty-xml" or output_format == "xml":
            d = {}
            # for n3, try to resolve missing prefixes with prefix.cc
            if output_format == "n3":
                from StringIO import StringIO
                n3_file = StringIO(serialization)
                for line in n3_file.readlines():
                    if line.lower().find("@prefix") >= 0:
                        lt = line.find("<")
                        gt = line.find(">")
                        if 0 < lt < gt:
                            url = line[(lt+1):gt].strip()
                            d = dict(d.items() + getPrefixDict(url))
                                    
            # for pretty-xml the same
            elif output_format == "pretty-xml" or output_format == "xml":
                import re
                for m in re.finditer(r"xmlns:[a-zA-Z0-9]+=\"?([^\"]*)", serialization):
                    #logging.info(m.group(1))
                    url = m.group(1)
                    d = dict(d.items() + getPrefixDict(url))
            
            # do only if not already in dict of known vocabularies
            if len(d) > 0:
                g = rdflib.Graph()
            
                for key, value in dict(known_vocabs.items() + d.items()).items():
                    g.bind(key, value)
            
                if file_format == "string":
                    g.parse(data=f, format=input_format)
                else:
                    g.parse(f, format=input_format)
                            
                serialization = g.serialize(format=output_format).decode("UTF-8")           
        
        # final format is rdfa or microdata, made detour over rdf/xml
        if final_format:
            rdf = g.serialize(format=output_format).decode("UTF-8")
            serialization = createSnippet(rdf, final_format).decode("UTF-8")
        
        if do_pygmentize:
            return pygmentize(serialization, output_format)
        else:
            return serialization
    else:
        return ""