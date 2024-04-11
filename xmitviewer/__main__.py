''' is run with python -m xmitviewer
'''
import sys
from pathlib import Path

import xmitviewer
from xmitviewer.utils import errors

def export_all(pds):
    ''' Export all members
    '''
    count = len(pds.members)
    prompt = f'Export all {count} members to current directory {Path.cwd()}/ ? '
    yesno = input(prompt)
    if yesno in "yY":
        pds.export_all()

def open_pds(path):
    ' open path and return pds, sys.exit(1) on failure'
    try:
        pds = xmitviewer.Xmitfile(path).get_pds()
    except (FileNotFoundError, errors.XmitfileError) as e:
        print(e)
        sys.exit(1)
    print(pds)
    return pds

def main():
    ' - '
    if len(sys.argv) == 1:    # no args
        xmitviewer.Ttkgui().mainloop()
    elif sys.argv[1] in ['-x', '--export'] and len(sys.argv) == 3:
        export_all(open_pds(sys.argv[2]))
    else:
        print(HELP)
        sys.exit(1)

HELP = '''
Usage:
    % python -m xmitviewer
        starts GUI

    % python -m xmitviewer --export <path to xmitfile>
       exports all members to current directory
'''

main()
