import win32print
import win32api

printer_name = 'Honeywell PC42t plus (203 dpi)'  # имя вашего принтера
file_path = "d:\\files\\86694.pdf"  # путь к вашему PDF файлу

# Открытие принтера
printer_handle = win32print.OpenPrinter(printer_name)

# Создание задания на печать
job_id = win32print.StartDocPrinter(printer_handle, 1, (file_path, None, "RAW"))

# Отправка на печать
with open(file_path, 'rb') as f:
    file_content = f.read()
print(file_content)  # выводим содержимое файла для отладки

win32print.StartPagePrinter(printer_handle)
print("Страница начата на печать")  # отладочный вывод
win32print.WritePrinter(printer_handle, file_content)
print("Содержимое файла отправлено на печать")  # отладочный вывод
win32print.EndPagePrinter(printer_handle)
print("Страница завершена")  # отладочный вывод
# Завершение задания и закрытие принтера
win32print.EndDocPrinter(printer_handle)
win32print.ClosePrinter(printer_handle)
