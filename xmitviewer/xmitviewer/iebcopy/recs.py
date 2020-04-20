'''Describes the records within the iebcopy unload file
   and its record types

   class RecDirblock(Unloadrecord)
   class RecMbrdata(Unloadrecord)
   class Rec_…(Unloadrecord)

   Function gen_unload_rec():
        generator for sequence of Unloadrecords
'''

from xmitviewer.iebcopy.unloadrec import Unloadrecord
import xmitviewer.utils.address as address
import xmitviewer.iebcopy.directory as directory
import xmitviewer.iebcopy.recscntl as cntl

def gen_unload_recs(pds):
    '''Scans the records in iebcopy unload data set and
       returns list of record objects
    '''
    dsn = pds.dsn
    recs = dsn.datarecords
    cr1 = cntl.RecCr1(recs[0], dsn)
    yield cr1
    yield cntl.RecCr2(recs[1], dsn, cr1.data['TRKCYL'])
    for rec in recs[2:]:
        the_bytes = rec.the_bytes
        rec_address = address.build_address(the_bytes[:12])\
            if len(the_bytes) >= 12 else None
        if len(the_bytes) < 12:
            recordtype = RecUnknown
        elif rec_address.k == 8:   # keylen
            recordtype = RecDirblock
        elif len(the_bytes) == 12:
            recordtype = RecEof
        elif rec_address.flag == 0:
            recordtype = RecMbrdata
        elif rec_address.flag in (0x04, 0x08):
            recordtype = RecAttrib
        else:
            recordtype = RecUnknown

        yield recordtype(the_bytes, dsn)

class RecDirblock(Unloadrecord):
    '''Record contains directory blocks of fixed length 276

        directory block data (containing the directory entries) is
        256 bytes fixed. The data is prefixed with 20 bytes:
         - Addr 8 Bytes, here always x'00'
         - keylen, with PDS dir block always 8
         - dalenlen, with PDS dir block always 256
         - the key, with PDS name of last member in directory block.
    '''
    def __init__(self, the_bytes, dsn):
        Unloadrecord.__init__(self, the_bytes, dsn)
        self.the_bytes = the_bytes

    def get_members(self, cr2):
        '''return the members in this Directory Block
        '''
        members = []
        #
        # Hinten wird der Block aufgefüllt, so iterate in chunks of 276
        # to get the directory block records
        #
        for i in range(0, len(self.the_bytes), 276):
            dbr = directory.Directoryblock(self.the_bytes[i:], cr2)
            members.extend(dbr.members)
            if dbr.last:
                break
        return members

class RecMbrdata(Unloadrecord):
    '''Record contains data of a particular member.
    Each member owns zero to many member data records.
    The assignment of a member data records happens by correlating its
    DASD address with the relative track address of the directory entry.
    '''
    def __init__(self, the_bytes, dsn):
        Unloadrecord.__init__(self, the_bytes, dsn)
        self.the_bytes = the_bytes
        self.mbbcchhr = the_bytes[1:9]

class RecAttrib(Unloadrecord):
    '''The unload data set from PDSEs contains attribute records.
    These are not documented by IBM and are ignored here.
    '''
    def __init__(self, the_bytes, dsn):
        Unloadrecord.__init__(self, the_bytes, dsn)

class RecEof(Unloadrecord):
    '''EOF records separate the logical parts of an unload data set.
    '''
    def __init__(self, the_bytes, dsn):
        Unloadrecord.__init__(self, the_bytes, dsn)

class RecUnknown(Unloadrecord):
    '''I hope record types I don't know, are not important
    to this package.
    '''
    def __init__(self, the_bytes, dsn):
        Unloadrecord.__init__(self, the_bytes, dsn)
        self.the_bytes = the_bytes
