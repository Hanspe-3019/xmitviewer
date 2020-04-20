'''Contains only one class, it parses the text units in a xmit controlrecord.
'''
import xmitviewer.xmit.textunit as textunit
class Controlrecord(object):
    '''Control Record:
       see doc in TSO Customisation
       type = 'INMRxx'
       tu_list: List of text units
    '''
    def __init__(self, segment):
        self.type = segment.the_bytes[0:6].decode('cp273')
        segment_len = len(segment.the_bytes)
        pos = 10 if self.type[-1] == '2' else 6 # hier beginnen die TUs
        self.tu_list = []
        while pos < segment_len:
            tunit = textunit.Textunit(segment.the_bytes[pos:])
            self.tu_list.append(tunit)
            pos += tunit.bytes
    def __repr__(self):
        return "\n%r : %r " % (self.type, self.tu_list)
