# -*- coding: utf-8 -*-
import json
import os

from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm, mm
import win32print
import win32api
from os.path import isfile
from os import remove as osrem
import glob
import time
from sys import exit
import uuid
import sys
module_path = "d:\\kassa\\script_py\\shtrih"
if module_path not in sys.path:
    sys.path.append(module_path)
from preparation_km_to_honest_sign import preparation_km



def del_pdf_in_folder(i_path_pdf):
    """
    функция очистки папки от использованых pdf
    :param i_path_pdf: str путь до папки в котрой лежaт pdf
    :return:
    """
    file_queue = [f for f in glob.glob(i_path_pdf + "*.pdf") if isfile(f)]
    if len(file_queue) > 0:
        for i in file_queue:
            osrem(i)


def sendtoprinter(work_dir:str = ''):
    """
    функция отправки на печать pdf файлов из папки
    :return:
    """
    old_printer = win32print.GetDefaultPrinter()
    new_printer = win32print.SetDefaultPrinter('Honeywell PC42t plus (203 dpi)')
    # file_queue = [f for f in glob.glob("%s\\*.pdf" % source_path) if isfile(f)]
    file_queue = [f for f in glob.glob(work_dir + "*.pdf") if isfile(f)]
    if len(file_queue) > 0:
        for i in file_queue:
            if i.find('99999999999999999999999999999999') == -1:
                error_level = print_file(i, new_printer)
                print(i)
    time.sleep(10)
    # if len(file_queue) > 0:
    #     for i in file_queue:
    #         osrem(i)
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



def text_on_page(canvs, vtext: str = '', vtext_font_size: int = 10, xstart: int = 0, ystart: int = 0,
                 xfinish: int = 170, cross_out:bool = False):
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
            if cross_out is True:
                cross_out_y = ystart + vtext_font_size // 3
                canvs.line(xstart, cross_out_y, xstart + stringWidth(vtext_result, 'Arial', vtext_font_size), cross_out_y)
            if char != " ":
                vtext_result = char
            else:
                vtext_result = ""
            ystart = ystart - vtext_font_size
    else:
        canvs.drawString(xstart, ystart, vtext_result)
        if cross_out is True:
            cross_out_y = ystart + vtext_font_size // 3
            canvs.line(xstart, cross_out_y, xstart + stringWidth(vtext_result, 'Arial', vtext_font_size), cross_out_y)
    return ystart

def make_pdf_page(c, price_tag_dict: dict = {}):
    """
    функция создания объекта pdf страницы
    :param c: объект pdf
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
    vtext_font_size = 10
    c.setFont('Arial', vtext_font_size)
    qr_width = qr_height = c_height // 2
    pole = c_height // 20
    # image qr-code
    qr_data = price_tag_dict.get('qr', '')
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
    c.rect(c_width - qr_width - pole * 1.4,
           c_height - qr_height - pole * 0.8,
           qr_width + pole * 0.8,
           qr_height + pole * 0.65,
           fill=0)
    # image qr-code
    ytext = c_height - vtext_font_size * 1.5
    # image name of vendor code
    vtext = price_tag_dict.get('name', None)
    ytext = text_on_page(c, vtext=vtext, vtext_font_size=vtext_font_size, xstart=vtext_font_size, ystart=ytext,
                         xfinish=c_width - (qr_width + 20 + pole), cross_out=cross_out)
    # image name of vendor code
    # image sale
    sale = price_tag_dict.get('sale', None)
    if sale:
        price_font_size = 16
        ytext = 4 * mm
        if float(sale) != 0:
            c.setFont('Arial', price_font_size)
            # ytext = ytext - price_font_size * 3
            xs = 4 * mm
            text_on_page(c, vtext=sale + 'р.', vtext_font_size=price_font_size, xstart=xs, ystart=ytext,
                         xfinish=c_width, cross_out=cross_out)
        # image sale
    # image price
    vtext_price = price_tag_dict.get('price', None)
    if vtext_price:
        if float(sale) != 0:
            # price_font_size = 20
            cross_out = True
        c.setFont('Arial', price_font_size)
        xs = 29 * mm
        text_on_page(c, vtext=vtext_price + 'р.', vtext_font_size=price_font_size, xstart=xs, ystart=ytext,
                     xfinish=c_width, cross_out=cross_out)
    # image price
    # текст qr кода
    qr_font_size = 6
    c.setFont('Arial', qr_font_size)
    text_on_page(c,
                 vtext=qr_data[0:31],
                 vtext_font_size=qr_font_size,
                 xstart=c_width - qr_width - pole * 1.4,
                 ystart=c_height - qr_height - pole * 0.8 - qr_font_size * 1.2,
                 xfinish=c_width - pole)
    c.showPage()


widthPage = 6 * cm
heightPage = 4 * cm


def main():
    i_path = 'd:\\files\\qr\\'
    if os.path.exists(i_path) is False:
        os.makedirs(i_path)
    del_pdf_in_folder(i_path)
    with open('d:\\files\\qr.json') as json_file:
        data = json.load(json_file)
        for pt in data['price_tag']:
            f_name_pdf = pt.get('qr', '')
            if f_name_pdf == '':
                f_name_pdf = str(uuid.uuid4()).replace('-', '')
            pdf_canvas = canvas.Canvas(i_path + f_name_pdf + ".pdf", pagesize=(widthPage, heightPage))
            # make_pdf_page(pdf_canvas, qr_data=pt['qr'], vtext=pt['name'],
            #               vtext_price=pt['price'], shop=pt['shop'], sale=pt['sale'])
            make_pdf_page(pdf_canvas, pt)
    os.startfile(i_path)
    # return sendtoprinter(work_dir=i_path)


# 170.0787401574803
# 113.38582677165354
# price_tag = [
#     {
#     'qr': '201760115211966201760115211966',
#     'name': 'Zen Водолазка муж.73300дл.р(46-52)охра; 50',
#     'price': '21799',
#     'shop': 'ЕКБ Академический'
#     },
#     {
#     'qr': '201760115211966201111111111111',
#     'name': 'YAX Джемпер жен.73300дл.р(46-52)раха; 10',
#     'price': '199',
#     'shop': 'ЕКБ Академический'
#     }
# ]
if __name__ == '__main__':
    error = main()
    exit(error)
