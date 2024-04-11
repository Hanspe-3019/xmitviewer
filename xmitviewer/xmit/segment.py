'''Module containing code to assemble
    segments in xmit file to segment groups
'''
class Segmentgroup(object):
    '''describes the union of all segments
       within a group of segments
        - file_pos: File position of first segment
        - header: Segment Header of last(!) part
        - segments_bytes: concatenated bytes of all parts without
                          their headers
        - count_segs: count of segment parts
    '''
    def __init__(self, opened_file):
        self.file_pos = opened_file.tell()
        self.header = Segmentheader(opened_file.read(2), self.file_pos)
        self.the_bytes = opened_file.read(self.header.laenge - 2)
        # if more segments in record read on
        self.count_segs = 1
        while not self.header.is_last_seg_in_rec:
            self.header = Segmentheader(opened_file.read(2), opened_file.tell())
            self.the_bytes += opened_file.read(self.header.laenge - 2)
            self.count_segs += 1
    def __repr__(self):
        return 'SegGroup of %3d, %5d bytes, starting at pos +%r' % (
            self.count_segs, len(self.the_bytes), self.file_pos)

class Segmentheader(object):
    '''Beschreibt den Segment Header
       zwei Bytes: +0 FL1 Länge des Segments inkl. Header
                   +1 X   ein paar Flags
    '''
    def __init__(self, segment_header, segment_offset):
        self.laenge = segment_header[0]
        self.offset = segment_offset
        flags = segment_header[1]
        self.is_controlrecord = (flags & (1<<5) > 0)
        self.is_first_seg_in_rec = (flags & (1<<7) > 0)
        self.is_last_seg_in_rec = (flags & (1<<6) > 0)
    def __repr__(self):
        return 'Segment Header (%r, %r)' % (self.offset, self.laenge)
