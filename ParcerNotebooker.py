#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import datetime as DT
import time

from typing import List, Tuple, Union
from pathlib import Path

# pip install pandas
import pandas as pd

# pip install selenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException

import gspread
from oauth2client.service_account import ServiceAccountCredentials

def write_to_csv_clear(items) -> None:
    """Функция принимает dataframe с элементами, преобразует их в list и записывает их в google sheet"""
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secrets.json', scope)

    client = gspread.authorize(creds)
    sheet = client.open('Парсер по интернет-магазинам by Boyar.K Зима 2021-2022')
    sheet_instance = sheet.get_worksheet(11)
    sheet_instance.insert_rows(items.values.tolist())

def write_to_csv(items) -> None:
    """Функция принимает dataframe с элементами, преобразует их в list и записывает их в google sheet"""
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secrets.json', scope)

    client = gspread.authorize(creds)
    sheet = client.open('сводная наличия и ррц у партнеров online')
    sheet_instance = sheet.get_worksheet(26)
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
    driver.implicitly_wait(5.5)

    try:
        page = last_page = 1
        while page <= last_page:
            url = url_search
            if page > 1:
                url = f'{url_search}&PAGEN_1={page}'

            print(f'Load: {url}')
            driver.get(url)

            for item_el in driver.find_elements_by_css_selector("#catalogColumn .product"):
                name = get_text_by_css(item_el, '.name', 'Null').strip('Електропривод багажника').strip('Автомобільна мультимедійна система')
                price = get_text_by_css(item_el, '.price', '-')
                nal = get_text_by_css(item_el, '', 'Есть в наличии')

                row = name,f'{DT.datetime.now():%H:%M_%d-%m-%Y}','', price, nal

                items.append(row)

            # Обновление номера последней страницы
            try:
               last_page = 14

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
     write_to_csv_clear(df)

if __name__ == '__main__':
    url = "https://notebooker.ua/search/?q=Gazer&send=Y&r=Y"
    items = parse(url)
    print(f'Total goods: {len(items)}')

    file_name = f'Notebooker_parser_{DT.datetime.now():%Y-%m-%d}.csv'
    print(f'Saved to {file_name}')
    save_goods(file_name, items)
