import json


with open('qr.json') as json_file:
    data = json.load(json_file)
    for pt in data['price_tag']:
        print(pt['qr'])