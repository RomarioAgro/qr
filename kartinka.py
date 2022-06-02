from PIL import Image, ImageDraw, ImageFont

# width = 480
# height = 320
x = 300
y = 320
img = Image.new('RGB', (x,y), color=('#FFFFFF'))
vtext = 'мама мыла раму, съешь еще этих французких булок и выпей чаю'
list_vtext = list(vtext)
font_size = 30
font = ImageFont.truetype("arial.ttf", size=font_size)
idraw = ImageDraw.Draw(img)
vtext_result = ""
ytext = 10
for i in list_vtext:
    if idraw.textsize(vtext_result,font=font)[0] < x-(font_size + font_size//2):
        vtext_result = vtext_result + i
    else:
        idraw.text((font_size,ytext), vtext_result, font=font, fill='black')
        if i != " ":
            vtext_result = i
        else:
            vtext_result = ""
        ytext = ytext + font_size
else:
    idraw.text((font_size, ytext), vtext_result, font=font, fill='black')
idraw.rectangle((1,1,x-1,1),fill='blue')
idraw.rectangle((x-1,1,x-1,y-1),fill='blue')
idraw.rectangle((x-1,y-1,1,y-1),fill='blue')
idraw.rectangle((1,1,1,y-1),fill='blue')
img.save('kartinka.png','png')
img.show()
