"""
Basic tools to process files in TMX format.
Herramientas básicas para procesar archivos en formato TMX.

TMX 1.4b Specification: https://www.gala-global.org/tmx-14b
Un Guía al TMX: http://www.fti.uab.es/tradumatica/revista/num0/articles/jgomez/art.htm

TMX: translation memory exchange / intercambio de memoria de traducción
TU: translation unit / unidad de traducción
TUV: translation unit variant / variante de unidad de traducción
SEG: segment / segmento

Ejemplo. Crear una lista de TUS.
>>> tus = read_tmx("../EsGn/DGO/tmx/dgo2.tmx")
>>> tus[10]
{'ES-PY': ['Correr los escombros,'], 'GN': ['Emboyke kusugue']}
"""

import sys
from xml.sax import make_parser
from xml.sax.handler import feature_namespaces, ContentHandler
from xml.sax.saxutils import unescape

def read_tmx(filename):
    '''Read in a TMX file; return it in the form of a dict.'''
    parser = make_parser()
    # Tell the parser we are not interested in XML namespaces
    parser.setFeature(feature_namespaces, 0)
    # Create the handler
    tmx = ReadTMX()
    # Tell the parser to use our handler
    parser.setContentHandler(tmx)
    # Parse the input
    parser.parse(filename)
    # Return the whole thing; be careful not to let it print out!
    return tmx.TUs

class ReadTMX(ContentHandler):
    '''ContentHandler for reading the whole lexicon in from a file, storing as a dict.'''

    def __init__(self, verbosity=0):
        '''Constructor for ReadTMX.'''
        # Initialize the list of TUs
        self.TUs = []
        # Current TU, TUV, segment, and language
        self.tu = None
        self.tuv = None
        self.seg = None
        self.lg = ''
        # Within a TUV
        self.in_tuv = False
        # Within a segment
        self.in_seg = False
        self.verbosity = verbosity

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
            if self.verbosity:
                print('Beginning TU')
            # Beginning of new TU; initialize
            self.tu = {}
        elif name == 'prop':
#            print(" Beginning prop, ignoring")
            pass
        elif name == 'tuv':
            if self.verbosity:
                print(' Beginning TUV')
            lg = attrs.get('xml:lang')
            if self.verbosity:
                print("  In language {}".format(lg))
            self.in_tuv = True
            self.tuv = []
            self.lg = lg
        elif name == 'seg':
            if self.verbosity:
                print(' Beginning seg')
            self.in_seg = True
            self.seg = ''
        else:
            if self.verbosity:
                print('Start name??:', name)
            
    def endElement(self, name):
        '''What happens when the parser reaches the end of an element.'''
        if name == 'tu':
            if self.verbosity:
                print("Ending TU")
            self.record_tu()
        elif name == 'prop':
#            print(" Ending prop, ignoring")
            pass
        elif name == 'tuv':
            if self.verbosity:
                print(' Ending TUV')
                print('  {}'.format(self.tuv))
            self.in_tuv = False
            self.record_tuv()
        elif name == 'seg':
            if self.verbosity:
                print(' Ending seg')
                print("  {}".format(self.seg))
            self.in_seg = False
            self.record_seg()
        else:
            if self.verbosity:
                print('End name??:', name)

    def characters(self, ch):
        '''What happens when the parser finds text between tags.'''
        ch = ch.strip()
        if ch:
            if self.in_seg:
                self.seg += ch
                
    def record_tu(self):
        """Record the current TU in the list of TUs."""
        self.TUs.append(self.tu)

    def record_tuv(self):
        """Record the current TUV in the current TU."""
        self.tu[self.lg] = self.tuv

    def record_seg(self):
        """Record the current segments in the current TUV."""
        self.tuv.append(self.seg)
