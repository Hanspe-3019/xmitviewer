'''Module handles DASD address fmbbcchhrkdd in IEBCOPY's
unload records
'''
import collections
import struct
ADDRESS = '>BBHIBBH'
Address = collections.namedtuple(
    'Address',
    'flag, m, bb, cchh, r, k, dd')
def build_address(twelve_bytes):
    '''extracts the parts of DASD address into its parts as namedtuple
    '''
    return Address(*struct.unpack(ADDRESS, twelve_bytes))
