#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import datetime as DT

from typing import List, Tuple, Union
from pathlib import Path
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
# pip install pandas
import pandas as pd

# pip install selenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
import time

import gspread
from oauth2client.service_account import ServiceAccountCredentials
def write_to_csv_clear(items) -> None:
    """Функция принимает dataframe с элементами, преобразует их в list и записывает их в google sheet"""
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secrets.json', scope)

    client = gspread.authorize(creds)
    sheet = client.open('Парсер по интернет-магазинам by Boyar.K Зима 2021-2022')
    sheet_instance = sheet.get_worksheet(12)
    sheet_instance.insert_rows(items.values.tolist())
def write_to_csv(items) -> None:
    """Функция принимает dataframe с элементами, преобразует их в list и записывает их в google sheet"""
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secrets.json', scope)

    client = gspread.authorize(creds)
    sheet = client.open('сводная наличия и ррц у партнеров online')
    sheet_instance = sheet.get_worksheet(32)
    sheet_instance.clear()
    sheet_instance.insert_rows(items.values.tolist())


def parse(url: str) -> List[Tuple[str, str, str]]:
    options = Options()
    

    items = []
    
    driver = webdriver.Firefox(options=options)
    driver.implicitly_wait(0.5)
    i = 1
  
    print('Load:', url)
    driver.get(url)
   
    try:
        while i <= 21:
            i += 1
            time.sleep(2)

            if driver.find_element(By.XPATH,'//*[@id="bingc-active-close-button"]').is_displayed():
                 time.sleep(15)
                 driver.find_element(By.XPATH,'//*[@id="bingc-active-close-button"]').click()
            
            
            for item_el in driver.find_elements_by_css_selector(".col-cell-3.middle, .col-inline-xs-3.middle"):
                

                try:name = item_el.find_element_by_css_selector('.product-micro-title a').text
                except NoSuchElementException:name = ''

                # Не у всех товаров есть цена
                try:
                    price = item_el.find_element_by_css_selector('.product-micro-price').text
                except NoSuchElementException:
                    price = '-'
                try: nal = item_el.find_element_by_css_selector('.product-status').text
                except: nal = 'Нет в наличии'
                
                    
                row = name,f'{DT.datetime.now():%H:%M_%d-%m-%Y}','', price, nal
                items.append(row)

            

            try:
                
                a_next_page = driver.find_element_by_class_name('pagination')
                a_next_page.click()
                time.sleep(1) 

            except NoSuchElementException:
                break

            
    finally:
        driver.quit()

    return items


def save_goods(
        file_name: Union[str, Path],
        items: List[Tuple[str, str, str]],
        encoding='utf-8'
):
     df = pd.DataFrame(items, columns=['Name',"Data",'', 'Price', 'Nal'])
     write_to_csv(df)
     write_to_csv_clear(df)
if __name__ == '__main__':
    url = "https://atl.ua/search?q=Gazer"
    items = parse(url)
    print(f'Total goods: {len(items)}')

    file_name = f'ATL_Parcer{DT.datetime.now():%Y-%m-%d}.csv'
    print(f'Saved to {file_name}')
    save_goods(file_name, items)
