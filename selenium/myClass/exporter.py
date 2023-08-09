import csv
import time

class Ecsv():
    def __init__(self,mode='w',fieldnames=None,filename=None):
        if mode == 'w':
            if not fieldnames:
                raise('You need to provide fieldnames')
            self.create(fieldnames,filename)
        elif mode == 'r':
            if not filename:
                raise('You need to provide filename')
            self.read(filename)


    def create(self, fieldnames,filename=None):
        self.fieldnames = fieldnames
        self.timestr = time.strftime("%Y%m%d-%H%M%S")
        if not filename:
            self.filename = './output'+ self.timestr +'.csv'
        else:
            self.filename = filename

        with open(self.filename, 'w', encoding='UTF8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames, delimiter=';')
            writer.writeheader()


    def save_row(self, row:dict):
        with open(self.filename, 'a', encoding='UTF8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames, delimiter=';')
            writer.writerow(row)

    def save_rows(self, data):
        with open(self.filename, 'a', encoding='UTF8', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerows(data)
            
    def read(self,filename):        
        with open(filename, mode='r', encoding='UTF8') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=';')
            cnt=0
            self.rows = []
            for row in csv_reader:
                # if cnt == 0:
                #     self.fieldnames = row
                # else:
                #     self.rows.append(row)
                cnt+=1
                self.rows.append(row)

