'''Module declares super class of IEBCOPYs unload records '''

import xmitviewer.utils.dumper as dumper
import xmitviewer.utils.address as address

class Unloadrecord(object):
    '''Describes a single Unload Record
    subclassed by specific record types
    '''
    def __init__(self, the_bytes, dsn):
        self.dataset = dsn
        self.reclen = len(the_bytes)
        self.rec16 = the_bytes[:16]
        self.rectype = type(self).__name__[3:] # ohne Rec-prefix

        self.address = address.build_address(the_bytes[:12])\
                if len(the_bytes) >= 12 else None

    def __repr__(self):
        hexdump = dumper.Dumper(codepage='cp273')
        return "%8s %5d %s" % (
            self.rectype,
            self.reclen,
            '  '.join([s for s in hexdump(self.rec16)]))
    def show(self):
        '''todo:
        check if superflous
        '''
        return self.__repr__()
