#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import datetime as DT

from typing import List, Tuple, Union
from pathlib import Path
from selenium.webdriver.common.by import By
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
    sheet_instance = sheet.get_worksheet(0)
    sheet_instance.insert_rows(items.values.tolist())
def write_to_csv(items) -> None:
    """Функция принимает dataframe с элементами, преобразует их в list и записывает их в google sheet"""
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secrets.json', scope)

    client = gspread.authorize(creds)
    sheet = client.open('сводная наличия и ррц у партнеров online')
    sheet_instance = sheet.get_worksheet(39)
    sheet_instance.clear()
    sheet_instance.insert_rows(items.values.tolist())

def parse(url: str) -> List[Tuple[str, str, str]]:
    options = Options()
    options.add_argument('--headless')

    items = []

    driver = webdriver.Firefox(options=options)
    driver.implicitly_wait(0.5)
    try:
        while True:
            print('Load:', url)
            driver.get(url)

            for item_el in driver.find_elements_by_css_selector(".itemRow"):
                name = item_el.find_element_by_css_selector('.name').text

                # Не у всех товаров есть цена
                try:
                    price = float(item_el.find_element_by_css_selector('.price').text.strip('грн.').replace(' ', '').replace(',','.'))
                except NoSuchElementException:
                    price = '-'

                try:nal = item_el.find_element_by_css_selector('.inStock').text
                except NoSuchElementException:
                    nal = item_el.find_element_by_css_selector('.outOfStock').text


                row = name,'',f'{DT.datetime.now():%H:%M_%d-%m-%Y}', price, nal
                print(row)
                items.append(row)

            # Если есть кнопка перехода на следующую страницу, то продолжаем цикл, иначе завершаем
            try:
                a_next_page = driver.find_element(By.XPATH, "//*[@id='catalog']/div[2]/div/ul/li[7]/a ")
                url = a_next_page.get_attribute('href')
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
    df = pd.DataFrame(items, columns=["Data",'Name','', 'Price', 'Nal'])
    write_to_csv(df)
    write_to_csv_dont_clear_table(df)

if __name__ == '__main__':
    url = "https://products.mti.ua/search/index.php?VIEW=TABLE&SORT_TO=90&q=Gazer"
    items = parse(url)
    print(f'Total goods: {len(items)}')

    file_name = f'Parcer_MTI_{DT.datetime.now():%Y-%m-%d}.csv'
    print(f'Saved to {file_name}')
    save_goods(file_name, items)


