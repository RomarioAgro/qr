from decouple import config
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from json_read import ReadJSON
from sys import argv, exit
import os
import win32print
import win32api
import random
import logging
import datetime
import time
from pdf_creator_OOP import sendtoprinter, print_file


widthPage = 35 * mm
heightPage = 20 * mm

current_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H_%M_%S')
logging.basicConfig(
    filename=argv[1] + '\\' + argv[2] + "_" + current_time + '_.log',
    filemode='a',
    level=logging.DEBUG,
    format="%(asctime)s - %(filename)s - %(funcName)s: %(lineno)d - %(message)s",
    datefmt='%H:%M:%S')

logging.debug('start')


def text_on_page_split_by_char(canvs, vtext: str = '', vtext_font_size: int = 10, xstart: int = 0, ystart: int = 0,
                 xfinish: int = 170, cross_out:bool = False) -> int:
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
            if cross_out:
                canvs.line(xstart, ystart, xstart + stringWidth(vtext_result, 'Arial', vtext_font_size), ystart + vtext_font_size)
            if char != " ":
                vtext_result = char
            else:
                vtext_result = ""
            ystart = ystart - vtext_font_size
    else:
        canvs.drawString(xstart, ystart, vtext_result)
        if cross_out:
            canvs.line(xstart, ystart, xstart + stringWidth(vtext_result, 'Arial', vtext_font_size), ystart + vtext_font_size)
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
    cross_out: bool флаг зачернутый текст будет или нет
    :return: file
    """

    cross_out = False
    pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
    pdfmetrics.registerFont(TTFont('ArialBold', 'arialbd.ttf'))
    c_width = c.__dict__['_pagesize'][0]
    c_height = c.__dict__['_pagesize'][1]
    pole = 1
    # image sale
    sale = price_tag_dict.get('sale', None)
    price_font_size = 16
    ytext = c_height - price_font_size
    if sale:
        if float(sale) > 0.0:
            c.setFont('Arial', price_font_size)
            # ytext = ytext - price_font_size * 3
            text_sale = sale + 'р.'
            xs = c_width - c_width + (c_width - stringWidth(text_sale, 'Arial', price_font_size)) // 2
            ytext = text_on_page_split_by_char(c, vtext=text_sale, vtext_font_size=price_font_size, xstart=xs, ystart=ytext,
                         xfinish=c_width, cross_out=cross_out)
            cross_out = True
    # image sale
    # image price
    vtext_price = price_tag_dict.get('price', None)
    if vtext_price:
        vtext_price = vtext_price + 'р.'
        c.setFont('Arial', price_font_size)
        xs = c_width - c_width + (c_width - stringWidth(vtext_price, 'Arial', price_font_size)) // 2
        ytext = ytext - price_font_size
        ytext = text_on_page_split_by_char(c, vtext=vtext_price, vtext_font_size=price_font_size, xstart=xs, ystart=ytext,
                     xfinish=c_width, cross_out=cross_out)
    vtext = 'цена за 1 шт.'
    if vtext_price:
        vtext_font_size = c_height // 25
        c.setFont('Arial', vtext_font_size)
        xs = c_width - c_width + (c_width - stringWidth(vtext, 'Arial', vtext_font_size)) // 2
        ytext = ytext - vtext_font_size
        ytext = text_on_page_spit_by_word(c, vtext=vtext, vtext_font_size=vtext_font_size, xstart=xs, ystart=ytext,
                     xfinish=c_width, cross_out=False)
    name = price_tag_dict.get('name', None)
    # text under price
    if name:
        vtext_font_size = 7
        c.setFont('Arial', vtext_font_size)
        xs = c_width - c_width + pole
        ytext = ytext - vtext_font_size
        ytext = text_on_page_spit_by_word(c, vtext=name, vtext_font_size=vtext_font_size, xstart=xs, ystart=ytext,
                     xfinish=c_width, cross_out=False)
    c.showPage()


def main():
    print('hello')
    # читаем json  с данными ценника
    all_pt = ReadJSON(argv[1], argv[2])
    logging.debug('прочитали весь json {0}'.format(all_pt))
    i_path = argv[1] + '\\qr\\'
    if os.path.exists(i_path) is False:
        os.makedirs(i_path)
    f_name = str(random.randint(1, 99999))
    pdf_path = argv[1] + '\\qr\\' + f_name + ".pdf"
    # создаем объект pdf станицы
    pdf_canvas = canvas.Canvas(pdf_path, pagesize=(widthPage, heightPage))
    logging.debug('создали объект pdf {0}'.format(pdf_canvas))
    for price_tag in all_pt.data['price_tag']:
        print('перебираем наши ценники {0}'.format(price_tag))
        logging.debug('перебираем наши ценники {0}'.format(price_tag))
        # формируем pdf листик
        logging.debug('собираемся формировать страничку pdf'.format())
        make_pdf_page(pdf_canvas, price_tag)
        logging.debug('закончили формировать pdf страничку')
    pdf_canvas.save()

    sendtoprinter(i_file=pdf_path, paper_width=350, paper_height=200)
    os.startfile(pdf_path)


if __name__ == '__main__':
    main()
