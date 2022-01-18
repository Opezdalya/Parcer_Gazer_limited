#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import datetime as DT
import time

from typing import List, Tuple, Union
from pathlib import Path

# pip install pandas
import pandas as pd
from selenium.webdriver.common.by import By
# pip install selenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
import gspread
from oauth2client.service_account import ServiceAccountCredentials
def write_to_csv_dont_clear_table(items) -> None:
    """Функция принимает dataframe с элементами, преобразует их в list и записывает их в google sheet"""
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secrets.json', scope)

    client = gspread.authorize(creds)
    sheet = client.open('Парсер по интернет-магазинам by Boyar.K Зима 2021-2022')
    sheet_instance = sheet.get_worksheet(1)
    sheet_instance.insert_rows(items.values.tolist())
def write_to_csv(items) -> None:
    """Функция принимает dataframe с элементами, преобразует их в list и записывает их в google sheet"""
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secrets.json', scope)

    client = gspread.authorize(creds)
    sheet = client.open('сводная наличия и ррц у партнеров online')
    sheet_instance = sheet.get_worksheet(20)
    sheet_instance.clear()
    sheet_instance.insert_rows(items.values.tolist())


def get_text_by_css(parent, css_selector: str, default: str) -> str:
    try:
        return parent.find_element_by_css_selector(css_selector).text
    except:
        return default


def parse(url_search: str) -> List[Tuple[str, str, str]]:
    options = Options()
    options.add_argument('--headless')

    items = []

    driver = webdriver.Firefox(options=options)
    driver.implicitly_wait(0.1)

    try:
  
        page = last_page = 1
        while page <= last_page:
            url = url_search
            if page > 1:
                url = f'{url_search}?PAGEN_1={page}'

            print(f'Load: {url}')
            driver.get(url)

            for item_el in driver.find_elements_by_css_selector(".card[_ngcontent-serverApp-c94]"):
                name = get_text_by_css(item_el, '.em-styles b', 'Null')
                price = get_text_by_css(item_el, '.card__price-sum[_ngcontent-serverApp-c94]', '-')
                nal = get_text_by_css(item_el, '.card__availability-status[_ngcontent-serverApp-c94]', 'Есть в наличии')
               
                row = name,f'{DT.datetime.now():%H:%M_%d-%m-%Y}','', price, nal
                print(row)

                items.append(row)

            # Обновление номера последней страницы
            try:
               last_page = 36

            except NoSuchElementException:
                break

            page += 1

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
     write_to_csv_dont_clear_table(df)

if __name__ == '__main__':
    url = "https://epicentrk.ua/ua/shop/avtomagnitoly/fs/brand-gazer/"
    items = parse(url)
    print(f'Total goods: {len(items)}')

    file_name = f'Epicentr_parser_{DT.datetime.now():%Y-%m-%d}.csv'
    print(f'Saved to {file_name}')
    save_goods(file_name, items)