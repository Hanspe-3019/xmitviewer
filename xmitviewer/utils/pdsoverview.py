'''Small helper to give some statistics from pds records
'''
from xmitviewer.iebcopy.recs import gen_unload_recs as unl
def get_overview(pds):
    '''returns dictionary of recordtypes with statistics
        only for analysis, no real purpose
    '''
    class OverviewData(object):
        '''Data class to provide template rectypes statistics
        '''
        def __init__(self):
            self.cntrec = 0
            self.sumlen = 0
            self.max = 0
            self.min = 0
            self.locs = list()
        def __repr__(self):
            reclen = ''
            if self.cntrec > 1:
                if self.min != self.max:
                    reclen = ', MinAvgMax=[%5d - %6.1f - %5d]' % (
                        self.min,
                        self.sumlen/self.cntrec,
                        self.max)
                else:
                    reclen = ', reclen=%d' % (self.min,)
            return '%5d - %9d bytes%s' % (
                self.cntrec,
                self.sumlen,
                reclen)
    rectypes = {}
    for i, rec in enumerate(unl(pds)):
        data = rectypes.setdefault(rec.rectype, OverviewData())
        data.cntrec += 1
        data.sumlen += rec.reclen
        if data.max < rec.reclen:
            data.max = rec.reclen
        if (data.min == 0) | (data.min > rec.reclen):
            data.min = rec.reclen
        data.locs.append(i)
        rectypes[rec.rectype] = data
    return rectypes
