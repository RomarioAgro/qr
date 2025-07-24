from decouple import config
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import landscape
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.graphics.barcode import createBarcodeDrawing
from json_read import ReadJSON
from sys import argv, exit
import os
# import win32print
# import win32api
import random
import logging
import datetime
import time
from sendtoprinter import sendtoprinter


widthPage = 35
heightPage = 20
widthPage_mm = widthPage * mm
heightPage_mm = heightPage * mm


current_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H_%M_%S')
logging.basicConfig(
    filename=argv[1] + '\\' + current_time + '_.log',
    filemode='a',
    level=logging.DEBUG,
    format="%(asctime)s - %(filename)s - %(funcName)s: %(lineno)d - %(message)s",
    datefmt='%H:%M:%S')

logging.debug('start')


def text_on_page_spit_by_word(canvs, vtext: str = '', vtext_font_size: int = 10, xstart: int = 0, ystart: int = 0,
                 xfinish: int = 170, cross_out:bool = False) -> int:
    """
    функция размещения текста на нашем объекте pdf разбиваем текстпо словам
    :param canvs: obj сам объект pdf
    :param vtext: str текст который будем размещать
    если текст не входит в одну строку, то будем делать переносы,
    поэтому по выходу надо знать на какой высоте объект уже занят
    :param vtext_font_size: int размер шрифта
    :param xstart: int стартовая координата X
    :param ystart: int стартовая координата Y
    :param xfinish: int финишная координата X
    :return: int финишная координата Y, на какой высоте остановились
    """
    # xstart, ystart start coordinates our text string
    vtext_result = ''
    words = vtext.split(" ")
    for word in words:
        size_space = stringWidth(' ', 'Arial', vtext_font_size)
        size_word = stringWidth(word, 'Arial', vtext_font_size)
        x_text_print = xstart + stringWidth(vtext_result, 'Arial', vtext_font_size) + size_space + size_word
        if x_text_print < xfinish:
            vtext_result += word + ' '
        else:
            canvs.drawString(xstart, ystart, vtext_result)
            if cross_out:
                canvs.line(xstart, ystart, xstart + stringWidth(vtext_result, 'Arial', vtext_font_size), ystart + vtext_font_size)
            ystart = ystart - vtext_font_size
            vtext_result = word + ' '
    else:
        canvs.drawString(xstart, ystart, vtext_result)
        if cross_out:
            canvs.line(xstart, ystart, xstart + stringWidth(vtext_result, 'Arial', vtext_font_size), ystart + vtext_font_size)
    return ystart

def make_pdf_page(c, number: int = 100201):
    """
    функция создания объекта pdf страницы
    печать QR кодов для учета картриджей
    """

    cross_out = False
    pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
    pdfmetrics.registerFont(TTFont('ArialBold', 'arialbd.ttf'))
    c_width = c.__dict__['_pagesize'][0]
    c_height = c.__dict__['_pagesize'][1]
    qr_width = qr_height = c_height * 0.9
    pole = 1 * mm
    barcode = createBarcodeDrawing("DataMatrix", value=number, xdim=1)
    desired_size = c_height - pole  # Желаемый размер в пикселях
    current_height = barcode.height
    scale_factor = desired_size / current_height
    c.saveState()
    c.translate(c_width - qr_width + 0.5, 1)  # Координаты вставки
    c.scale(scale_factor, scale_factor)  # Масштабирование
    barcode.drawOn(c, x=0, y=0)
    c.restoreState()


    vtext_font_size = 4
    c.setFont('Arial', vtext_font_size)
    xs = pole
    ytext = c_height // 2
    ytext = text_on_page_spit_by_word(c, vtext=number, vtext_font_size=vtext_font_size, xstart=xs, ystart=ytext,
                 xfinish=c_width, cross_out=False)
    c.showPage()


def main():
    i_path = argv[1]
    if os.path.exists(i_path) is False:
        os.makedirs(i_path)
    f_name = str(random.randint(1, 99999))
    pdf_path = argv[1] + f_name + ".pdf"
    # создаем объект pdf станицы
    pdf_canvas = canvas.Canvas(pdf_path, pagesize=landscape((widthPage, heightPage)))
    logging.debug('создали объект pdf {0}'.format(pdf_canvas))
    number_s = 100201
    number_f = 101000
    for number in range(number_s, number_f):
        print(f'перебираем наши ценники {number}')
        logging.debug(f'перебираем наши ценники {number}')
        # формируем pdf листик
        logging.debug('собираемся формировать страничку pdf'.format())
        make_pdf_page(pdf_canvas, str(number))
        logging.debug('закончили формировать pdf страничку')
    pdf_canvas.save()
    os.startfile(pdf_path)


if __name__ == '__main__':
    main()


