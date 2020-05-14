'''Module contains code to guess type of data. It declares suspectible
characters to determine the code page and looks for eye catchers
of standard file formats.
'''
import string as _string
_PRINTABLE = set(' ').union(
    _string.punctuation,
    _string.ascii_letters,
    _string.digits)
_SUSPECTS = {chr(i) for i in range(256)}.difference(_PRINTABLE)

def check_codepage(the_bytes, codepage=None):
    '''Gives number from 0 to 100 indicating the percentage of
        non-printable/unusual characters according to a given encoding.
        Small numbers indicate a text file,
        large numbers indicate a non-text file.
    '''
    test_string = the_bytes.decode(codepage, errors='replace')
    return len(
        [s for s in test_string if s in _SUSPECTS]
        ) * 100 // len(the_bytes)

def get_type(the_bytes):
    '''
    Does some heuristic tests to guess the type of a bytes given.

    'ebcdic' - Textfile EBCDIC
    'ascii' - Textfile ASCII
    ...
    '''
    resp = 'bin'
    if check_codepage(the_bytes, codepage='cp273') < 2:
        resp = 'ebcdic'
    elif check_codepage(the_bytes, codepage='latin-1') < 2:
        resp = 'ascii'
    elif the_bytes[2:8] == 'INMR01'.encode('cp273'):
        resp = 'xmit'
    elif the_bytes.find(b'%PDF') >= 0:
        resp = 'pdf'
    elif the_bytes[0:2] == 'PK'.encode('latin-1'):
        resp = 'zip'
    elif the_bytes[1:5] == 'ESD '.encode('cp273'):
        resp = 'obj'
    return resp
