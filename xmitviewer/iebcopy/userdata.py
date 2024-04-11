''' Extract ISPF statistics of member from
    its Userdata in Directory Entry
'''
import datetime
from collections import namedtuple
import struct

import xmitviewer.utils.dumper as dumper

ISPFUSERDATA = struct.Struct('>3Bx 4s 4s 2s 2h 2x 7s')
Userdata = namedtuple(
    'Userdata',
    'ver mod flags crea last last_time lines lines_initial userid')
Stats = namedtuple(
    'Stats',
    'vermod  crea last last_time lines lines_initial userid')
def extract_stats(userdata, is_alias):    # pylint: disable=unused-argument

    '''returns named tuple of ispf member statistics
    '''
    def julian_to_strdate(julian):
        ''' 4 bytes packed P'0cyydddF'
            to ISO-dateString
        '''

        yyyyddd = str(julian[0] + 19) + julian.hex()[2:-1]
        the_date = datetime.datetime.strptime(yyyyddd, '%Y%j').date()
        return the_date.strftime('%Y-%m-%d')

    if len(userdata) != 30: # std ISPF Statistics
        return UserdataUnknown(
            userdata,
            error_text='len={:}'.format(len(userdata))
        )

    udata = Userdata(*ISPFUSERDATA.unpack(userdata[:ISPFUSERDATA.size]))
    vermod = "{:02d}.{:02d}".format(udata.ver, udata.mod)
    crea = julian_to_strdate(udata.crea)
    last = julian_to_strdate(udata.last)
    last_time = "{:02d}:{:02d}".format(udata.last_time[0], udata.last_time[1])
    userid = udata.userid.decode('cp273')
    return UserdataStats(Stats(
        vermod, crea, last, last_time,
        udata.lines, udata.lines_initial, userid))

class UserdataStats(object):
    '''ISPF statistics
    '''
    def __init__(self, stats):
        self.stats = stats
    def __repr__(self):
        return "{:s} {:5d} {:s}".format(
            self.stats.last,
            self.stats.lines,
            self.stats.userid)

def extract_unknown(userdata):
    '''Returns Diagnosis Object when unsupported format encountered
    '''
    return UserdataUnknown(userdata)
class UserdataUnknown(object):
    '''Userdata which could not be properly interpreted.
        __repr__() will dump the data
    '''
    def __init__(self, data, error_text=''):
        self.data = data
        self.error_text = error_text
    def __repr__(self):
        dump_it = dumper.Dumper(codepage='cp037')
        return '\n'.join((
            '*unknown* ' + self.error_text,
            '\n'.join(s for s in dump_it(self.data)),
            '\n'
        ))
