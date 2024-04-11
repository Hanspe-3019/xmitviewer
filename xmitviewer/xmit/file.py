'''This module contains the starting object: Xmitfile
'''
import xmitviewer.utils.errors as errors
import xmitviewer.xmit.controlrecord as cntl
import xmitviewer.xmit.dataset as dataset
import xmitviewer.xmit.segment as segm
import xmitviewer.iebcopy.iebcopyds as ieb

class Xmitfile(object):
    '''A XMIT file contains segments of length 2 to 256.

       Each segment starts with a two byte segment header, which describes
       its length, its type and whether it is complete or is a part of
       a multi-segment structure, which I call segment group.
       A record is built from one or multiple consecutive segments.
       There are two kinds of records:
        - Control records
        - Data records
       Data records are split by control record 3 into data sets: A XMIT file
       contains one or multiple data sets.

       Attributes:
       - .path - path of Xmitfile
       - .controlrecords - List of the control records
       - .datasets - list of its datasets (INMR02 records), usually two.
       - .get_pds() - method, giving the pds object.

       See Documentation in TSO Customization
    '''
    def __init__(self, path):
        def next_segment():
            '''little helper to iterate over the segments
            '''
            while True:
                if xmit_file.tell() < file_size:
                    yield segm.Segmentgroup(xmit_file)
                else:
                    return

        self.path = path
        self.controlrecords = []
        self.datasets = []
        self._layout = []

        with open(path, 'rb') as xmit_file:
            xmit_start = xmit_file.read(8)
            if xmit_start[1:] != bytes.fromhex('e0 c9d5 d4d9 f0f1'):
                raise errors.XmitfileError('INMR01 Record missing')

            file_size = xmit_file.seek(0, 2) # EOF
            xmit_file.seek(0) # wieder nach vorne gehen
            count_datarecords = 0
            sum_datalen = 0
            (cur_dataset, first_in_group) = (None, True)
            for seg in next_segment():
                if seg.header.is_controlrecord:
                    if count_datarecords > 0:
                        self._layout.append(" DataRecords %r - %r bytes"
                                            % (count_datarecords, sum_datalen))
                        count_datarecords = 0
                    crec = cntl.Controlrecord(seg)
                    self.controlrecords.append(crec)
                    self._layout.append(" %s  %s%s" % (
                        crec.type,
                        '<' if seg.header.is_first_seg_in_rec else '.',
                        '>' if seg.header.is_last_seg_in_rec else '.',
                        ))
                    if  crec.type == 'INMR02':
                        dsn = dataset.Dataset(crec.tu_list)
                        self.datasets.append(dsn)
                        if first_in_group:
                            first_in_group = False
                            cur_dataset = dsn

                else:
                    sum_datalen += len(seg.the_bytes)
                    count_datarecords += 1
                    cur_dataset.add_datarecord(seg)

    def __repr__(self):
        '''Simple print of XMIT file's layout
        '''
        return self.path + '\n' + '\n'.join(self._layout)
    def get_pds(self):
        '''returns PDS file object found in XMIT file_size
           raises TypeError if not found
        '''
        if self.datasets[0].utiln != 'IEBCOPY':
            raise errors.XmitfileError('No PDS found in XMIT File')
        return ieb.Iebcopyds(self.datasets[0])
    def get_inmr01(self):
        '''Short info from INMR01:
        FROMNODE.FROMUID FTIME (as yyyy-mm-dd)
        '''
        inmr01 = self.controlrecords[0]
        textunits = dict(
            (textunit.field, textunit.data[0]) for textunit in inmr01.tu_list
            if len(textunit.data) == 1)
        its_date = list(textunits.get('FTIME', 'yyyymmdd')[:8])
        its_date.insert(6, '-')
        its_date.insert(4, '-')
        return 'INMR01: {}.{} - {}'.format(
            textunits.get('FNODE', '<FNODE>'),
            textunits.get('FUID', '<FUID>'),
            ''.join(its_date))
