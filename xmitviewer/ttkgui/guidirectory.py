
'''Frame for display of PDS directory
'''
import tkinter as tk
import tkinter.ttk as ttk

from xmitviewer.utils.errors import NodataError

#
# Keys for dictionary of widgets and stringvars
#
MHEAD = 'mhead'
MEMBERS = 'members'
BUTTON0 = 'but_0'
BUTTON1 = 'but_1'
SCROLLBAR = 'scrollbar'

class DirectoryFrame(ttk.Frame):    # pylint: disable=too-many-ancestors
    '''
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
    !  but-0     !  but-1  but-2  but-3          !
    +--------------------------------------------+
    '''
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        self.grid(
            sticky=tk.W+tk.N,
            padx=20,
            pady=20)

        self.widgets = {}
        self.stringvars = {}

        self.pds = None

        self.widgets[MHEAD] = ttk.Label(
            self,
            text='Directory'
        )
        self.widgets[SCROLLBAR] = ttk.Scrollbar(
            self,
            orient=tk.VERTICAL
        )
        self.widgets[MEMBERS] = tk.Listbox(
            self,
            yscrollcommand=self.widgets[SCROLLBAR].set,
            height=22,
            width=10
        )

        self.widgets[MHEAD].grid(row=0, column=0)
        self.widgets[MEMBERS].grid(
            row=1,
            column=0,
            pady=10,
            sticky=tk.N+tk.S+tk.W+tk.E
        )
        self.widgets[SCROLLBAR].grid(
            row=1,
            column=1,
            pady=10,
            sticky=tk.N+tk.S
        )
        self.widgets[SCROLLBAR]['command'] = self.widgets[MEMBERS].yview

        self.widgets[BUTTON0] = ttk.Button(
            self,
            text="Show Dir",
            command=self.show_directory,
            state=tk.DISABLED,
            width=10
        )
        self.widgets[BUTTON0].grid(row=2, column=0)

        self.widgets[BUTTON1] = ttk.Button(
            self,
            text="Exp. all",
            command=self.export_all,
            state=tk.DISABLED,
            width=10
        )
        self.widgets[BUTTON1].grid(row=3, column=0)

    def show(self, pds):
        '''Start showing content of pds:
         - fill selection box with the member names in directory
         - initialize data display with list display.
        '''
        self.pds = pds
        self.fill_selbox()
        self.widgets[BUTTON0].configure(state=tk.NORMAL)
        self.widgets[BUTTON1].configure(state=tk.NORMAL)
        self.show_directory()

    def show_member(self, event):   # pylint: disable=unused-argument
        '''Show member's data.
        If EBCDIC type translate to unicode and display as text
        otherwise display in dump format.
        '''
        i = self.widgets[MEMBERS].curselection()[0]
        member = self.pds.members[i]
        self.master.show_member_data(member)

    def show_directory(self):
        '''Display the directory in member data area.
        '''
        self.master.show_directory()

    def fill_selbox(self):
        '''Populate the selection box with pds member names
        '''
        if self.widgets[MEMBERS].size() > 0:
            self.widgets[MEMBERS].delete(0, self.widgets[MEMBERS].size())
        names = (m.name_display for m in self.pds.members)
        self.widgets[MEMBERS].insert(tk.END, *names)
        self.widgets[MEMBERS].bind('<<ListboxSelect>>', self.show_member)
    def export_all(self):
        '''Export all members into directory
        '''
        directory = tk.filedialog.askdirectory(initialdir='.')
        if not directory:
            return
        directory += '/'    ######### Windows?
        for member in self.pds.members:
            try:
                memberdata = member.get_memberdata(self.pds)
            except  NodataError:
                continue
            (ext, codepage, mode, linesep) =\
                ('txt', 'cp273', 'w', '\n')\
                if memberdata.datatype == 'ebcdic' else\
                (memberdata.datatype, None, 'wb', '')

            save_path = "{:}{:}.{:}".format(
                directory,
                member.name.strip(),
                ext)

            with open(save_path, mode) as save:
               save.writelines(
                   memberdata.get_as_records(
                       codepage=codepage,
                       linesep=linesep)
               )
