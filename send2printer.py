import win32print
import win32api
from os.path import isfile
import glob
import time
import win32con

# Имя принтера

printer_name = 'Honeywell PC42t plus (203 dpi)'
# Получаем объект принтера
printer_handle = win32print.OpenPrinter(printer_name)

# Получаем текущие настройки принтера
default_printer_properties = win32print.GetPrinter(printer_handle, 2)

# Устанавливаем размер страницы
default_printer_properties['pDevMode'].PaperWidth = 500  # Ширина страницы 60 мм
default_printer_properties['pDevMode'].PaperLength = 500  # Высота страницы 40 мм

# Устанавливаем ориентацию страницы (1 - портретная, 2 - ландшафтная)
default_printer_properties['pDevMode'].Orientation = 1

# Применяем настройки принтера
win32print.SetPrinter(printer_handle, 2, default_printer_properties, 0)

# Закрываем объект принтера
win32print.ClosePrinter(printer_handle)

