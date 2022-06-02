# -*- coding: utf-8 -*-
import json
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm, mm
import qrcode
import win32print
import win32api
from os.path import isfile
from os import remove as osrem
import glob
import time

def del_pdf_in_folder(i_path_pdf):
    file_queue = [f for f in glob.glob(i_path_pdf + "*.pdf") if isfile(f)]
    if len(file_queue) > 0:
        for i in file_queue:
            osrem(i)

def sendtoprinter():
    old_printer = win32print.GetDefaultPrinter()
    new_printer = win32print.SetDefaultPrinter('Honeywell PC42t plus (203 dpi)')
    # file_queue = [f for f in glob.glob("%s\\*.pdf" % source_path) if isfile(f)]
    file_queue = [f for f in glob.glob("d:\\files\\*.pdf") if isfile(f)]
    if len(file_queue) > 0:
        for i in file_queue:
            print_file(i, new_printer)
            print(i)
    time.sleep(5)
    if len(file_queue) > 0:
        for i in file_queue:
            osrem(i)
    win32print.SetDefaultPrinter(old_printer)

def print_file(pfile, printer):
    win32api.ShellExecute(
        0,
        "print",
        '%s' % pfile,
        '/d:"%s"' % printer,
        ".",
        0
        )




def text_on_page(canvs, vtext='Test', vtext_font_size=10, xstart=0, ystart=0, xfinish=170):
    from reportlab.pdfbase.pdfmetrics import stringWidth
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

def make_pdf_page(c, qr_data='99999', vtext='zaglushka',vtext_price='000000',shop ='not shop'):
    pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
    pdfmetrics.registerFont(TTFont('ArialBold', 'arialbd.ttf'))
    c_width = c.__dict__['_pagesize'][0]
    c_height = c.__dict__['_pagesize'][1]
    vtext_font_size = 10
    c.setFont('Arial', vtext_font_size)
    qr_width = qr_height = c_width // 3
    pole = 4*mm
    # image qr-code
    c.drawInlineImage(qrcode.make(qr_data), c_width - qr_width - pole, c_height - qr_height, width=qr_width, height=qr_height)
    c.rect(c_width - qr_width - pole, c_height - qr_height, qr_width, qr_height, fill=0)
    # image qr-code
    ytext = c_height - vtext_font_size * 1.5
    # image name of vendor code
    ytext = text_on_page(c, vtext=vtext, vtext_font_size=vtext_font_size, xstart=vtext_font_size, ystart=ytext, xfinish=c_width - (qr_width+20 + pole))
    # image name of vendor code
    price_font_size = 17
    c.setFont('Arial', price_font_size)
    ytext = ytext - price_font_size * 2
    # image price
    text_on_page(c, vtext=vtext_price+'р.', vtext_font_size=price_font_size, xstart=vtext_font_size, ystart=ytext, xfinish=c_width - (qr_width+20))
    vtext_shop = 'Цена за 1 шт усл. ' + shop
    shop_font_size = 6
    c.setFont('ArialBold', shop_font_size)
    # image name of shop
    text_on_page(c, vtext=vtext_shop, vtext_font_size=shop_font_size, xstart=shop_font_size, ystart=shop_font_size*2, xfinish=c_width - (qr_width+20))
    qr_font_size = 8
    c.setFont('Arial', qr_font_size)
    text_on_page(c, vtext=qr_data, vtext_font_size=qr_font_size, xstart=c_width-qr_width-pole, ystart=qr_height-10, xfinish=c_width - pole)
    c.save()



widthPage = 6 * cm
heightPage = 4 * cm
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
# for pt in price_tag:
#     pdf_canvas = canvas.Canvas(pt.get('qr') + ".pdf", pagesize=(widthPage, heightPage))
#     make_pdf_page(pdf_canvas, qr_data=pt.get('qr'), vtext=pt.get('name'),
#                     vtext_price=pt.get('price'), shop=pt.get('shop'))


i_path = 'd:\\files\\'
del_pdf_in_folder(i_path)
with open('d:\\files\\qr.json') as json_file:
    data = json.load(json_file)
    for pt in data['price_tag']:
        pdf_canvas = canvas.Canvas('d:\\files\\' + pt['qr'] + ".pdf", pagesize=(widthPage, heightPage))
        make_pdf_page(pdf_canvas, qr_data=pt['qr'], vtext=pt['name'],
                        vtext_price=pt['price'], shop=pt['shop'])

sendtoprinter()