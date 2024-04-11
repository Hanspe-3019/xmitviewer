'''Module assembles the parts of a pds from the unload dataset
as attributes of the Iebcopyds class
'''
import xmitviewer.utils.errors as errors
import xmitviewer.utils.address as address
from xmitviewer.iebcopy.memberdata import Memberdata
from xmitviewer.iebcopy.recs import gen_unload_recs as unl
import xmitviewer.utils.errors as errors

class Iebcopyds(object):
    '''Class built from Xmit-IEBCOPY Dataset

        - .dsn : the dataset seen from xmit file
        - .datarecords: the records which constitute the pds unload dataset
        - .members: the members extracted from directory block records
        - .addr_to_data, .addr_to_mbr and .mbrname_to_mbr: some lookup dicts.

        To access the data of some member, use get_memberdata('mbrname'),
            which returns a Memberdata object.
        To extract member data to file use
            - save_member_as_binary('mbrname') or
            - save_member_as_textfile('mbrname')
    '''
    def __init__(self, dsn):

        self.dsn = dsn
        self.datarecords = [dbr for dbr in unl(self)]
        self.members = []
        cr2 = self.datarecords[1]
        for dbr in (dbr for dbr in unl(self) if dbr.rectype == 'Dirblock'):
            self.members.extend(dbr.get_members(cr2))
        self.addr_to_mbr = {}
        self.mbrname_to_mbr = {}
        for mbr in self.members:
            self.addr_to_mbr[mbr.mbbcchhr] = mbr
            self.mbrname_to_mbr[mbr.name] = mbr
        self.addr_to_data = {} # von ADDR zur ersten Position in unl()
        for i, data in enumerate(unl(self)):
            if data.rectype == 'Mbrdata':
                j = self.addr_to_data.get(data.mbbcchhr, i)
                self.addr_to_data[data.mbbcchhr] = j

    def __repr__(self):
        return "IEBCOPY %r \n %d Member" % (self.dsn, len(self.members))

    def save_member_as_textfile(self, mbrname, outdir='.', codepage='cp273'):
        '''Writes member data to file 'mbrname'.txt to 'outdir'
            as text file.

            That is, the logical records extracted from the
            member data records are converted from code page
            to string and written as separate lines.
        '''
        textpath = outdir + '/' + mbrname.rstrip() + '.txt'
        with open(textpath, 'w') as textfile:
            textfile.writelines(self.get_memberdata(mbrname).
                                get_as_records(codepage=codepage, linesep='\n'))
    def save_member_as_binary(self, mbrname, outdir='.'):
        '''Writes member data to file 'mbrname'.bin' to 'outdir' as binary file.

            That is, the logical reocrds extracted from the
            member data records are written concatenated as bytes.
        '''
        binpath = outdir + '/' + mbrname.rstrip() + '.bin'
        with open(binpath, 'wb') as binfile:
            binfile.writelines(self.get_memberdata(mbrname).
                               get_as_records(codepage=None, linesep=''))

    def export_all(self):
        '''Export all members into current directory
        '''
        for member in self.members:
            try:
                memberdata = member.get_memberdata(self)
            except  errors.NodataError:
                continue
            (ext, codepage, mode, linesep) =\
                ('txt', 'cp273', 'w', '\n')\
                if memberdata.datatype == 'ebcdic' else\
                (memberdata.datatype, None, 'wb', '')

            save_path = "{:}.{:}".format(
                member.name.strip(),
                ext)

            with open(save_path, mode) as save:
               save.writelines(
                   memberdata.get_as_records(
                       codepage=codepage,
                       linesep=linesep)
               )

    def overview(self):
        '''returns dictionary of recordtypes
            only for analysis, no real purpose
        '''
        from xmitviewer.utils.pdsoverview import get_overview
        for (k, the_val) in sorted(get_overview(self).items()):
            print("%8s : %s" % (k.upper(), the_val))


    def get_memberdata(self, mbrname):
        '''Collect member data from the data records and returns
            a Memberdata object.

            Uses lookup from membername to directory entry
            and lookup from addr in directory entry to indexr
            of first data record.
            Now scans the data records forward until end of member data:
             - data record not 'mbrdata' (e.g. 'eof')
             - data record has addr equal addr of another member's
               first data record
        '''
        mbrname8 = mbrname.ljust(8) # always fill up to 8 Characters
        mbr = self.mbrname_to_mbr.get(mbrname8, False)
        if not mbr:
            raise KeyError('Member ' + mbrname + ' not found')
        addr = mbr.mbbcchhr
        start = self.addr_to_data.get(addr, -1)
        if start < 0: # empty member
            raise errors.NodataError
        stop = start
        while True:
            stop = stop + 1
            rec = self.datarecords[stop]
            if rec.rectype != 'Mbrdata':
                break
            check_member = self.addr_to_mbr.get(rec.mbbcchhr, False)
            if check_member and check_member.name != mbrname8:
                break

#       Insbesondere Bei PDS-Lademodulbibliotheken kann ein Unloadrecord
#       mehrere DASD-Blöcke des PDS enthalten:
#          dr.reclen > dr.address.dd
        memberdata = []
        for dr in self.datarecords[start: stop]:
            i = 0
            while i < dr.reclen - 12:
                addr = address.build_address(dr.the_bytes[i: i+12])
                i = i + 12
                memberdata.append(dr.the_bytes[i:addr.dd+i])
                i = i + addr.dd
        return Memberdata(
            mbr,
            self.dsn.dcb,
            b''.join(memberdata)
            )
