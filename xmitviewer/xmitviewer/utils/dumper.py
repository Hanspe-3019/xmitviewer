'''Small helper to output bytes in dump format
'''
import string
TO_POINT = {ord(c): '.' for c in set(
    [chr(i) for i in range(256)]).difference(
        set(' ').union(
            string.punctuation,
            string.ascii_letters,
            string.digits)
    )
           }

class Dumper:
    '''Contains the print dump function
    Instance of Dumper is callable: a generator of print lines
    Example:
    print_dump = dumper.Dumper(rowbytes=32)
    for s in print_dump(b'abcdefghijklmnopqrstuvwxyz'): print(s)
    '''
    def __init__(self, codepage='latin-1', rowbytes=16):
        self.codepage = codepage
        self.rowbytes = rowbytes
    def dump_them(self, the_bytes):
        '''Generator of print lines in classical dump format
        '''

        def split8(to_split):
            '''Split hexadecimal string into parts of 8 hexadecimal numbers
            '''
            i = 0
            while to_split[i:i+8]:
                yield to_split[i:i+8]
                i += 8
        hexa_cols = (self.rowbytes + 3) // 4
        len_hexa_part = 8 * hexa_cols + hexa_cols - 1
        the_rows = (the_bytes[i: i + self.rowbytes]
                    for i in range(0, len(the_bytes), self.rowbytes))
        for row in the_rows:
            hexa_part = ' '.join(split8(row.hex().upper()))
            display_part = row.decode(self.codepage).translate(TO_POINT)
            yield hexa_part.ljust(len_hexa_part) + '  ' + display_part
        return

    __call__ = dump_them

VALID_MEMBER_CHARS = ' '.join([
    string.ascii_uppercase,
    string.digits,
    '#$@'])
VALID_MEMBER_BYTES = set(VALID_MEMBER_CHARS.encode('cp037'))
def check_cp037(the_bytes):
    '''Checks for MVS characters
    if True returns string represention, else
    returns hexa decimal
    '''
    if not set(the_bytes).issubset(VALID_MEMBER_BYTES):
        return the_bytes.hex().upper()
    return the_bytes.decode('cp037')
def to_point(the_bytes, code_page='cp037'):
    '''Masks nonprintable chars with '.'
    '''
    return the_bytes.decode(code_page).translate(TO_POINT)
