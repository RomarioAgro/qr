"""
печать кодов маркировки честного знака
"""
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.pdfbase.pdfmetrics import stringWidth
from sys import argv, exit, path
import os
from json_read import ReadJSON
import logging
import datetime
import time
from typing import Dict
from sendtoprinter import print_pdf_in_chunks
module_path = "d:\\kassa\\script_py\\shtrih"
if module_path not in path:
    path.append(module_path)
from preparation_km_to_honest_sign import preparation_km





widthPage = 57 * mm
heightPage = 40 * mm


current_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H_%M_%S')
logging.basicConfig(
    filename=argv[1] + '\\' + argv[2] + "_" + current_time + '_.log',
    filemode='a',
    level=logging.DEBUG,
    format="%(asctime)s - %(filename)s - %(funcName)s: %(lineno)d - %(message)s",
    datefmt='%H:%M:%S')

logging.debug('start')


def text_on_page_split_by_char(canvs,
                               vtext: str = '',
                               vtext_font_size: int = 10,
                               xstart: int = 0,
                               ystart: int = 0,
                               xfinish: int = 170) -> int:
    """
    функция размещения текста на нашем объекте pdf
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
    for char in vtext:
        x_text_print = xstart + stringWidth(vtext_result, 'Arial', vtext_font_size)
        if x_text_print < xfinish:
            vtext_result = vtext_result + char
        else:
            canvs.drawString(xstart, ystart, vtext_result)
            if char != " ":
                vtext_result = char
            else:
                vtext_result = ""
            ystart = ystart - vtext_font_size
    else:
        canvs.drawString(xstart, ystart, vtext_result)
    return ystart

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
    size_space = stringWidth(' ', 'Arial', vtext_font_size)
    for word in words:
        size_word = stringWidth(word, 'Arial', vtext_font_size)
        # вычисляем где по Х кончится наша строка для печати
        size_text_print = xstart + stringWidth(vtext_result, 'Arial', vtext_font_size) + size_space + size_word
        # если он меньше чем координата конца области печати, то увеличиваем нашу строку на слово и пробел
        if size_text_print < xfinish:
            vtext_result += word + ' '
        # если больше то печатаем что есть, заменяем строку печати текущим словом с пробелом
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



def make_pdf_page(c, price_tag_dict: dict = {}):
    """
    функция создания объекта pdf страницы
    :param c: объект pdf
    :param price_tag_dict dict словарь с инфой о шк,
        дата изготовления, сорт, адрес производства, гост
    :param care объект картинка с уходом
    :param qr_data: str строка c QR кодом
    :param vtext: str строка с текстом на ценнике
    :param vtext_price: str строка с ценой
    :param shop: str строка с названием магазина
    :return: file
    """
    pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
    pdfmetrics.registerFont(TTFont('ArialBold', 'arialbd.ttf'))
    c_width = c.__dict__['_pagesize'][0]
    c_height = c.__dict__['_pagesize'][1]
    qr_width = qr_height = c_height // 1.5
    pole = c_height // 20
    # image qr-code
    qr_data = price_tag_dict.get('qr', None)
    if qr_data != '':
        qr_data = preparation_km(qr_data)
        barcode = createBarcodeDrawing("DataMatrix", value=qr_data, xdim=1)
        desired_size = qr_height  # Желаемый размер в пикселях
        current_height = barcode.height
        scale_factor = desired_size / current_height
        c.saveState()
        c.translate(c_width - qr_width - pole, c_height - qr_height - pole * 0.5)  # Координаты вставки
        c.scale(scale_factor, scale_factor)  # Масштабирование
        barcode.drawOn(c, x=0, y=0)
        c.restoreState()
    # image qr-code
    #рамка вокруг qr-code
    ramka_x = c_width - qr_width - pole * 1.4 ##координата Х с которой начинается рамка QR кода
    c.rect(ramka_x,
           c_height - qr_height - pole * 0.8,
           qr_width + pole * 0.8,
           qr_height + pole * 0.65,
           fill=0)
    # рамка вокруг qr-code
    vtext_font_size = int(c_height // 15)
    ytext = c_height - vtext_font_size * 1.5
    # text qr кода
    c.setFont('Arial', vtext_font_size)
    text_on_page_split_by_char(c, vtext=qr_data[:31], vtext_font_size=vtext_font_size, xstart=ramka_x,
                 ystart=c_height - qr_height - vtext_font_size - pole, xfinish=c_width - pole)
    # text qr кода
    vtext_font_size = int(c_height // 12)
    c.setFont('ArialBold', vtext_font_size)
    # text model название артикула
    vtext = price_tag_dict.get('mod', None)
    if vtext:
        ytext = vtext_font_size
        c.setFont('ArialBold', vtext_font_size)
        ytext = text_on_page_spit_by_word(c,
                                          vtext=vtext,
                                          vtext_font_size=vtext_font_size,
                                          xstart=pole,
                                          ystart=c_height - ytext,
                                          xfinish=ramka_x)
    # text model
    # text size
    vtext = price_tag_dict.get('razm', None)
    if vtext:
        # vtext_font_size = c_height // 15
        vtext = 'Размер: ' + vtext
        ytext = ytext - vtext_font_size
        c.setFont('ArialBold', vtext_font_size)
        ytext = text_on_page_split_by_char(c,
                                           vtext=vtext,
                                           vtext_font_size=vtext_font_size,
                                           xstart=pole,
                                           ystart=ytext,
                                           xfinish=c_width - (qr_width + 20 + pole))
    # text size
    # text color
    vtext = price_tag_dict.get('col_gl_txt', None)
    if vtext:
        vtext = 'Цвет: ' + vtext.strip()
        ytext = ytext - vtext_font_size
        c.setFont('ArialBold', vtext_font_size)
        ytext = text_on_page_split_by_char(c,
                                           vtext=vtext,
                                           vtext_font_size=vtext_font_size,
                                           xstart=pole, ystart=ytext,
                                           xfinish=c_width - (qr_width + 20 + pole))
    # text color
    c.showPage()

def get_model_color_size(name: str = 'CLE C680к Трусы жен.спорт|чсрный(13я061)|M') -> Dict:
    """
    получаем модель, цвет, размер из
    строки названия артикула
    :return:
    """
    data = {
        'mod': 'model',  # имя
        'col_gl_txt': 'color',  # цвет
        'razm': 'size'  # размер
    }
    parts = name.split('|')
    if len(parts) > 2:
        data = {
            'mod': parts[0],  # имя
            'col_gl_txt': parts[1],  # цвет
            'razm': parts[2]  # размер
        }
    return data

def main():
    print('hello')
    all_pt = ReadJSON(argv[1], argv[2])
    logging.debug('прочитали весь json {0}'.format(all_pt))
    i_path = argv[1] + '\\qr\\'
    if os.path.exists(i_path) is False:
        os.makedirs(i_path)
    os.chdir(i_path)
    f_name = str(int(time.time()))
    pdf_path = i_path + f_name + ".pdf"
    pdf_canvas = canvas.Canvas(pdf_path, pagesize=(widthPage, heightPage))
    logging.debug('создали объект pdf')
    for price_tag in all_pt.data:
        print('1')
        price_tag.update(get_model_color_size(name=price_tag.get('name', '')))
        print('перебираем наши ценники {0}'.format(price_tag))
        logging.debug('перебираем наши ценники {0}'.format(price_tag))
        make_pdf_page(pdf_canvas, price_tag)
    pdf_canvas.save()
    logging.debug('pdf сохранен, сейчас будем печатать')
    error_level = print_pdf_in_chunks(pdf_path, 30)
    logging.debug(f'результат печати {error_level}')
    os.startfile(pdf_path)



if __name__ == '__main__':
    main()
