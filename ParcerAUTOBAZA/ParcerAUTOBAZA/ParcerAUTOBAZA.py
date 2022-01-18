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
def write_to_csv_dont_clear_table(items) -> None:
    """Функция принимает dataframe с элементами, преобразует их в list и записывает их в google sheet"""
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secrets.json', scope)

    client = gspread.authorize(creds)
    sheet = client.open('Парсер по интернет-магазинам by Boyar.K Зима 2021-2022')
    sheet_instance = sheet.get_worksheet(7)
    sheet_instance.insert_rows(items.values.tolist())
def write_to_csv(items) -> None:
    """Функция принимает dataframe с элементами, преобразует их в list и записывает их в google sheet"""
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secrets.json', scope)

    client = gspread.authorize(creds)
    sheet = client.open('сводная наличия и ррц у партнеров online')
    sheet_instance = sheet.get_worksheet(22)
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
            if page > 0:
                url = f'{url_search}page{page}?text=Gazer'

            print(f'Load: {url}')
            driver.get(url)

            for item_el in driver.find_elements_by_css_selector(".product-view__inner"):
                name = get_text_by_css(item_el, '.product-view-title__link', 'Null').strip('Монітор в підголівник').strip('Штатна магнітола').strip('Дзеркало з монітором').strip('Мультимедіа інтерфейс').strip('го виду').strip('м ').strip('Система кругового огляду').strip('Мультимедіа ресивер').strip('Відеореєстратор')
                price = get_text_by_css(item_el, '.product-view-prices__base-price-number', '-')
                nal = get_text_by_css(item_el, '.product-view-description__status', '-')

                row = name,f'{DT.datetime.now():%H:%M_%d-%m-%Y}','', price, nal
                print(row)

                items.append(row)

            # Обновление номера последней страницы
            try:
                last_page = 58
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
    url = "https://avtozvuk.ua/ua/search/"
    items = parse(url)
    print(f'Total goods: {len(items)}')

    file_name = f'AUTOZVUK_parser_{DT.datetime.now():%Y-%m-%d}.csv'
    print(f'Saved to {file_name}')
    save_goods(file_name, items)
