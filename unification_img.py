from PIL import Image

img = Image.open('kartinka.png')
qr = Image.open('qr.png')
print(img.size)
print(qr.size)
qr_resized = qr.resize((180,180))
total_x = img.size[0] + qr_resized.size[0]
total_y = max(img.size[1],qr_resized.size[1])
print(total_x)
print(total_y)
price_tag = Image.new('RGB', (total_x,total_y), color=('#FFFFFF'))
price_tag.paste(img,(0,0))
price_tag.paste(qr_resized,(img.size[0],0))
price_tag.show()
price_tag.save("rezult.png")