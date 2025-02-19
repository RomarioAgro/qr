import json


class ReadJSON:
    """
    класс чтения json файла с нашими ценниками
    """
    def __init__(self, f_path: str = 'd:\\files\\', f_name: str = 'qr.json'):
        with open(f_path + '\\' + f_name) as json_file:
            temp_dict = json.load(json_file)
        #сортируем наши ценники по имени чтоб при печати они рядом были
        self.data = sorted(temp_dict['price_tag'], key=lambda x: x['name'])

class ReadJSON_QR_KM:
    """
    класс чтения json файла с нашими ценниками
    с УШК или КМ
    """
    def __init__(self, f_path: str = 'd:\\files\\', f_name: str = 'qr.json'):
        with open(f_path + '\\' + f_name) as json_file:
            temp_dict = json.load(json_file)
        self.data = temp_dict
        self.data['price_tag'] = sorted(temp_dict['price_tag'], key=lambda x: x['name'])



def main():
    # i_data = ReadJSON(f_path='d:\\files\\', f_name='qr.json')
    # print(i_data.data)
    i_data = ReadJSON_QR_KM(f_path='d:\\files\\', f_name='qr.json')
    print(i_data.data)

if __name__ == '__main__':
    main()