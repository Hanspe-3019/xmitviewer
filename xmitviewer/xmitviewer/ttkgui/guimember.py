
'''Erste Tests mit tkinter
'''
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog
import tkinter.scrolledtext
import re

import xmitviewer.utils.dumper as dumper
import xmitviewer.utils.errors as errors

MAX_DUMPLINES = 22

CODEPAGES = {
    'ascii': 'latin-1',
    'ebcdic-de': 'cp273',
    'ebcdic-us': 'cp037'
}
STRING = re.compile(
    r'[a-zA-Z0-9!"§$%&/()=?*+\'#;:_,.<> -]{9,64}'
)
#
# Keys for dictionary of widgets and stringvars
#
MINFO = 'minfo'
MHEAD = 'mhead'
MDATA = 'mdata'
MEMBERS = 'members'
BUTTON0 = 'but_0'
BUTTON1 = 'but_1'
SELCODEPAGE = 'selcp'
DUMP_MODE = 'Show in Hex'
TEXT_MODE = 'Show as Text'

class MemberFrame(ttk.Frame):    # pylint: disable=too-many-ancestors
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
        ttk.Frame.__init__(self, master, borderwidth=3, relief=tk.GROOVE)
        self.grid(
            sticky='WENS',
            pady=20,
            ipadx=20,
            ipady=20)

        self.widgets = {}
        self.stringvars = {}

        self.pds = None
        self.mdata = None
        self.display_as_text = True

        self.stringvars[MINFO] = tk.StringVar()
        self.widgets[MINFO] = ttk.Label(
            self,
            textvariable=self.stringvars[MINFO]
        )


        self.widgets[MDATA] = tkinter.scrolledtext.ScrolledText(
            self,
            bg='white',
            padx=5,
            wrap=tk.NONE,
            height=24,
            width=80
        )

        self.widgets[MINFO].grid(row=0, column=0)
        self.widgets[MDATA].grid(
            row=1, column=0, rowspan=3, padx=10, pady=10)

        self.stringvars[SELCODEPAGE] = tk.StringVar()
        self.stringvars[SELCODEPAGE].set('ascii')
        self.current_codepage = CODEPAGES['ascii']
        self.widgets[SELCODEPAGE] = ttk.Combobox(
            self,
            values=' '.join(CODEPAGES.keys()),
            width=10,
            textvariable=self.stringvars[SELCODEPAGE],
            exportselection=0
        )
        self.widgets[SELCODEPAGE].active_state = 'readonly'
        self.widgets[SELCODEPAGE].grid(
            row=1,
            column=1,
            sticky=tk.N+tk.W,
            padx=10,
            pady=10
        )
        self.widgets[SELCODEPAGE].bind(
            '<<ComboboxSelected>>',
            self.apply_new_codepage
        )

        self.widgets[SELCODEPAGE].configure(state=tk.DISABLED)
        self.stringvars[BUTTON0] = tk.StringVar()
        self.stringvars[BUTTON0].set(TEXT_MODE)
        self.widgets[BUTTON0] = ttk.Button(
            self,
            textvariable=self.stringvars[BUTTON0],
            command=self.switch_dump_text,
            width=14
        )
        self.widgets[BUTTON1] = ttk.Button(
            self,
            text="Export Member",
            command=self.save_to_file,
            state=tk.DISABLED,
            width=14
        )
        self.widgets[BUTTON0].grid(row=2, column=1, sticky=tk.N)
        self.widgets[BUTTON0].grid_remove()
        self.widgets[BUTTON1].grid(row=3, column=1)
        self.widgets[BUTTON1].grid_remove()

    def show_member_data(self, member, event=True):
        '''Show member's data.
        If EBCDIC type translate to unicode and display as text
        otherwise display in dump format.
        '''
        self.widgets[SELCODEPAGE].grid()
        self.widgets[BUTTON0].grid()
        self.widgets[BUTTON1].grid()
        self.widgets[BUTTON1].configure(state=tk.NORMAL)
        self.widgets[MDATA].delete('1.0', tk.END)
        try:
            self.mdata = self.pds.get_memberdata(member.name)
        except errors.NodataError:
            self.stringvars[MINFO].set(
                '{} {}'.format(member, '*empty*')
            )
            for i in (SELCODEPAGE, BUTTON1, BUTTON0):
                self.widgets[i].configure(state=tk.DISABLED)
        else:
            self.stringvars[MINFO].set(
                '{} {}'.format(member, self.mdata.datatype)
            )
            if event:
                if self.mdata.datatype in ('ebcdic', ):
                    self.current_codepage = 'cp273'
                    self.widgets[SELCODEPAGE].set('ebcdic-de')
                    self.display_as_text = True
                elif self.mdata.datatype in ('xmit', 'lmod'):
                    self.current_codepage = 'cp037'
                    self.widgets[SELCODEPAGE].set('ebcdic-us')
                    self.display_as_text = False
                else:
                    self.current_codepage = 'latin-1'
                    self.widgets[SELCODEPAGE].set('ascii')
                    self.display_as_text = False
            else:
                pass

            self.widgets[MDATA].insert(
                '1.0',
                get_lines_to_display(
                    self.mdata,
                    self.current_codepage,
                    self.display_as_text
                )
            )
            for i in (SELCODEPAGE, BUTTON1, BUTTON0):
                widget = self.widgets[i]
                try:
                    active_state = widget.active_state
                except AttributeError:
                    active_state = tk.NORMAL
                widget.configure(state=active_state)

        new_mode = DUMP_MODE if self.display_as_text else TEXT_MODE
        self.stringvars[BUTTON0].set(new_mode)

    def show_directory(self, pds):
        '''Display the directory in member data area.
        '''
        self.pds = pds
        self.stringvars[MINFO].set(
            '--- {} ---'.format('Member List')
        )
        self.mdata = None
        self.widgets[BUTTON0].grid_remove()
        self.widgets[BUTTON1].grid_remove()
        self.widgets[SELCODEPAGE].configure(state=tk.DISABLED)
        self.widgets[MDATA].delete('1.0', tk.END)
        self.widgets[MDATA].insert(
            '1.0',
            '\n'.join(str(s) for s in pds.members)
        )
    def save_to_file(self):
        '''Save member's data to a file.
        Depending on data type of member data, the records are
        converted and written to the file system.
        '''
        (ext, codepage, mode, linesep) =\
            ('txt', self.current_codepage, 'w', '\n')\
            if self.mdata.datatype == 'ebcdic' else\
            (self.mdata.datatype, None, 'wb', '')

        fname_init = '{}.{}'.format(
            self.mdata.member.name.strip(),  # len() always 8 chars!
            ext
        )
        fname = tkinter.filedialog.asksaveasfilename(initialfile=fname_init)
        if not fname:
            return

        with open(fname, mode) as save:
            save.writelines(
                self.mdata.get_as_records(
                    codepage=codepage,
                    linesep=linesep)
            )

    def switch_dump_text(self):
        '''Switch display of memeber data from text to dump mode and
        vice versa.
        '''
        self.display_as_text = not self.display_as_text
        self.show_member_data(self.mdata.member, event=None)  # no event
    def apply_new_codepage(self, event):    # pylint: disable=unused-argument
        '''Apply new code page for display of shown member data
        '''
        new_codepage = CODEPAGES[self.stringvars[SELCODEPAGE].get()]
        if new_codepage == self.current_codepage:
            return
        self.current_codepage = new_codepage
        self.show_member_data(self.mdata.member, event=None)  # no event

def get_lines_to_display(mdata, codepage, display_as_text):
    '''returns lines of member's data
    EBCDIC data with EBCDIC code page gets displayed as text lines.
    EBCDIC data with ASCII code page gets displayed in dump format.
    Binary data gets displayed in dump format.
    '''
    if (mdata.datatype == 'ebcdic')\
        & (codepage.startswith('cp'))\
        & display_as_text:
        to_display = '\n'.join(mdata.get_as_records(codepage=codepage))
    elif display_as_text:
        to_display = get_strings_in_binary_data(mdata.the_bytes, codepage)
    else:
        to_display = get_dump_display_of_data(mdata.the_bytes, codepage)
    return to_display
def get_strings_in_binary_data(the_bytes, codepage):
    '''filters data into group of displayable characters
    suppressing non printable characters.
    '''
    return '\n'.join(
        '+{:05X} : {:s}'.format(s.start(), s.group())
        for s in STRING.finditer(the_bytes.decode(codepage)))
def get_dump_display_of_data(the_bytes, codepage):
    '''returns lines from dump display of the bytes
    '''
    dump = dumper.Dumper(codepage=codepage)
    to_display = '\n'.join(
        '+{:03X}  {}'.format(i * 16, s)
        for i, s in enumerate(dump(the_bytes)) if i < MAX_DUMPLINES)

    not_shown = len(the_bytes) - MAX_DUMPLINES * 16
    if not_shown > 0:
        to_display += '\n\n\t{} bytes more...'.format(not_shown)
    return to_display
