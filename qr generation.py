import qrcode

# пример данных
data = "201760115211966"
# имя конечного файла
filename = "qr.png"
# генерируем qr-код
img = qrcode.make(data)
print(img)
# сохраняем img в файл
img.save(filename)