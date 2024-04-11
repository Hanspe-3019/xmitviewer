'''Describes the first two Controlrecords of IEBCOPY-Unload Data Set
'''
import struct

from xmitviewer.iebcopy.unloadrec import Unloadrecord

class RecCr1(Unloadrecord):
    '''first Controlrecord of IEBCOPY-Unload Data Set

    R1INDC   DS    X             INDICATOR, X'00'=OK, X'80'=ERROR
    R1ID     DS    XL3           IEBCOPY IDENTIFIER = X'CA6D0F'
    R1DSORG  DS    XL2           DSORG
    R1BLKSI  DS    XL2           BLKSIZE
    R1LRECL  DS    XL2           LRECL
    R1RECFM  DS    X             RECFM
    R1KEYLEN DS    X             KEYLEN
    R1OPTCD  DS    X             OPTCD
             DS    X             *** RESERVED ***
    R1TBLKSI DS    XL2           BLKSIZE OF TAPE FILE
    R1DEVTYP DS    XL20          DEVICE TYPE INFORMATION
    R1TRKCYL EQU   R1DEVTYP+10,2,C'H'
    '''
    def __init__(self, datarecord, dsn):
        the_bytes = datarecord.the_bytes
        Unloadrecord.__init__(self, the_bytes, dsn)
        if not the_bytes[1:4] == bytearray.fromhex('CA6D0F'):
            raise TypeError
        self.data = dict(zip('DSORG BLKSIZE LRECL RECFM TBLK TRKCYL'.split(),
                             struct.unpack('>4x3hB3xH10xh', the_bytes[:28])))
    def __repr__(self):
        return Unloadrecord.__repr__(self) + "\nCR1 %r" % (self.data)

class RecCr2(Unloadrecord):
    '''CopyR2: Second Header Record with the DEB Extensions
        needed for conversion between relative TTR and MBBCCHHR
    '''
    def __init__(self, datarecord, dsn, tracks_in_cylinder):
        cr2 = datarecord.the_bytes
        Unloadrecord.__init__(self, cr2, dsn)
        cnt_debx = cr2[0]
        self.trkcyl = tracks_in_cylinder
        self.debxes = [
            Debx(cr2[i:i+16]) for i in range(16, 16*cnt_debx + 1, 16)]

    def __repr__(self):
        return Unloadrecord.__repr__(self) + "\nCR2 %r" % (self.debxes)

    def convert_ttr(self, rel_trk, recnum):
        '''converts relative track address (trknum + recnum)
        to absolute dasd address MBBCCHHR
        '''
        abs_m = 0
        the_debx = None
        for debx in self.debxes:
            if rel_trk < debx.data['NMTRK']:
                the_debx = debx
                break
            rel_trk -= debx.data['NMTRK']
            abs_m += 1
        else:
            raise TypeError
        (abs_cc, abs_hh) = divmod(rel_trk, self.trkcyl)
        abs_cc += the_debx.data['CC0']
        abs_hh += the_debx.data['HH0']
        (cc_overflow, abs_hh) = divmod(abs_hh, self.trkcyl)
        abs_cc += cc_overflow
        abs_bb = the_debx.data['BB']
        return struct.pack(
            '>BHHHB',
            abs_m,
            abs_bb,
            abs_cc,
            abs_hh,
            recnum)

class Debx(object):
    '''
    DEBXTENT DSECT ,             FORMAT OF DEB EXTENT
    DEBDVMOD DS    X             FILE MASK
    DEBUCBA  DS    AL3           UCB ADDRESS
    DEBINUM  DS    H             BIN NUMBER
    DEBSTRCC DS    H             CYLINDER ADDRESS FOR START OF EXTENT
    DEBSTRHH DS    H             TRACK ADDRESS FOR START OF EXTENT
    DEBENDCC DS    H             CYLINDER ADDRESS FOR END OF EXTENT
    DEBENDHH DS    H             TRACK ADDRESS FOR END OF EXTENT
    DEBNMTRK DS    H             NO. OF TRACKS ALLOCATED TO THIS EXTENT
    '''
    def __init__(self, the_bytes):
        self.data = dict(zip('BB CC0 HH0 CC1 HH1 NMTRK'.split(),
                             struct.unpack('>4x6H', the_bytes[:16])))
    def __repr__(self):
        return 'DEB Extent : {}'.format(self.data)
