from csv import DictReader
import qrcode
from os import path, mkdir


def csv_to_qr(filepath):
    export_dir = path.join(path.dirname(path.realpath(__file__)), 'qr_exports')

    if not path.exists(export_dir):
        mkdir(export_dir)

    if path.exists(filepath) and filepath.endswith('.csv'):
        with open(filepath, mode='r', newline='', encoding='utf-8-sig') as f:
            index = 1
            for row in DictReader(f):
                name_data = f'{row["FirstName"]} {row["LastName"]}'
                filename = "{:04d}_{}.png".format(index, name_data)
                
                img = qrcode.make(name_data)
                img.save(path.join(export_dir, filename))

                print(f'Exported: {filename}')

                index += 1