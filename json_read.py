import json


class ReadJSON:
    """
    класс чтения json файла с нашими ценниками
    """
    def __init__(self, f_path: str = 'd:\\files\\', f_name: str = 'qr.json'):
        with open(f_path + '\\' + f_name) as json_file:
            temp_dict = json.load(json_file)
        self.data = sorted(temp_dict['price_tag'], key=lambda x: x['name'])


def main():
    i_data = ReadJSON(f_path='d:\\files\\', f_name='qr.json')
    print(i_data.data)


if __name__ == '__main__':
    main()