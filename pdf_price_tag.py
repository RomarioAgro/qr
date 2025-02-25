"""
печать ценников без QR кода
"""
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from sys import argv, exit, path
import os
from json_read import ReadJSON
import logging
import datetime
import time
from typing import Dict
from sendtoprinter import print_pdf_in_chunks
from text_on_pdf import text_on_page_spit_by_word, text_on_page_split_by_char



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


def print_artikul_name(c,
                       vtext: str = 'Производитель название артикула',
                       pole: float = 2.0,
                       ystart: float = 0.0,
                       xfinish: float = 0.0,
                       font_size: int = 8,
                       font_name: str = 'ArialBold'
                       ) -> float:
    """
    печать названия артикула
    # text model название артикула
    :return: ytext float на какой высоте остановился наш текст
    """
    c.setFont(font_name, font_size)
    ytext = text_on_page_spit_by_word(c,
                                      vtext=vtext,
                                      vtext_font_size=font_size,
                                      xstart=pole,
                                      ystart=ystart - font_size,
                                      xfinish=xfinish)
    return ytext


def print_sale_price(c,
               vtext: str = '100.00',
               pole: float = 2.0,
               ystart: float = 0.0,
               xfinish: float = 0.0,
               font_size: int = 8,
               font_name: str = 'ArialBold',
               cross_out: bool = False,
               price_only: bool = True) -> float:
    """
    печатьцены и распродажи
    :param c: объект пдф
    :param vtext: строка цены-распродажи
    :param pole: поле до границы листка
    :param xstart: Х координата старта
    :param ystart: Y координата старта
    :param xfinish: X координата финиша
    :param font_size: размер шрифта
    :param font_name: название шрифта
    :param cross_out: перечеркивать или нет
    :return:
    """
    vtext = vtext + 'р.'


    if price_only is True:
        xstart = c.__dict__['_pagesize'][0] // 2 - stringWidth(vtext, font_name, font_size) // 2
        ystart = c.__dict__['_pagesize'][1] // 2 - font_size - pole
    else:
        xstart = c.__dict__['_pagesize'][0] - stringWidth(vtext, font_name, font_size) - pole * 2
        ystart = ystart - font_size - pole
    c.setFont(font_name, font_size)
    ytext = text_on_page_split_by_char(c, vtext=vtext, vtext_font_size=font_size, xstart=xstart, ystart=ystart,
                 xfinish=xfinish - pole, cross_out=cross_out)
    return ytext


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
    pole = c_height // 20
    # печать названия артикула
    art_name = price_tag_dict.get('mod', None)
    ytext = print_artikul_name(c, vtext=art_name, pole=pole, ystart=c_height, xfinish=c_width - pole, font_size=8, font_name='ArialBold')
    # печать названия артикула

    # печать размера
    razmer = 'Размер ' + price_tag_dict.get('razm', None)
    if razmer:
        ytext = print_artikul_name(c, vtext=razmer, pole=pole, ystart=ytext, xfinish=c_width - pole, font_size=14, font_name='ArialBold')

    # печать распродажи
    sale = price_tag_dict.get('sale', '0.0')
    price = price_tag_dict.get('price', '0.0')

    if float(sale) > 0.0:
        ytext = c_height * 0.6
        ytext = print_sale_price(c,
                                 vtext=price,
                                 pole=pole,
                                 ystart=ytext,
                                 xfinish=c_width - pole,
                                 font_size=14,
                                 font_name='Arial',
                                 cross_out=True,
                                 price_only=False)
        ytext = print_sale_price(c,
                                 vtext=sale,
                                 pole=pole,
                                 ystart=ytext,
                                 xfinish=c_width - pole,
                                 font_size=19,
                                 font_name='ArialBold',
                                 cross_out=False,
                                 price_only=False)
    else:
        ytext = print_sale_price(c,
                                 vtext=price,
                                 pole=pole,
                                 ystart=ytext,
                                 xfinish=c_width - pole,
                                 font_size=19,
                                 font_name='ArialBold',
                                 cross_out=False,
                                 price_only=True)
    a = int(price_tag_dict.get('defective', 0))
    if int(price_tag_dict.get('defective', 0)) == 1:
        font_size = 19
        c.setFont('Arial', font_size)
        vtext = "БРАК"
        xs = pole * 2
        ytext = text_on_page_spit_by_word(c, vtext=vtext, vtext_font_size=font_size, xstart=xs, ystart=ytext,
                                          xfinish=c_width, cross_out=False)
    vtext = 'цена за 1 шт.'
    vtext_font_size = 6
    c.setFont('Arial', vtext_font_size)
    xs = c_width - stringWidth(vtext, 'Arial', vtext_font_size) - pole * 2
    ytext = 0 + vtext_font_size + pole
    ytext = text_on_page_spit_by_word(c, vtext=vtext, vtext_font_size=vtext_font_size, xstart=xs, ystart=ytext,
                 xfinish=c_width, cross_out=False)

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
