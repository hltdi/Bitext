"""
Basic Python tools to process files in TMX format.
"""

import sys
from xml.sax import make_parser
from xml.sax.handler import feature_namespaces, ContentHandler
from xml.sax.saxutils import unescape

def read_tmx(filename):
    '''Read in a TMX file; return it in the form of a dict.
    '''
    parser = make_parser()
    # Tell the parser we are not interested in XML namespaces
    parser.setFeature(feature_namespaces, 0)
    # Create the handler
    dh = ReadTMX()
    # Tell the parser to use our handler
    parser.setContentHandler(dh)
    # Parse the input
    parser.parse(filename)
    # Return the whole thing; be careful not to let it print out!
    return dh.lexicon

def write_ques_lexicon(lex, filename):
    lex_list = list(lex.items())
    lex_list.sort(key=lambda x: x[0])
    with open(filename, 'w', encoding='utf8') as outfile:
        for lex in lex_list:
            # First element is Qu, POS pair
            qu, pos = lex[0]
            # Spanish gloss is in the dict
            es = lex[1]['es']
            print(qu + '|' + pos + '|' + es, file=outfile)

def make_esqu_dict(lex):
    es_dict = {}
    for (qu, pos), dct in lex.items():
        es = dct['es']
        es_split = es.split(';')
        for es_gloss in es_split:
            es_gloss = es_gloss.strip()
            if es_gloss in es_dict:
                es_dict[es_gloss].add(qu)
            else:
                es_dict[es_gloss] = {qu}
    return es_dict

def write_esqu_lexicon(lex, filename, make_dict=False):
    if make_dict:
        lex = make_esqu_dict(lex)
    lex_list = list(lex.items())
    lex_list.sort(key=lambda x: x[0])
    with open(filename, 'w', encoding='utf8') as outfile:
        for lex in lex_list:
            es = lex[0]
            qu = '; '.join(lex[1])
            print(es + '|' + qu, file=outfile)

class ReadTMX(ContentHandler):
    '''ContentHandler for reading the whole lexicon in from a file, storing as a dict.'''

    def __init__(self):
        '''Constructor for ReadTMX.'''
        # Initialize the list of TUs
        self.TUs = []
        # To keep track of the current TU
        self.tu = None
        # Within a TUV
        self.in_tuv = False

    def startDocument(self):
        '''What happens when the parser starts reading the document.'''
        pass

    def endDocument(self):
        '''What happens when the parser reaches the end of the document.'''
        # Store the last entry
        self.record_tu()

    def startElement(self, name, attrs):
        '''What happens when the parser finds the start of an element.'''
        if name == 'tu':
            print('Beginning TU')
            # Beginning of new entry; reinitialize the entry dict
            self.entry = {}
        elif name == 'prop':
            print(" In prop")
            pass
        elif name == 'tuv':
            print(' In TUV')
            lg = attrs.get('xml:lang')
            print("  In languuage {}".format(lg))
        elif name == 'seg':
            print(' In seg')
        elif name == 'quote':
#            print('In quote')
            self.in_quote = True
#        else:
#            print('Name:', name)
            
    def endElement(self, name):
        '''What happens when the parser reaches the end of an element.'''
        if name == 'entry':
            # End of entry; add it to dict
#            print('Done with entry')
            self.record_entry()
        elif name == 'gramGrp':
            pass
        elif name == 'pos':
#            print('Out of POS')
            self.in_pos = False
        elif name == 'cit':
#            print('Out of cit')
            self.in_qu_gloss_a = False
            self.in_qu_gloss_b = False
            self.in_es_gloss = False
        elif name == 'quote':
#            print('Out of quote')
            self.in_quote = False

    def characters(self, ch):
        '''What happens when the parser finds text between tags.'''
        if self.in_quote and not ch[:2] == '..':
            if self.in_qu_gloss_a:
                # Gloss for current entry
                self.entry['qu_a'] = self.entry.get('qu_a', '') + ch
            elif self.in_qu_gloss_b:
                self.entry['qu_b'] = self.entry.get('qu_b', '') + ch
            elif self.in_es_gloss:
                self.entry['es'] = self.entry.get('es', '') + ch
        elif self.in_pos:
            self.entry['pos'] = self.entry.get('pos', '') + ch

    def record_tu(self):
        self.TUs.append(self.tu)

### Testing 
##def test(filename):
##    parser = make_parser()
##    # Tell the parser we are not interested in XML namespaces
##    parser.setFeature(feature_namespaces, 0)
##    # Create the handler
##    dh = Test()
##    # Tell the parser to use our handler
##    parser.setContentHandler(dh)
##    # Parse the input
##    parser.parse(filename)
##    # Return the whole thing; be careful not to let it print out!
##
##class Test(ContentHandler):
##
##    def __init__(self):
##        self.chars = False
##
##    def startElement(self, name, attrs):
##        '''What happens when the parser finds the start of an element.'''
##        if name == 'entry':
##            pass
##        elif name == 'qu':
##            self.chars = True
##        elif name == 'es':
##            self.chars = True
##            
##    def endElement(self, name):
##        '''What happens when the parser reaches the end of an element.'''
##        if name == 'entry':
##            pass
##        elif name == 'qu':
##            self.chars = False
##            print()
##        elif name == 'es':
##            self.chars = False
##            print()
##
##    def characters(self, ch):
##        '''What happens when the parser finds text between tags.'''
##        if self.chars:
##            print(ch, end='')
##
