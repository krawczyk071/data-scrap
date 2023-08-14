import csv
import time
import json
from typing import List

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

class Ejson():
    def __init__(self,mode='w',filename='test.json'):
        self.filename = filename

    def save_data(self,datadict):
        # extract data to json file
        with open(self.filename, 'w',newline='',encoding='utf-8') as jsonfile:
            json.dump(datadict, jsonfile) # commnad write json data to file
            
class Esql():
    def __init__(self,mode='w',filename='test.json'):
        self.filename = filename

class Etxt():
    def __init__(self,mode='w',filename=None):
        self.filename = filename
        if mode == 'w':
            self.create(filename)
        elif mode == 'r':
            if not filename:
                raise('You need to provide filename')
            self.read(filename)

    def create(self, filename=None):
        self.timestr = time.strftime("%Y%m%d-%H%M%S")
        if not filename:
            self.filename = './output'+ self.timestr +'.txt'
        else:
            self.filename = filename

        with open(self.filename, 'w', encoding='UTF8', newline='\n') as f:
            pass

    def save_row(self, row:str):
        with open(self.filename, 'a', encoding='UTF8', newline='\n') as f:
            f.write(row + "\n")

    def save_rows(self, data:List[str]):
        with open(self.filename, 'a', encoding='UTF8', newline='\n') as f:
            for string in data:
                f.write(string+ + "\n")
            
    def read(self,filename):        
        with open(filename, mode='r', encoding='UTF8') as f:
            lines = f.readlines()
            cnt=0
            self.rows = []
            for row in lines:
                cnt+=1
                self.rows.append(row)
            