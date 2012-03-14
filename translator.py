# encoding: utf-8
import sys
sys.path.append("lib")
import re

import rdflib
import rdflib_microdata
from rdflib.parser import Parser
from rdflib.serializer import Serializer

rdflib.plugin.register("rdf-json", Parser, "rdfextras.parsers.rdfjson", "RdfJsonParser")
rdflib.plugin.register("rdf-json", Serializer, "rdfextras.serializers.rdfjson", "RdfJsonSerializer")
rdflib.plugin.register("rdf-json-pretty", Serializer, "rdfextras.serializers.rdfjson", "PrettyRdfJsonSerializer")

rdflib.plugin.register("json-ld", Parser, "rdfextras.parsers.jsonld", "JsonLDParser")
rdflib.plugin.register("json-ld", Serializer, "rdfextras.serializers.jsonld", "JsonLDSerializer")

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import guess_lexer, get_lexer_for_mimetype, sw, XmlLexer, JavascriptLexer

from google.appengine.api import urlfetch
import urllib

try:
  import json
except ImportError:
  import simplejson as json

import logging

known_vocabs = {
    "eco": "http://www.ebusiness-unibw.org/ontologies/eclass/5.1.4/#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "dbpedia": "http://dbpedia.org/resource/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
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
    "s": "http://schema.org/",
    "grddl": "http://www.w3.org/2003/g/data-view#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfa": "http://www.w3.org/ns/rdfa#",
    "rif": "http://www.w3.org/2007/rif#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "skosxl": "http://www.w3.org/2008/05/skos-xl#",
    "wdr": "http://www.w3.org/2007/05/powder#",
    "void": "http://rdfs.org/ns/void#",
    "wdsr": "http://www.w3.org/2007/05/powder-s#",
    "xml": "http://www.w3.org/XML/1998/namespace",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "cc": "http://creativecommons.org/ns#",
    "ctag": "http://commontag.org/ns#",
    "ical": "http://www.w3.org/2002/12/cal/icaltzd#",
    "og": "http://ogp.me/ns#",
    "rev": "http://purl.org/stuff/rev#",
    "sioc": "http://rdfs.org/sioc/ns#",
    "v": "http://rdf.data-vocabulary.org/#"
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
    elif format == "rdf-json" or format == "rdf-json-pretty" or format == "json-ld":
        lexer = JavascriptLexer()
    else:
        lexer = guess_lexer(text)
    return highlight(text, lexer, HtmlFormatter())

def parse(f, do_pygmentize=False, file_format="file", input_format="rdfa", output_format="pretty-xml"):
    global known_vocabs
    
    final_format = None
    base = None
    
    if output_format == "rdfa" or output_format == "microdata":
        final_format = output_format
        output_format = "pretty-xml"
        base = "http://rdf-translator.appspot.com/"
    
    g = rdflib.Graph()

    if not output_format == "trix": # trix should not display all these namespace definitions
        for key, value in dict.items(known_vocabs):
            g.bind(key, value)
    
    if file_format == "string":
        g.parse(data=f, format=input_format, publicID=base)
    else:
        g.parse(f, format=input_format, publicID=base)
        # NOTE: has no effect with current RDFLib version, because it shows full URIs for subjects and objects
        #d = dict()
        #for s in g.subjects(None, None):
        #    base = None
        #    split_hash = s.rsplit("#")
        #    split_slash = s.rsplit("/")
        #    if len(split_hash) > 1:
        #        base = split_hash[0]
        #    elif len(split_slash) > 1:
        #        base = split_slash[0]
        #    if base in d:
        #        d[base] += 1
        #    else:
        #        d[base] = 0
                
        #ns_sorted = sorted(d.items(), key=lambda x: x[1], reverse=True)
    
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
                    g.parse(data=f, format=input_format, publicID=base)
                else:
                    # NOTE: has no effect with current RDFLib version
                    #it = iter(xrange(len(ns_sorted)))
                    #for item in ns_sorted:
                    #    g.bind("ns%d"%it.next(), item)
                    g.parse(f, format=input_format, publicID=base)
                            
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