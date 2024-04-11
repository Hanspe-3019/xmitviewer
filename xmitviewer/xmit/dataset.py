'''Only one class: Dataset, see doc there
'''
class Dataset(object):
    '''This class describes a MVS data set contained inside xmit file
    data from text units in control record INMR02
     - .dsn - Dataset Name of xmitted file
     - .utiln - Name of Utility used (e.g. IEBCOY)
     - .dcb - some DCB attributes
     - .datarecords - list of datarecords, initially empty
    '''
    def __init__(self, tu_list):
        '''extract relevant TUs from data control record
        '''
        tunits = {}
        for tunit in tu_list:
            data = tunit.data[0] if len(tunit.data) == 1 else '.'.join(tunit.data)
            tunits[tunit.field] = data
        self.dsn = tunits.get('DSNAM', '?')
        self.utiln = tunits.get('UTILN', '?')
        self.dcb = {}
        self.dcb['recfm'] = tunits.get('RECFM', '?')
        self.dcb['lrecl'] = tunits.get('LRECL', 0)
        self.dcb['dsorg'] = tunits.get('DSORG', '?')
        self.dcb['blksz'] = tunits.get('BLKSZ', 0)
        self.datarecords = []

    def __repr__(self):
        return 'Data Set %r mit %r, DCB %r' % (self.dsn, self.utiln, self.dcb)

    def add_datarecord(self, datarecord):
        '''Used by Class Xmitfile during scan of xmit file
        '''
        self.datarecords.append(datarecord)

    def dump_datarecords(self, index_list):
        '''Dump of selected datarecords
            Example: Dump records from index 2 to 4:
                dump_datarecords(range(2:5))
        '''
        for i in index_list:
            self.datarecords[i].dump()
