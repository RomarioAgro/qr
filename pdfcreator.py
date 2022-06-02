# -*- coding: utf-8 -*-

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm

pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
width = 6 * cm
height = 4 * cm
vtext_font_size = 10
# 170.0787401574803
# 113.38582677165354
print(width)
print(height)
c = canvas.Canvas("rezult.pdf", pagesize=(width, height))
c.setFont('Arial', vtext_font_size)
vtext = 'мама мыла раму, съешь еще этих французких булок и выпей чаю'
vtext = 'Zen Водолазка муж.73300дл.р(46-52)охра; 50'
# c.drawString(vtext_font_size, height - vtext_font_size, vtext)
qr_image = 'qr.png'
qr_width = qr_height = width // 3
print(qr_width, qr_height)
c.drawImage(qr_image, width - qr_width, height - qr_height, width=qr_width, height=qr_height, preserveAspectRatio=True, mask='auto')
ytext = height - vtext_font_size * 1.5
xtext = vtext_font_size
vtext_result = ""
for i in vtext:
    # very strange, but work, i don't know why my text size
    # it should be less width of page
    if len(vtext_result)*vtext_font_size < width:
        vtext_result = vtext_result + i
    else:
        c.drawString(xtext, ytext, vtext_result)
        if i != " ":
            vtext_result = i
        else:
            vtext_result = ""
        ytext = ytext - vtext_font_size

else:
    c.drawString(xtext, ytext, vtext_result)
vtext_price = '1 799.00р.'
price_font_size = vtext_font_size * 2
c.setFont('Arial', price_font_size)
print(xtext, ytext)
c.drawString(vtext_font_size, ytext - price_font_size * 2, vtext_price)
shop = 'ЕКБ Академический'
vtext_shop = 'Цена за 1 шт усл. ' + shop
shop_font_size = vtext_font_size // 2
c.setFont('Arial-Bold', shop_font_size)
c.drawString(shop_font_size, shop_font_size, vtext_shop)
qr_text = "201760115211966"

c.save()