'''
Author: your name
Date: 2021-02-25 16:33:31
LastEditTime: 2021-02-26 22:50:07
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /Spider/test.py
'''
import os
import json
import time
import numpy as np
import pandas as pd
from collections.abc import Mapping

class File:
    def __init__(self, subject):
        self.name = subject

    def __get__(self, instance, owner):
        return instance.__dict__[self.name]
    
    def __set__(self, instance, value):
        if isinstance(value, str):
            instance.__dict__[self.name] = value
        else:
            raise TypeError

        
class ReadFile:
    rain = File('rain')
    station = File('station')
    south = File('south')
    
    def __init__(self, rain, station, south):
        self.rain = rain
        self.station = station
        self.south = south
    
    @property
    def readrain(self):
        return pd.read_csv(self.rain)
    
    # @property
    # def readrain(self):
    #     if self.rain.endwith('csv'):
    #         return pd.read_csv(self.rain)
    #     else:
    #         return pd.read_excel(self.rain)
    
    @property
    def readstation(self):
        return pd.read_csv(self.station)
    
    @property
    def readsouth(self):
        return pd.read_excel(self.south)
    
    
class SouthWave(ReadFile):
    
    def __init__(self, rain, station, south, month):
        ReadFile.__init__(self, rain, station, south)
        self.month = month
    
    def month_choice(self):
        
        rain = self.readrain
        rain['date'] = pd.to_datetime(rain['date'])
        rain = rain.loc[rain.date.dt.month == self.month]
        rain['date'] = rain['date'].dt.strftime('%Y%m%d')
        rain.set_index('date', inplace=True)
        return rain.to_dict('dict')
    
    def sta_choice(self, rain):
     
        station = self.readstation
        station = [i for i in station.sta_id if i != 56434]
        station = np.array(station, dtype='str')
        rain = {key:value for key, value in rain.items() if key in station}
        return rain
    
    def snow_choice(self, rain):
        snows = []
        for key, value in rain.items():
            if isinstance(value, Mapping):
                val = {str(k):v for k, v in value.items() if v >= 10.}
                if val:
                    snow = {key:val}
                    snows.append(snow)
        return snows
        
    def snow_time(self, snows):
        times = []
        for i, snow in enumerate(snows):
            for key, value in snow.items():
                time = [k for k, v in value.items()]
                times.extend(time)
        return times
    
    def duplicate(self, times):
        time = list(set(times))
        return sorted(time)
        
    def go(self):
        rain = self.month_choice()
        rain = self.sta_choice(rain)
        snows = self.snow_choice(rain)
        times = self.snow_time(snows)
        times = self.duplicate(times)
        return times
   
        
class SouthernTrough(ReadFile):
    def __init__(self, rain, station, south, month):
        ReadFile.__init__(self, rain, station, south)
        self.month = month

    @property
    def readsouth(self):
        df = pd.read_excel(self.south, usecols=[0, 4, 5, 6],
        names=['time', 'lon', 'lat', 'data'])
        return df   
    def month_choice(self):
        south = self.readsouth
        south['time'] = pd.to_datetime(south['time'],
        format='%Y%m%d') 
        south = south.loc[south.time.dt.month == self.month]
        south['time'] = south['time'].dt.strftime('%Y%m%d')
        south.set_index('time', inplace=True)
        return south.to_dict('index')

class IoStorm:
    def __init__(self, file_dir, month):
        self.file_dir = file_dir
        self.month = month

    def obtain_file_path(self):
        sfiles = []
        for root, dirs, files in os.walk(self.file_dir):  
            file = [os.path.join(root, f) for f in files if f.endswith(('.txt', '.dat'))]
            sfiles.append(file)
        return sfiles

    def obtain_datas(self, sfiles):
        files = [file for file in sfiles if file]
       
        datas = []
        for i, values in enumerate(files):
            for index, value in enumerate(values):
                data = pd.read_table(value, header=None, sep=',', 
                usecols=[0, 2, 6, 7], names=['name', 'time', 'lat', 'lon'])
                datas.append(data)
        merge_datas = pd.concat(datas, axis=0)
        return merge_datas
    
    def obtain_times(self, data):
        data['time'] = pd.to_datetime(data['time'],
        format='%Y%m%d%H')
        data = data.loc[data.time.dt.month == self.month]
        data['time'] = data['time'].dt.strftime('%Y%m%d')
        data.drop_duplicates(subset='time',keep='first',inplace=True)
        data.set_index('time', inplace=True)
        return data.to_dict('index')
             
if __name__ == '__main__' :
    
    path = os.getcwd()
    rain_file = os.path.join(path, 'data/rainfall.csv')
    south_file = os.path.join(path, 'data/analysis500.xlsx')
    station_file = os.path.join(path, 'data/sta.dat') 
    
    month = 2    
    southwave = SouthWave(rain_file, station_file, south_file, month)
    times = southwave.go()
    
    southern = SouthernTrough(rain_file, station_file, south_file, month)
    southern_time = southern.month_choice()
    southern_times = [key for key, value in southern_time.items()]

    result = [i for i in times if i in southern_times]
    

    file_dir = 'data/Jtwc/'
    io = IoStorm(file_dir, month)
    sfiles = io.obtain_file_path()
    datas = io.obtain_datas(sfiles)
    datas = io.obtain_times(datas)
    datas_time = [key for key, value in datas.items()]
    # print(len(datas_time))

    result_io = [i for i in times if i in datas_time]

    print(times, len(times), '\n', result, len(result), '\n', result_io, len(result_io))
    # print(result_io)
    # a=1