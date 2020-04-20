'''Describes some stuff around directories in PO File

The directory of a PDS occupies the beginning of the area allocated to
the data set on a direct access volume. It is searched and maintained by
the BLDL, FIND, and STOW macros. The directory consists of member entries
arranged in ascending order according to the binary value of
the member name or alias.

PDS member entries vary in length and are blocked into 256-byte blocks.
Each block contains as many complete entries as will fit in a maximum
of 254 bytes. Any remaining bytes are left unused and are ignored.
Each directory block contains a 2-byte count field that specifies the
number of active bytes in a block (including the count field).
Each block is preceded by a hardware-defined key field containing
the name of the last member entry in the block, that is, the member name
with the highest binary value.
Each member entry contains a member name or an alias. Each entry also
contains the relative track address of the member and a count field.
It can also contain a user data field.
The last entry in the last used directory block has a name field of
maximum binary value (all 1s), a TTR field of zeros,
and a zero-length user data field.
'''
import struct
import collections
import xmitviewer.iebcopy.userdata as userdata
import xmitviewer.iebcopy.lmoddata as lmoddata
import xmitviewer.utils.dumper as dumper

TTRC = '>HBB'
Ttrc = collections.namedtuple(
    'Ttrc',
    'tt r c')
class Member: # pylint: disable=too-many-instance-attributes
    '''describes single Directory Member Entry:
        - Member Name
        - Addr (TT R)
        - Length of Userdata: Last 5 bits in C field in Half Words!
        - Userdata
        - Length of Entry
    '''
    def __init__(self, the_bytes, cr2):
        self.ttrc = Ttrc(*struct.unpack(TTRC, the_bytes[8:12]))
        self.name = dumper.check_cp037(the_bytes[:8])
        self.name_display = dumper.to_point(the_bytes[:8])
        self.name_is_hidden = len(self.name) > 8
        userlen = 2 * (self.ttrc.c&0b11111)
        self.entrylen = 12 + userlen
        self.alias = self.ttrc.c >> 7 == 1
        get_userdata = userdata.extract_stats if userlen in (30, 40)\
                else lmoddata.extract_lmod if userlen > 0\
                else lambda x, **kw: None
        self.userdata = get_userdata(
            the_bytes[12: self.entrylen],
            is_alias=self.alias
        )
        self.mbbcchhr = cr2.convert_ttr(
            self.ttrc.tt,
            self.ttrc.r)
    def __repr__(self):
        name_hex = ' (x\'{:s}\')'.format(self.name) if self.name_is_hidden\
            else ''
        return "%08s: %04X%02X %s %s" % (
            self.name_display,
            self.ttrc.tt,
            self.ttrc.r,
            str(self.userdata),
            name_hex
        )
    def get_memberdata(self, pds):
        '''Collect member data from pds data records and returns
            a Memberdata object.
        '''
        return pds.get_memberdata(self.name)

class Directoryblock:
    '''Describes one Directory Block
        gets built from a loop over a directory block record
        - 'members' contains the member entries in this block
        - 'highkey' name of last member in directory block.
        - 'blocklen' length of directory block
        - 'the_bytes' for diagnosing the data
    '''
    dirblock_len = 276
    def __init__(self, the_bytes, cr2):
        (keylen, datalen) = struct.unpack(">8x2h", the_bytes[:12])
        if not keylen == 8:
            raise TypeError
        if not datalen == 256:
            raise TypeError
        self.the_bytes = the_bytes
        if the_bytes[12:20] == b'\xff'*8:
            self.highkey = False
            self.last = True
        else:
            self.highkey = the_bytes[12:20].decode('cp273')
            self.last = False
        self.blocklen = struct.unpack('>H', the_bytes[20:22])[0]
        self.members = []
        pos = 0x16
        while pos < self.blocklen:
            member = Member(the_bytes[pos:], cr2)
            self.members.append(member)
            pos += member.entrylen


    def __repr__(self):
        return "Directory Block, highkey = %r" % (self.highkey)
