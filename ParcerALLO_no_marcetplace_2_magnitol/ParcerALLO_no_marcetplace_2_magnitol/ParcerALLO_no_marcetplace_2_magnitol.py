#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import datetime as DT

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
    sheet_instance = sheet.get_worksheet(5)
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

            for item_el in driver.find_elements_by_css_selector(".product-card"):
                name = item_el.find_element_by_css_selector('.product-card__title').text.strip('Парктронік').strip('Монітор для задніх пасажирів').rstrip('з Android 9.').rstrip('Smart TV').rstrip('Graphite').strip('Професійна втомобільна відеокамера').strip('Антена').strip('- рамка перехідна').strip('2 din').strip('USB').rstrip('Gray').rstrip('Grafit').strip('Відеореєстратор').rstrip('Wi-Fi').strip('Камера заднього виду').strip('Система видеопарковки').strip('Відеокамера внутрішня').strip('Штатна магнітола').strip('Мультимедійний інтерфейс').strip('Мультимедійний центр').strip('Паркувальна камера заднього виду').strip('Зеркало заднего вида')

                # Не у всех товаров есть цена
                try:
                    price = item_el.find_element_by_css_selector('.v-price-box__cur').text
                except NoSuchElementException:
                    price = '-'

                try:nal = item_el.find_element_by_css_selector('.v-price-box__text--out-stock').text
                except NoSuchElementException:
                    nal = "Есть в наличии"


                row = name,f'{DT.datetime.now():%H:%M_%d-%m-%Y}', price, nal
                print(row)
                items.append(row)

            # Если есть кнопка перехода на следующую страницу, то продолжаем цикл, иначе завершаем
            try:
                a_next_page = driver.find_element_by_css_selector('.pagination__next a')
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
    df = pd.DataFrame(items, columns=["Data",'Name', 'Price', 'Nal'])
    df.to_csv(file_name, encoding=encoding, index = False)
    write_to_csv_dont_clear_table(df)


if __name__ == '__main__':
    url = "https://allo.ua/ua/avtozvuk/p-1/proizvoditel-gazer/seller-allo/"
    items = parse(url)
    print(f'Total goods: {len(items)}')

    file_name = f'ALLO_no_marketplace__magnitols_{DT.datetime.now():%Y-%m-%d}.csv'
    print(f'Saved to {file_name}')
    save_goods(file_name, items)

