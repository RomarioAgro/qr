import win32print as wp
import win32api
# from PyQT4 import QTCore, QTGui

# print(wp.EnumPrinters(Flags=PRINTER_ENUM_LOCAL, Name=None, Level=1))
# list_print = wp.EnumPrinters(2)
# print(list_print)
# 'Honeywell PC42t plus (203 dpi)'
# local_printer = wp.OpenPrinter(list_print[3], None)
local_printer = wp.GetDefaultPrinterW()
# print(local_printer)
lp_handler = wp.OpenPrinter(local_printer)
print(lp_handler)
local_job = wp.EnumJobs(lp_handler, 1, 4)
print(local_job)
# new_printer = wp.SetDefaultPrinter('Honeywell PC42t plus (203 dpi)')
# print(new_printer)
# filename = 'd:\\python_work\\venv\\qr\\201760115211966201760115211966.pdf'
# rez = win32api.ShellExecute(0, "print", filename, None, ".", 0)
# local_job = wp.EnumJobs(lp_handler, 1, 1, 2)
# print(local_job)
# print(rez)
# wp.SetDefaultPrinter(local_printer)

