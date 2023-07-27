import csv
import time

class Ecsv():
    def __init__(self, fieldnames):
        self.fieldnames = fieldnames
        self.timestr = time.strftime("%Y%m%d-%H%M%S")
        self.filename = './output'+ self.timestr +'.csv'

        with open(self.filename, 'w', encoding='UTF8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames, delimiter=';')
            writer.writeheader()

    def save_row(self, row):
        with open(self.filename, 'a', encoding='UTF8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames, delimiter=';')
            writer.writerow(row)

    def save_rows(self, data):
        with open(self.filename, 'a', encoding='UTF8', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerows(data)
            
    def read(self):
        pass
