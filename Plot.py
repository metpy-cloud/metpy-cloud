'''
Author: your name
Date: 2021-03-01 18:07:43
LastEditTime: 2021-03-01 21:37:28
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /South/Plot.py
'''
import os
import re
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

import snow 


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
    hf_data = File('hf_data')
    file_dir = File('file_dir')
    ec_data = File('ec_data')

    
    def __init__(self, hf_data, file_dir, ec_data):
        self.hf_data = hf_data
        self.file_dir = file_dir
        self.ec_data = ec_data
        

    def read_hf5(self):
        try:
            with xr.open_dataset(self.hf_data) as hf:
                data = {key : value for key, value in hf.items()}
                return data
        except IOError:
            print('Cannot open %s for readint.' %self.ec_data)
            raise

    def obtain_file_path(self):
        sfiles = []
        for root, dirs, files in os.walk(self.file_dir):  
            file = [os.path.join(root, f) for f in files if f.endswith('.nc')]
            sfiles.append(file)
        return sfiles

    @property
    def read_ecdata(self):
        return xr.open_dataset(self.ec_data)
       
    def select_data(self, data, time):
        pass


class Plot(ReadFile):
    shape = File('shape')
    
    def __init__(self, hf_data, file_dir, ec_data, shape):
        super().__init__(hf_data, file_dir, ec_data)
        self.shape = shape
    
    @property
    def read_data(self):
        return xr.open_dataset(self.ec_data)

    def draw_map(self):
        fig, ax = plt.subplots(figsize=(6, 4.5), dpi=300, subplot_kw=dict(projection=ccrs.PlateCarree()))
        ax.set_extent([50, 130, 5, 55], crs=ccrs.PlateCarree())
        
        ax.add_geometries(Reader(self.shape).geometries(), ccrs.PlateCarree(), facecolor='none', edgecolor='k', linewidth=0.2)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.2)
        ax.add_feature(cfeature.LAKES.with_scale('50m'))
        
        ax.xaxis.set_major_formatter(LongitudeFormatter())
        ax.yaxis.set_major_formatter(LatitudeFormatter())
        ax.set_xticks(np.arange(50, 131, 20), crs=ccrs.PlateCarree())
        ax.set_yticks(np.arange(5, 56, 10), crs=ccrs.PlateCarree())
        return fig, ax

    def plot_contour(self, times):
        years = []
        for i, time in enumerate(times):
            year = re.findall('[\d]{4}', time)[0]
            years.append(year)

        years = list(set(years))
        for i, year in enumerate(years):
            for i, data_time in enumerate(times):
                if re.findall('[\d]{4}', data_time)[0] == str(year):
                    file_name = str(year) + '.uvh.1.5.nc'
                    file_path = os.path.join(self.file_dir, file_name)
                    try:
                        data = xr.open_dataset(file_path)

                        X = data['longitude'][()]
                        Y = data['latitude'][()]
                        Uwnd = data['u'][()]
                        Vwnd = data['v'][()]

                        U = Uwnd.sel(level=500, time=data_time)
                        V = Vwnd.sel(level=500, time=data_time)
                        # print(U, V)
                
                        fig, ax = self.draw_map()
                        plot1 = plt.quiver(X, Y, U, V, width=0.0012, scale=600, pivot='mid', transform=ccrs.PlateCarree())
                        plot2 = plt.quiverkey(plot1, 0.95, 0.9, 20, '20m/s', fontproperties={'size': 8})
                        ax.add_patch(plt.Rectangle((122, 48), 8, 7, facecolor='white', edgecolor='black', zorder=1))
                        plt.title(data_time)
                        # plt.tight_layout()
                        plt.savefig('fig\\November\\' + data_time + '.png', dpi=300)
                        plt.close()
                    except IOError:
                        print('Cannot open file!')
                    # plt.show()
            else:
                print('Data_Time not in times!')
        print('Successfully!')
    

if __name__ == '__main__' :
    
    path = os.getcwd()
    file_dir = os.path.join(path, 'ec_data\\')

    ec_data = os.path.join(path, 'data\\1979.uvh.1.5.nc')
    hf_data = os.path.join(path, 'data\\Mean.hdf5')
    shape = os.path.join(path, 'shape\\cnhimap.shp')
    
    rain_file = os.path.join(path, 'data\\rainfall.csv')
    south_file = os.path.join(path, 'data\\analysis500.xlsx')
    station_file = os.path.join(path, 'data\\sta.dat') 
    
    month = 11    
    southwave = snow.SouthWave(rain_file, station_file, south_file, month)
    times = southwave.go()
    # print(times)
    
    plot = Plot(hf_data, file_dir, ec_data, shape)
    plot.plot_contour(times)
  