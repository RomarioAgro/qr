import win32print
import win32api
from os.path import isfile
import glob
import time

source_path = "d:\\python_work\\venv\\qr\\temp\\"
# source_path = ""

def sendtoprinter():
    old_printer = win32print.GetDefaultPrinter()
    new_printer = win32print.SetDefaultPrinter('Honeywell PC42t plus (203 dpi)')
    file_queue = [f for f in glob.glob("%s\\*.pdf" % source_path) if isfile(f)]
    if len(file_queue) > 0:
        for i in file_queue:
            print_file(i, new_printer)
            print(i)
    time.sleep(5)
    win32print.SetDefaultPrinter(old_printer)

def print_file(pfile, printer):
    win32api.ShellExecute(
        0,
        "print",
        '%s' % pfile,
        '/d:"%s"' % printer,
        ".",
        0
        )



sendtoprinter()