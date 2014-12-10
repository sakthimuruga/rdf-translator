#!/usr/bin/env python
# encoding: utf-8
"""
bookmarklet_list.py

This module serves to create a matrix of bookmarklets for the RDF Translator HTML page.

Created by Alex Stolz on 2011-12-19.
Copyright (c) 2011 Universität der Bundeswehr München. All rights reserved.
"""

import sys
import os


def create_matrix():
    """Generates the matrix."""
    input_formats = [
        "[detect]",
        "rdfa",
        "microdata",
        "xml",
        "n3",
        "nt",
        #"rdf-json",
        "json-ld",
        ]
        
    output_formats = [
        "rdfa",
        "microdata",
        "pretty-xml",
        "xml",
        "n3",
        "nt",
        #"rdf-json-pretty",
        #"rdf-json",
        "json-ld",
        #"trix",
        ]
        
    service = "http://rdf-translator.appspot.com/convert"
    
    f = open("matrix.html", "w")
    
    matrix = {}
    f.write("<table class=\"shade_box\" style=\"width:100%; text-align:center\" cellpadding=\"3\" cellspacing=\"3\">")
    row = 0
    for i in input_formats:
        if row == 0:
            f.write("<tr><th colspan=\"2\"></th><th colspan=\"%d\">Output</th></tr>" % len(output_formats))
            f.write("<tr>")
            f.write("<td colspan=\"2\"></td>")
            for o in output_formats:
                emphasis_o = ""
                if o in ["pretty-xml", "n3"]:
                    emphasis_o = " style=\"text-decoration: underline\""
                f.write("<td%(emphasis)s>%(name)s</td>" % {"emphasis":emphasis_o, "name":o})
            f.write("</tr>")
            f.write("<tr><th rowspan=\"%d\">Input</th>" % len(input_formats))
        else:
            f.write("<tr>")
        emphasis_i = ""
        if i in ["rdfa", "microdata"]: 
            emphasis_i = " style=\"text-decoration: underline\""
        f.write("<td%(emphasis)s>%(name)s</td>" % {"emphasis":emphasis_i, "name":i})
        for o in output_formats:
            if "detect" in i:
                f.write("""
        <td style="width:70px">
            <a href="javascript:location.href='%(service)s/detect/%(of)s/html/'+encodeURIComponent(location.href);">
                <img src="static/bookmark.png" alt="detect -> %(of)s" title="detect to %(of)s" />
            </a>
        </td>""" %{"service":service, "of":o})
            else:
                f.write("""
        <td style="width:70px">
            <a href="javascript:location.href='%(service)s/%(if)s/%(of)s/html/'+encodeURIComponent(location.href);">
                <img src="static/bookmark.png" alt="%(if)s -> %(of)s" title="%(if)s to %(of)s" />
            </a>
        </td>""" %{"service":service, "if":i, "of":o})
        f.write("</tr>")
        row += 1
    f.write("</table>")
    f.close()

if __name__ == '__main__':
    create_matrix()

