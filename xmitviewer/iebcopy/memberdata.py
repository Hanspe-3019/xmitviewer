'''Module for Memberdata: Code to extract member's data records
'''
import struct

import xmitviewer.utils.datatype as datatype
import xmitviewer.utils.errors as errors

class Memberdata(object):
    '''Describes the data of an member.

        - .member : corresponding directory entry object.
        - .the_bytes: the bytes of member data: The concatenation of
            of blocks according to RECFM of PDS.
        - .dcb : needed for unblocking of the bytes in get_as_records()
        - .datatype: short string guessing the the file type, e.g.
            ascii, ebcdic, zip, pdf, xmit
    '''
    def __init__(self, member, dcb, the_bytes):
        if not the_bytes:
            # Aus ISPF-Edit können leere Member entstehen!
            raise errors.NodataError
        self.member = member
        self.the_bytes = the_bytes

        self.dcb = dcb
        if dcb['recfm'] == 'U':
            self.datatype = 'lmod'
        else:
            first_bytes = b''.join(
                [r for i, r in enumerate(self.get_as_records(codepage=None))
                    if i < 5])
            self.datatype = datatype.get_type(first_bytes)

    def __repr__(self):
        return "%r %r %i Bytes" % (self.member.name,
                                   self.datatype,
                                   len(self.the_bytes))
    def get_as_records(self, codepage='cp273', linesep=''):
        ''' Unblocks member data into records separated by linesep
            if cp is none, no code page conversion occurs.

            Usage examples:

                print(*m.get_as_records(linesep='\\n'))
                print(*("%05d %s" % (i, r) for
                    i, r in enumerate(m.get_as_records(linesep='\\n'))))

        '''
        recfm = self.dcb['recfm']
        if recfm == 'FB':
            lrecl = self.dcb['lrecl']
            for i in range(0, len(self.the_bytes), lrecl):
                if codepage is None:
                    yield self.the_bytes[i: i + lrecl]
                else:
                    yield self.the_bytes[i: i + lrecl].\
                        decode(codepage) + linesep
        elif recfm == 'VB':
        #   2H Blocklänge
        #   n * Logical Record:
        #       2H Satzlänge incl Daten
        #       xx Daten
            j = 0
            while True: # iterate over the blocks
                (lblock, _) = struct.unpack('>2H', self.the_bytes[j:j+4])
                i = j + 4
                j = j + lblock # j points to begin of next block
                while i < j: # iterate over the logical records in block
                    (lrecl, _) = struct.unpack('>2H', self.the_bytes[i:i+4])
                    if codepage is None:
                        yield self.the_bytes[i + 4: i + lrecl]
                    else:
                        yield self.the_bytes[i + 4: i + lrecl].\
                            decode(codepage) + linesep
                    i = i + lrecl
                if j > len(self.the_bytes) - 4:
                    break

        else:   # recfm=U
            yield self.the_bytes
