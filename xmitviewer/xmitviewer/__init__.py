'''This package only imports the main class Xmitfile
'''
from .xmit.file import Xmitfile
from .ttkgui.guiapp import Ttkgui
from .utils.errors import NodataError

print('''Usage from python shell:
        pds = xmitviewer.Xmitfile(<path>).get_pds()
        pds.export_all()''')
