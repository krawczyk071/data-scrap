import csv
import time


class Csv_export():
    timestr = time.strftime("%Y%m%d-%H%M%S")

    def create_csv(fieldnames):

        timestr = time.strftime("%Y%m%d-%H%M%S")
        filename = './output'+timestr+'.csv'

        with open(filename, 'w', encoding='UTF8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
        return filename

    def save_csv(filename, fieldnames, row):
        with open(filename, 'a', encoding='UTF8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
            writer.writerow(row)

    def export_csv(name, data):

        timestr = time.strftime("%Y%m%d-%H%M%S")
        filename = './'+name+timestr+'.csv'

        with open(filename, 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerows(data)
        return filename
