'''My collection of exceptions
'''
class XmitfileError(Exception):
    '''Main exception class for issues with the xmit file
    needs refinement?
    '''
    pass
class NodataError(Exception):
    '''Member contains no data.
    Directory entry exists, but data has been deleted in ISF Edit.
    '''
    pass
