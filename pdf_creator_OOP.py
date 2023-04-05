from decouple import config
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from PIL import Image, ImageFilter
import io
from from_sql import Sql
import qrcode
from json_read import ReadJSON
from sys import argv
import os
import win32print
import win32api
import time
import random
import logging
import json



widthPage = 57 * mm
heightPage = 40 * mm


class PriceTag:
    """
    класс одного ценника, одной страницы
    """
    def __init__(self, pt: dict = {}):
        self.pt = pt


def sendtoprinter(i_file: str = ''):
    """
    функция отправки на печать pdf файлов из папки
    :return:
    """
    old_printer = win32print.GetDefaultPrinter()
    new_printer = win32print.SetDefaultPrinter('Honeywell PC42t plus (203 dpi)')
    error_level = print_file(i_file, new_printer)
    time.sleep(5)
    win32print.SetDefaultPrinter(old_printer)
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


# def make_pdf_page(c, qr_data: str = '99999', vtext: str = 'zaglushka', vtext_price: str = '000000',
#                   shop: str = 'not shop', sale='00000'):
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
    vtext_font_size = c_height // 10
    c.setFont('ArialBold', vtext_font_size)
    qr_width = qr_height = c_height // 2.5
    pole = 1
    # image qr-code
    qr_data = price_tag_dict.get('qr', None)
    if qr_data:
        c.drawInlineImage(qrcode.make(qr_data), c_width - qr_width, c_height - qr_height, width=qr_width,
                          height=qr_height)
    c.rect(c_width - qr_width, c_height - qr_height, qr_width, qr_height, fill=0)
    # image qr-code
    # rectangle replacement_part
    replacement_part_x = 35 * mm
    replacement_part_y = 20 * mm
    c.setDash(2, 2)
    c.rect(c_width - replacement_part_x, 0, replacement_part_x, replacement_part_y, fill=0)
    c.setDash(1, 0)
    # rectangle replacement_part

    # text qr кода
    vtext_font_size = c_height // 20
    c.setFont('ArialBold', vtext_font_size)
    text_on_page_split_by_char(c, vtext=qr_data, vtext_font_size=vtext_font_size, xstart=c_width // 2.6 + qr_width,
                 ystart=c_height - qr_height - vtext_font_size, xfinish=c_width - pole * mm)
    # text qr кода
    # text product group
    vtext = price_tag_dict.get('gr_tov', None)
    vtext_font_size = c_height // 15
    if vtext:
        ytext = c_height - vtext_font_size
        c.setFont('ArialBold', vtext_font_size)
        ytext = text_on_page_split_by_char(c, vtext=vtext, vtext_font_size=vtext_font_size, xstart=0, ystart=ytext,
                             xfinish=c_width - (qr_width + 20 + pole), cross_out=cross_out)
    # text product group
    # text model
    vtext = price_tag_dict.get('mod', None)
    if vtext:
        # vtext_font_size = c_height // 15
        vtext = 'Арт: ' + vtext
        ytext = ytext - vtext_font_size
        c.setFont('ArialBold', vtext_font_size)
        ytext = text_on_page_split_by_char(c, vtext=vtext, vtext_font_size=vtext_font_size, xstart=0, ystart=ytext,
                             xfinish=c_width - (qr_width + 20 + pole), cross_out=cross_out)
    # text model
    # text size
    vtext = price_tag_dict.get('razm', None)
    if vtext:
        # vtext_font_size = c_height // 15
        vtext = 'Размер: ' + vtext
        ytext = ytext - vtext_font_size
        c.setFont('ArialBold', vtext_font_size)
        ytext = text_on_page_split_by_char(c, vtext=vtext, vtext_font_size=vtext_font_size, xstart=0, ystart=ytext,
                             xfinish=c_width - (qr_width + 20 + pole), cross_out=cross_out)
    # text size
    # text color
    vtext = price_tag_dict.get('col_gl_txt', None)
    if vtext:
        # vtext_font_size = c_height // 15
        vtext = 'Цвет: ' + vtext.strip()
        ytext = ytext - vtext_font_size
        c.setFont('ArialBold', vtext_font_size)
        ytext = text_on_page_split_by_char(c, vtext=vtext, vtext_font_size=vtext_font_size, xstart=0, ystart=ytext,
                             xfinish=c_width - (qr_width + 20 + pole), cross_out=cross_out)
    # text color
    # image structure
    vtext = price_tag_dict.get('sost', None)
    if vtext:
        vtext = 'Состав: ' + vtext
        vtext_font_size = c_height // 17
        ytext = ytext - vtext_font_size
        c.setFont('ArialBold', vtext_font_size)
        ytext = text_on_page_spit_by_word(c, vtext=vtext, vtext_font_size=vtext_font_size, xstart=0, ystart=ytext,
                             xfinish=c_width - (qr_width + pole), cross_out=False)
    # image structure
    # image russia
    vtext = price_tag_dict.get('russia', None)
    if vtext:
        vtext_font_size = c_height // 20
        ytext = ytext - vtext_font_size
        c.setFont('ArialBold', vtext_font_size)
        ytext = text_on_page_spit_by_word(c, vtext=vtext, vtext_font_size=vtext_font_size, xstart=0, ystart=ytext,
                             xfinish=c_width - (qr_width + 20 + pole), cross_out=False)
    # image russia
    # image manufacturer
    vtext = price_tag_dict.get('org', None)
    if vtext:
        vtext_font_size = c_height // 20
        ytext = ytext - vtext_font_size
        vtext = 'Производитель: ' + vtext
        c.setFont('ArialBold', vtext_font_size)
        ytext = text_on_page_spit_by_word(c, vtext=vtext, vtext_font_size=vtext_font_size, xstart=0, ystart=ytext,
                             xfinish=c_width - qr_width, cross_out=False)
    # image manufacturer
    # image adres_shp
    vtext = price_tag_dict.get('adres_shp', None)
    if vtext:
        vtext_font_size = c_height // 20
        ytext = ytext - vtext_font_size
        c.setFont('ArialBold', vtext_font_size)
        ytext = text_on_page_spit_by_word(c, vtext=vtext, vtext_font_size=vtext_font_size, xstart=0, ystart=ytext,
                             xfinish=c_width - (qr_width + 20 + pole), cross_out=False)
    # image adres_shp
    # image care
    try:
        care = Image.open(io.BytesIO(price_tag_dict.get('care', None)))
    except Exception as exc:
        care = None
        print(exc)
    # care = Image.open('1.bmp')
    if care:
        hcare = vtext_font_size * 1.5
        ycare = ytext - hcare - pole
        # ковертируем картинку в градации серого
        care_black_and_white = care.convert('L')
        threshold = 50
        #   все что не черное делаем белым
        care_black_and_white = care_black_and_white.point(lambda x: 255 if x > threshold else 0)
        # прогоняем через фильтр расширение, делаем пиксель черным если у него есть 1 черный сосед
        for _ in range(2):
            care_black_and_white = care_black_and_white.filter(ImageFilter.MinFilter(3))
        c.drawInlineImage(care_black_and_white, 0, ycare, width=c_width // 2.5, height=hcare)
    # image care
    # image make date
    vtext = price_tag_dict.get('make_date', None)
    if vtext:
        vtext_font_size = c_height // 20
        ytext = ycare - vtext_font_size
        c.setFont('ArialBold', vtext_font_size)
        ytext = text_on_page_split_by_char(c, vtext=vtext, vtext_font_size=vtext_font_size, xstart=0, ystart=ytext,
                             xfinish=c_width - (qr_width + 20 + pole), cross_out=False)
    # image make date
    # image GOST
    vtext = price_tag_dict.get('gost', None)
    if vtext:
        vtext_font_size = c_height // 15
        ytext = ytext - vtext_font_size
        c.setFont('ArialBold', vtext_font_size)
        ytext = text_on_page_split_by_char(c, vtext=vtext, vtext_font_size=vtext_font_size, xstart=0, ystart=ytext,
                             xfinish=c_width - (qr_width + 20 + pole), cross_out=False)
    # image GOST
    eac = Image.open('eac.png')
    if eac:
        weac = heac = c_height // 4.5
        c.drawInlineImage(eac, 0, 0, width=weac, height=heac)
    # image sort
    vtext = price_tag_dict.get('sort', None)
    if vtext:
        vtext_font_size = c_height // 20
        ytext = ytext - vtext_font_size
        c.setFont('ArialBold', vtext_font_size)
        ytext = text_on_page_split_by_char(c, vtext=vtext, vtext_font_size=vtext_font_size, xstart=weac, ystart=ytext,
                             xfinish=c_width - (qr_width + 20 + pole), cross_out=False)
    # image sort
    # image iz_nakl_ushk i don't know that this, but requires guidance
    vtext = price_tag_dict.get('iz_nakl_ushk', None)
    if vtext:
        vtext_font_size = c_height // 25
        ytext = ytext - vtext_font_size
        c.setFont('ArialBold', vtext_font_size)
        ytext = text_on_page_split_by_char(c, vtext=vtext, vtext_font_size=vtext_font_size, xstart=weac, ystart=ytext,
                             xfinish=c_width - (qr_width + 20 + pole), cross_out=False)
    # image iz_nakl_ushk i don't know that this, but requires guidance
    # image sale
    sale = price_tag_dict.get('sale', None)
    price_font_size = c_height // 7
    ytext = replacement_part_y - price_font_size
    if sale:
        if float(sale) > 0.0:
            c.setFont('Arial', price_font_size)
            # ytext = ytext - price_font_size * 3
            text_sale = sale + 'р.'
            xs = c_width - replacement_part_x + (replacement_part_x - stringWidth(text_sale, 'Arial', price_font_size)) // 2
            ytext = text_on_page_split_by_char(c, vtext=text_sale, vtext_font_size=price_font_size, xstart=xs, ystart=ytext,
                         xfinish=c_width, cross_out=cross_out)
            cross_out = True
    # image sale
    # image price
    vtext_price = price_tag_dict.get('price', None)
    if vtext_price:
        vtext_price = vtext_price + 'р.'
        c.setFont('Arial', price_font_size)
        xs = c_width - replacement_part_x + (replacement_part_x - stringWidth(vtext_price, 'Arial', price_font_size)) // 2
        ytext = ytext - price_font_size
        ytext = text_on_page_split_by_char(c, vtext=vtext_price, vtext_font_size=price_font_size, xstart=xs, ystart=ytext,
                     xfinish=c_width, cross_out=cross_out)
    vtext = 'цена за 1 шт.'
    if vtext_price:
        vtext_font_size = c_height // 25
        c.setFont('Arial', vtext_font_size)
        xs = c_width - replacement_part_x + (replacement_part_x - stringWidth(vtext, 'Arial', vtext_font_size)) // 2
        ytext = ytext - vtext_font_size
        ytext = text_on_page_spit_by_word(c, vtext=vtext, vtext_font_size=vtext_font_size, xstart=xs, ystart=ytext,
                     xfinish=c_width, cross_out=False)
    name = price_tag_dict.get('name', None)
    # text under price
    if name:
        vtext_font_size = c_height // 15
        c.setFont('Arial', vtext_font_size)
        xs = c_width - replacement_part_x + pole
        ytext = ytext - vtext_font_size
        ytext = text_on_page_spit_by_word(c, vtext=name, vtext_font_size=vtext_font_size, xstart=xs, ystart=ytext,
                     xfinish=c_width, cross_out=False)
    c.showPage()


def main():
    all_pt = ReadJSON(argv[1], argv[2])
    i_path = argv[1] + '\\qr\\'
    if os.path.exists(i_path) is False:
        os.makedirs(i_path)
    f_name = str(random.randint(1, 99999))
    pdf_path = argv[1] + '\\qr\\' + f_name + ".pdf"
    pdf_canvas = canvas.Canvas(pdf_path, pagesize=(widthPage, heightPage))
    data_from_dbfsv = Sql('ACE', server='DBFSV\DBF2008')

    for price_tag in all_pt.data['price_tag']:
        i_pt = PriceTag(price_tag)
        # стучимся в SQL сервер
        inf_shk = data_from_dbfsv.manual(price_tag['nomnomer'])
        i_pt.pt.update(inf_shk)
        # with open(argv[1] + '\\new_qr.json', 'w') as jf:
        #     i_pt.pt['care'] = ''
        #     json.dump(i_pt.pt, jf)

        print(i_pt.pt)
        make_pdf_page(pdf_canvas, i_pt.pt)
    pdf_canvas.save()
    # sendtoprinter(i_file=pdf_path)
    os.startfile(pdf_path)


if __name__ == '__main__':
    main()