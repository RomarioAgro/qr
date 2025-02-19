import win32print
import win32api
import logging
import ctypes
import time
import PyPDF2
import os


logger_km: logging.Logger = logging.getLogger('pdf_create_KM')
logger_km.setLevel(logging.DEBUG)
logger_km.debug('start send to printer')

def print_pdf_in_chunks(pdf_path, chunk_size=10):
    # Читаем исходный PDF
    with open(pdf_path, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        total_pages = len(pdf_reader.pages)
        print(f"Всего страниц в PDF: {total_pages}")

        # Разбиваем на части и отправляем на печать
        for start_page in range(0, total_pages, chunk_size):
            end_page = min(start_page + chunk_size, total_pages)
            temp_pdf_path = f"temp_chunk_{start_page + 1}_to_{end_page}.pdf"

            # Создаём новый PDF с частью страниц
            pdf_writer = PyPDF2.PdfWriter()
            for page_num in range(start_page, end_page):
                pdf_writer.add_page(pdf_reader.pages[page_num])

            with open(temp_pdf_path, "wb") as temp_pdf:
                pdf_writer.write(temp_pdf)
            try:
                sendtoprinter(i_file=temp_pdf_path)
                print(f"Печатаем страницы с {start_page + 1} по {end_page}")
            except Exception as e:
                print(f"Ошибка при печати: {e}")
            finally:
                # Удаляем временный файл
                os.remove(temp_pdf_path)
                time.sleep(10)


def sendtoprinter(i_file: str = '', printer_name: str = 'Honeywell PC42t plus (203 dpi)'):
    """
    функция отправки на печать pdf файлов из папки
    :return:
    """
    # printer_name = 'Honeywell PC42t plus (203 dpi)'
    old_printer = win32print.GetDefaultPrinter()
    new_printer = win32print.SetDefaultPrinter(printer_name)
    logging.debug(f'установили новый принтер по умолчанию {new_printer}')
    PRINTER_DEFAULTS = {"DesiredAccess": win32print.PRINTER_ALL_ACCESS}
    try:
        printer_handle = win32print.OpenPrinter(printer_name, PRINTER_DEFAULTS)
    except Exception as exc:
        text_error = 'ошибка открытия принтера'
        logging.debug(f' {text_error} {exc}')
        ctypes.windll.user32.MessageBoxW(0, text_error, 'Ошибка', 0x10)
        exit(2000)
    default_printer_properties = win32print.GetPrinter(printer_handle, 2)
    # Применяем настройки принтера
    win32print.SetPrinter(printer_handle, 2, default_printer_properties, 0)
    logging.debug(f'применили все настройки печати {default_printer_properties}')
    error_level = print_file(i_file, new_printer)
    logging.debug(f'отправили на печать наш файл')
    time.sleep(5)
    win32print.SetDefaultPrinter(old_printer)
    logging.debug(f'вернули старый принтер по усолчанию {old_printer}')
    return error_level

def print_file(pfile, printer):
    """
    функция отправки на принтер конкретного файла,
    используем винапи
    :param pfile: str полное имя файла
    :param printer: str имя принтера как в винде
    :return:
    """
    error_level = win32api.ShellExecute(
        0,
        "print",
        '%s' % pfile,
        '/d:"%s"' % printer,
        ".",
        0
    )
    return error_level


def main():
    pass

if __name__ == '__main__':
    main()