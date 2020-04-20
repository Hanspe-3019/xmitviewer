'''This package only imports the main class Xmitfile
'''
from .xmit.file import Xmitfile
from .ttkgui.guiapp import Ttkgui
from .utils.errors import NodataError
print('''Example Problem mit MacOS 10.14.6 Crash Windowserver :
    xmitviewer.Ttkgui().mainloop()''')
print('''Usage from python shell:
        pds = xmitviewer.Xmitfile(<path>).get_pds()
        pds.export_all()''')


