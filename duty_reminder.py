import telepot
from telepot.loop import *
from telepot.namedtuple import *
from datetime import *
import pandas as pd
from collections import *
from config import *


bot = telepot.Bot(dev_token)
public_hol = [date(2018, 8, 9), date(2018, 8 , 22), date(2018, 11, 6),
              date(2018, 12, 25)]

class Duty_cal():
    def __init__(self, year=None, month=None, filename=None):
        self.year = year
        self.month = month
        self.filename = filename
        self.cal = None
        self.holiday = public_hol

    # Methods to retrieve attributes
    def get_month(self):
        month_dict = {'Jan': 1, 'Feb': 2, 'Mar':3,
                     'Apr': 4, 'May': 5, 'Jun':6,
                     'Jul': 7, 'Aug': 8, 'Sep': 9,
                     'Oct': 10, 'Nov': 11, 'Dec': 12}
        return (self.month, month_dict[self.month])
    
    def get_filename(self):
        return self.filename
    
    def get_year(self):
        return self.year
    
    def get_cal(self):
        return self.cal

    # Methods to generate duty calendar
    def start(self):
        # Initialization, creates new empty calendar and fill with duty list
        yes = ('y','Y')
        no = ('N','n')
        while True:
            print('Importing schedule to bot.\n Leave fields blank for default values.')
            year = input('Enter the year (YYYY) [Default: Current Year]: ')
            month = input('Enter the month to import (e.g. Aug): ') #assuming sheet name is abbreviated month
            filename = input('Enter the filename: ') #Assume file in same directory as script
            
            if not month:
                month = datetime.today().strftime('%b')
            if not filename:
                filename = duty_filename
            if not year:
                year = datetime.today().year
                
            print('Importing sheet ', month, 'from:\n',  filename)
            check = input('Is the information correct? (Y/N):')
            if check in yes:
                break
                
        self.month = month
        self.filename = filename
        self.year = int(year)
        
        self.cal = self.empty_sem() #Generate empty calendar
        self.fill_cal() #Fill calendar

    def update_cal(self):
        self.start()
    
    def read_roster(self):
        #reads and extracts duty rows
        filename = self.get_filename()
        month_str, month_int = self.get_month()
        dfs = pd.read_excel(filename, sheet_name=month_str,index_col=None, na_values=['NA']) #read excel
        roster = dfs.values[5:20] #Duty rows
        
        duty_num = len(list(roster[0])[1:-5]) #Gets the total number of duties in the month
        consolidate = [] 
        for i in range(duty_num): #Create empty list with equivalent number of None elements as duties
            consolidate.append(None)
            
        for ra in roster: #reads duty list and input name by order of duty date
            ra_duty = list(ra)
            name = ra_duty[0]
            duty_list = ra_duty[1:-3]
            for i, key in enumerate(duty_list):
                if key == 'CD':
                    consolidate[i]=name
        return consolidate

    def fill_cal(self):
        #Fills calendar entries with duty RA names
        duty_list = self.read_roster()
        month_str, month_int = self.get_month()
        cal = self.cal
        year = self.get_year()
        
        counter = 0 #counter to cycle through consolidated duty list
        cal_month = cal[month_str]
        
        for dates in cal_month:
            if len(cal_month[dates]) == 1:
                self.insert_name(dates, duty_list[counter])
                counter += 1
            elif len(cal_month[dates]) == 2:
                self.insert_name(dates, duty_list[counter])
                self.insert_name(dates, duty_list[(counter+1)])
                counter += 2
                

    def empty_sem(self):
        #generate empty dictionary calendar
        year = self.get_year()
        result = OrderedDict()
        listdate = date(year, 1, 1)
        mth = listdate.strftime('%b')
        yr = listdate.year

        while yr == year: #Empty calendar starts from 1st Jan to 31st Dec
            if mth not in result: 
                result[mth] = OrderedDict() #Empty ordered dictionary
            else:
                str_day = listdate.strftime('%A %d %b %Y') #Gets date string e.g. Monday 6 Aug 2018 PM
                if ('Saturday' in str_day) or ('Sunday' in str_day) or (listdate in self.holiday):
                    result[mth][str_day] = {'AM':{},'PM':{}}
                else:
                    result[mth][str_day] = {'PM':{}}
                listdate += timedelta(days=1)
            mth = listdate.strftime('%b')
            yr = listdate.year
        return result

    def insert_name(self,cal_date,name):
        #inserts name in duty slot
        cal = self.get_cal()
        month_str, month_int = self.get_month()
        
        duty = cal[month_str][cal_date]
        if len(duty) == 1: #single duty day
            duty['PM'] = name
        else:
            if duty['AM']: # AM slot filled, fill PM slot
                duty['PM'] = name
            else:
                duty['AM'] = name # Fill AM slot
            
    def swap_duty(self,person1, person2):
        
        pass

    def alert_duty(self):
        todate = datetime.today().strftime('%A %d %b %Y')
        tomonth = datetime.today().strftime('%b')
        dutycal = self.get_cal()
        duty = dutycal[tomonth][todate]
        
        for shift in duty:
            name = duty[shift]
            chat_id = str(ra_list['Wei Song'])
            bot.sendMessage(chat_id, 'Hola mi amigo! {},\nYou have {} duty today ({})'.format(name, shift,todate))





