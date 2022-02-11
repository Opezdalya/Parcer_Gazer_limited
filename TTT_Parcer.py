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
def write_to_csv(items) -> None:
    """Функция принимает dataframe с элементами, преобразует их в list и записывает их в google sheet"""
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secrets.json', scope)

    client = gspread.authorize(creds)
    sheet = client.open('сводная наличия и ррц у партнеров online')
    sheet_instance = sheet.get_worksheet(34)
    sheet_instance.clear()
    sheet_instance.insert_rows(items.values.tolist())

def write_to_csv_clear(items) -> None:
    """Функция принимает dataframe с элементами, преобразует их в list и записывает их в google sheet"""
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secrets.json', scope)

    client = gspread.authorize(creds)
    sheet = client.open('Парсер по интернет-магазинам by Boyar.K Зима 2021-2022')
    sheet_instance = sheet.get_worksheet(16)
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
    pages = 24
    driver = webdriver.Firefox(options=options)
    driver.implicitly_wait(0.5)

    try:
        page = last_page = 1
        while page <= last_page:
            pages += 24
            url = url_search
            if page > 1:
                url = f'https://www.ttt.ua/ua/shop/search?text=Gazer&order=hot&user_per_page=24&per_page={pages}'

            print(f'Load: {url}')
            driver.get(url)

            for item_el in driver.find_elements_by_css_selector(".row--vindent-m .slick-track>[class*=col-], .row--vindent-m>[class*=col-]"):
                name = get_text_by_css(item_el, '.product-cut__title', 'Null')
                try:
                    price = item_el.find_element_by_css_selector('.product-price--bg .product-price__item').text
                except:
                    price = get_text_by_css(item_el,'.product-price--bg .product-price__item--has-discount', ' - ')
                try:
                    nal = item_el.find_element_by_class_name('.btn-minor, .btn-minor:active, .btn-minor:focus, .btn-minor:hover')
                    nal = item_el.find_element_by_class_name('.product-snippet__archive')
                    nal = 'Нет в наличии'
                except NoSuchElementException:
                      nal = 'Есть в наличии'
   
                row = f'{DT.datetime.now():%H:%M_%d-%m-%Y}',name, price, nal

                items.append(row)

            # Обновление номера последней страницы
            try:
                last_page = 31

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
    df = pd.DataFrame(items, columns=["Data",'Name', 'Price', 'Nal'])
    write_to_csv_clear(df)


if __name__ == '__main__':
    url = "https://www.ttt.ua/ua/shop/search?text=Gazer&order=hot&user_per_page=24&per_page="
    items = parse(url)
    print(f'Total goods: {len(items)}')

    file_name = f'STYLUS_parser_{DT.datetime.now():%Y-%m-%d}.csv'
    print(f'Saved to {file_name}')
    save_goods(file_name, items)


