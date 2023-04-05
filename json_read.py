import json


class ReadJSON:
    """
    класс чтения json файла с нашими ценниками
    """
    def __init__(self, f_path: str = 'd:\\files\\', f_name: str = 'qr.json'):
        with open(f_path + f_name) as json_file:
            self.data = json.load(json_file)



def main():
    i_data = ReadJSON(f_path='d:\\files\\', f_name='qr.json')
    print(i_data.data)


if __name__ == '__main__':
    main()