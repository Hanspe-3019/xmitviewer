'''Defines main class for gui front end

Example:
    import xmitviewer
    xmitviewer.Ttkgui().mainloop()
'''
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog
import tkinter.messagebox

import xmitviewer
import xmitviewer.ttkgui.guimember as guimember
import xmitviewer.ttkgui.guidirectory as guidirectory

XMITINFO = 'xmitinfo'
PDSINFO = 'pdsinfo'
CHOOSE = 'choose'

class Ttkgui(ttk.Frame): # pylint: disable=too-many-ancestors
    '''
    +--------------------------------------------+
    !   xmit info frame                          !
    +--------------------------------------------+
    !   pds info frame                           !
    +--------------------------------------------+
    !            !  member info frame            !
    ! pds dir    !                               !
    !            !-------------------------------!
    ! Listbox    !                               !
    !            !  member data frame            !
    !            !                               !
    !            !                               !
    !            !                               !
    !            !                               !
    !            !                               !
    !            !                               !
    !            !                               !
    !            !                               !
    +--------------------------------------------+
    '''
    def __init__(self):
        ttk.Frame.__init__(self)
        self.master.minsize(width=500, height=500)
        self.master.title("Xmit File Viewer")
        self.grid(sticky='WENS')

        self.xmit = None
        self.widgets = {}
        self.xmit_tk = tk.StringVar()
        self.pds_tk = tk.StringVar()
        self.widgets[XMITINFO] = ttk.Label(
            self,
            anchor=tk.NW,
            justify=tk.LEFT,
            textvariable=self.xmit_tk
        )
        self.widgets[PDSINFO] = ttk.Label(
            self,
            anchor=tk.NW,
            justify=tk.LEFT,
            textvariable=self.pds_tk
        )
        self.widgets[CHOOSE] = ttk.Button(
            self,
            text="Choose File",
            command=self.load_file,
            width=10
        )
        self.widgets[CHOOSE].grid(row=0, column=0, rowspan=2)
        self.widgets[XMITINFO].grid(row=0, column=1, sticky=tk.W)
        self.widgets[PDSINFO].grid(row=1, column=1, sticky=tk.W)

        self.directoryarea = guidirectory.DirectoryFrame(self)
        self.memberarea = guimember.MemberFrame(self)
        self.directoryarea.grid(row=3, column=0, sticky=tk.W+tk.N)
        self.memberarea.grid(row=3, column=1, sticky='W')

    def load_file(self):
        '''Load XMIT file
        '''
        self.master.title("Xmit File Viewer")
        fname = tkinter.filedialog.askopenfilename()
        if not fname:
            return
        try:
            self.xmit = xmitviewer.Xmitfile(fname)
            self.master.title(trunc_path(self.xmit.path))
            self.show_pds_info()
            self.show_xmit_info()
            self.directoryarea.show(self.xmit.get_pds())
        except xmitviewer.utils.errors.XmitfileError as err:
            tkinter.messagebox.showerror(
                "Load XMIT File",
                "Failed to read file\n'{}'\n{}".format(fname, err)
            )
        return
    def show_xmit_info(self):
        '''Show some info about XMIT file
        '''
        self.xmit_tk.set(self.xmit.get_inmr01())

    def show_pds_info(self):
        '''Show some general info about pds in XMIT file
        '''
        pds = self.xmit.get_pds()
        dsn = pds.dsn.dsn
        dcb = ','.join(k + '=' + str(v) for k, v in pds.dsn.dcb.items())

        self.pds_tk.set(
            'DSN={},{}'.format(dsn, dcb.upper())
        )
    def show_directory(self):
        '''Delegate to memberarea
        '''
        self.memberarea.show_directory(self.xmit.get_pds())
    def show_member_data(self, member):
        '''Delegate to memberarea
        '''
        self.memberarea.show_member_data(member)

def trunc_path(path):
    '''Truncate display of long path to reasonable size
    '''
    if len(path) < 50:
        return path
    all_parts = path.split('/')
    if len(all_parts) > 6:
        parts = all_parts[:3]
        parts.append('…')
        parts.extend(all_parts[-3:])
        return '/'.join(parts)
    return path
