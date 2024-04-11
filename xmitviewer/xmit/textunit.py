'''Module contains code to parse textunits and translate them to python objects
'''
def recfm_as_string(two_bytes):
    '''
    The record format of the file.
The value is the result of "logically ORing" one or more of
the following values together:
 - X'0001' Shortened VBS format used for transmission records
 - X'xx02' Varying length records without the 4-byte header
 - X'0200' Data includes machine code printer control characters
 - X'0400' Data contains ASA printer control characters
 - X'0800' Standard fixed records or spanned variable records
 - X'1000' Blocked records
 - X'2000' Track overflow or variable ASCII records
 - X'4000' Variable-length records
 - X'8000'Fixed-length records
 - X'C000'Undefined records
    '''
    (first_byte, second_byte) = two_bytes   #pylint: disable=unused-variable
    fix = first_byte & (1<<7) > 0
    var = first_byte & (1<<6) > 0
    f_or_v_or_u = 'U' if fix and var else 'F' if fix else 'V'
    blocked = 'B' if first_byte & (1<<4) > 0 else ''
    a_or_m = 'A' if first_byte & (1<<2) > 0 else 'M' if first_byte & (1<<1) > 0 else ''
    spanned = 'S' if first_byte & (1<<3) else ''
    return f_or_v_or_u + blocked + a_or_m + spanned

def build_dict_from_string(the_string):
    '''Little helper to build pythonic dictionary from documentation
    '''
    the_dict = {}
    for line in the_string.strip().splitlines():
        (its_key, its_value) = line.split()
        the_dict[bytes(bytearray.fromhex(its_key))] = its_value
    return the_dict

def dsorg(datalen, tunit):  # pylint: disable=unused-argument
    'get DSORG'
    return Textunit.dsorg_mapping[tunit[:2]]
def recfm(datalen, tunit):  # pylint: disable=unused-argument
    'get RECFM'
    return recfm_as_string(tunit[:2])
def binlen(datalen, tunit):
    'get integer from binary length'
    return int.from_bytes(tunit[:datalen], byteorder='big')
def lsize(datalen, tunit):  # pylint: disable=unused-argument
    'dummy'
    return 'size MB'
def ebcdic(datalen, tunit):
    'get string from ebcdic data in text unit'
    return tunit[:datalen].decode('cp273')
def unknown(datalen, tunit):  # pylint: disable=unused-argument
    'not implemented'
    return 'unknown'

class Textunit(object):
    '''Control Records contain text unit tuples:
     - 2 Byte TU key: The key identifies the type of information
       contained in the text unit. Possible key values are given
       in Types of text units.
     - Halfword: The number field contains the number of
       length-data pairs that follow. Most of the text units have
       only one length and one data field.
     - Halfword: The first of perhaps many length fields.
       The length value includes only the length of the data field
       immediately following it, and not its own two-byte length.
     - The Data: The first of perhaps many data fields.
       The data field contains the parameter information being passed,
       for example, the target node name.
    '''
    textunit_descriptions = '''    0030 INMBLKSZ    Block size
    1022    INMCREAT    Creation date
    0001    INMDDNAM    DDNAME for the file
    000C    INMDIR      Number of directory blocks
    0002    INMDSNAM    Name of the file
    003C    INMDSORG    File organization
    8028    INMEATTR    Extended attribute status
    1027    INMERRCD    RECEIVE command error code
    0022    INMEXPDT    Expiration date
    1026    INMFACK     Originator requested notification
    102D    INMFFM      Filemode number
    1011    INMFNODE    Origin node name or node number
    1024    INMFTIME    Origin timestamp
    1012    INMFUID     Origin user ID
    1023    INMFVERS    Origin version number of the data format
    1021    INMLCHG     Date last changed
    0042    INMLRECL    Logical record length
    1020    INMLREF     Date last referenced
    8018    INMLSIZE    Data set size in megabytes.
    0003    INMMEMBR    Member name list
    102F    INMNUMF     Number of files transmitted
    102A    INMRECCT    Transmitted record count
    0049    INMRECFM    Record format
    000B    INMSECND    Secondary space quantity
    102C    INMSIZE     File size in bytes
    0028    INMTERM     Data transmitted as a message
    1001    INMTNODE    Target node name or node number
    1025    INMTTIME    Destination timestamp
    1002    INMTUID     Target user ID
    8012    INMTYPE     Data set type
    1029    INMUSERP    User parameter string
    1028    INMUTILN    Name of utility program
'''
    dsorg_mapping = build_dict_from_string('''
        0008 VS
        0200 PO
        4000 PS
''')
    textunit_dict = {}
    for line in textunit_descriptions.splitlines():
        (tu_key, tu_name, tu_description) = line.split(maxsplit=2)
        tu_key = bytes(bytearray.fromhex(tu_key))
        textunit_dict[tu_key] = tu_name[3:]
    field_dict = {
        'DSORG': dsorg,
        'RECFM': recfm,
        'LRECL': binlen,
        'BLKSZ': binlen,
        'LSIZE': binlen,
        'SIZE':  binlen,
        'NUMF': binlen,
        'DIR': binlen,
        'DSNAM': ebcdic,
        'UTILN': ebcdic,
        'FNODE': ebcdic,
        'FUID': ebcdic,
        'TNODE': ebcdic,
        'TUID': ebcdic,
        'FTIME': ebcdic
    }
    def __init__(self, tu_bytes):
        '''Describes one text unit
            - 2 bytes key
            - field is fieldname as string
            - data is array of values
        '''
        self.key = tu_bytes[0:2]
        count_tu = int.from_bytes(tu_bytes[2:4], byteorder='big')
        self.data = []
        self.field = Textunit.textunit_dict[self.key]
        field_formatter = Textunit.field_dict.get(self.field, unknown)
        pos = 4
        for i in range(count_tu): #pylint: disable=unused-variable
            data_len = int.from_bytes(tu_bytes[pos: pos+2], byteorder='big')
            self.data.append(field_formatter(data_len, tu_bytes[pos+2:]))
            pos += (2 + data_len)
        self.bytes = pos
    def __repr__(self):
        return "\n     %r - %r" % (self.field, self.data)
