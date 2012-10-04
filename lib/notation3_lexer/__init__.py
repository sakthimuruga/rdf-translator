# -*- coding: utf-8 -*-
from pygments.lexer import bygroups
from pygments.lexer import include
from pygments.lexer import RegexLexer
from pygments.token import Comment
from pygments.token import Keyword
from pygments.token import Literal
from pygments.token import Name
from pygments.token import Operator
from pygments.token import Text

__all__ = ['Notation3Lexer']

class Notation3Lexer(RegexLexer):
    """
    Lexer for the N3 / Turtle / NT language

    :copyright: 2007 by Philip Cooper <philip.cooper@openvest.com>.
    :license: BSD, see LICENSE for more details.
    """
    name = 'N3'
    aliases = ['n3', 'turtle']
    filenames = ['*.n3', '*.ttl', '*.NT']
    mimetypes = ['text/rdf+n3','application/x-turtle','application/n3']

    tokens = {
        'comments': [
            (r'(\s*#.*)', Comment)
        ],
        'root': [
            include('comments'),
            (r'(\s*@(?:prefix|base|keywords)\s*)(\w*:\s+)?(<[^> ]*>\s*\.\s*)',bygroups(Keyword,Name.Variable,Name.Namespace)),
            (r'\s*(<[^>]*\>)', Name.Class, ('triple','predObj')),
            (r'(\s*[a-zA-Z_:][a-zA-Z0-9\-_:]*\s)', Name.Class, ('triple','predObj')),
            (r'\s*\[\]\s*', Name.Class, ('triple','predObj')),
        ],
        'triple' : [
            (r'\s*\.\s*', Text, '#pop')
        ],
        'predObj': [
            include('comments'),
            (r'(\s*[a-zA-Z_:][a-zA-Z0-9\-_:]*\b\s*)', Operator, 'object'),
            (r'\s*(<[^>]*\>)', Operator, 'object'),
            (r'\s*\]\s*', Text, '#pop'),
            (r'(?=\s*\.\s*)', Keyword, '#pop'), 
        ],
        'objList': [
            include('comments'),
            (r'\s*\)', Text, '#pop'),
            include('object')
        ],
        'object': [
            include('comments'),
            (r'\s*\[', Text, 'predObj'),
            (r'\s*<[^> ]*>', Name.Attribute),
            (r'\s*("""(?:.|\n)*?""")(\@[a-z]{2-4}|\^\^<?[a-zA-Z0-9\-\:_#/\.]*>?)?\s*', bygroups(Literal.String,Text)),
            (r'\s*".*?[^\\]"(?:\@[a-z]{2-4}|\^\^<?[a-zA-Z0-9\-\:_#/\.]*>?)?\s*', Literal.String),
            (r'\s*[a-zA-Z0-9\-_\:]\s*', Name.Attribute),
            (r'\s*\(', Text, 'objList'),
            (r'\s*;\s*\n?', Text, '#pop'),
            (r'(?=\s*\])', Text, '#pop'),            
            (r'(?=\s*\.)', Text, '#pop'),           
        ],
    }

