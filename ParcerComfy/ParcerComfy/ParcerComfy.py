#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
__author__ = 'ipetrash'
 
 
import datetime as DT
import time
 
from typing import List, Tuple, Union
from pathlib import Path
from datetime import datetime
# pip install pandas
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# pip install selenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
 
 
# TODO: Using logging instead print
# TODO: price must be decimal
 
 
def parse(url: str) -> List[Tuple[str, str, str]]:
    options = Options()
    # NOTE: на сайте была замечена капча, обойти ее сложно будет
    #       проще будет руками ее проходить, когда она возникнет
    # options.add_argument('--headless')
 
    items = []
    PROXY = '146.120.160.148	'
    driver = webdriver.Firefox(options=options)
    Firefox_options = webdriver.FirefoxOptions()
    Firefox_options.add_argument('--proxy-server=%s' % PROXY)
    cur_date = datetime.now().strftime("%d_%m_%Y")
    wait = WebDriverWait(driver, timeout=10)
 
    # Сайт замусорен и очень долго прогружается из-за различных ненужных запросов
    # Поэтому добавим ограничение, чтобы на driver.get не ждать несколько минут, тем
    # более товары уже присутствуют
    driver.set_page_load_timeout(10)
 
    try:
        while True:
            print('Load:', url)
            try:
                driver.get(url)
            except TimeoutException:
                print('Страница слишком долго грузится, парсим дальше, не дожидаясь окончания!')
 
            # Если наткнулись на капчу
            # TODO: использовать более явный способ определения капчи
            while True:
                try:
                    driver.find_element_by_css_selector("#main-iframe")
                    print('[!] Обнаружена капча!')
                    time.sleep(5)
                except NoSuchElementException:
                    break
 
            # Пробуем получить элементы
            while True:
                try:
                    # Добавляем в селекторе ограничение на data-product-url, чтобы не зацепить пустой элемент
                    items_el = wait.until(
                        EC.visibility_of_any_elements_located(
                            (By.CSS_SELECTOR, ".product-item[data-product-url]")
                        )
                    )
                    break
                except TimeoutException:
                    pass
 
            print(f'Найдено элементов: {len(items_el)}')
 
            for item_el in items_el:
                # print(item_el.get_attribute('outerHTML'))
                name = item_el.find_element_by_css_selector('.product-item__name').text
                price = item_el.find_element_by_css_selector('.price-box__content-i > .price-value').text
                try: nal = item_el.find_element_by_css_selector('t-item.out-of-stock-item').text
               
                except: nal = ('Есть в наличии ')
 
                print(name, price, nal)
                items.append((cur_date, name, price, nal))
 
            # У сайт два элемента для пагинации, оба имеют одинаковые поисковые атрибуты, причем
            # первый скрытый, поэтому недоступен для взаимодействия
            try:
                a_next_page_els = WebDriverWait(driver, timeout=2).until(
                    EC.visibility_of_any_elements_located(
                        (By.CSS_SELECTOR, '.pager__number_next:not(.disabled) > a[href]')
                    )
                )
                if not a_next_page_els:
                    break
            
            except TimeoutException:
                break
 
            a_next_page = a_next_page_els[0]
            url = a_next_page.get_attribute('href')
 
    finally:
        driver.quit()
 
    return items
 
 
def save_goods(
        file_name: Union[str, Path],
        items: List[Tuple[str, str, str]],
        encoding='utf-8'
):
    df = pd.DataFrame(items, columns=['cur_date', 'Name', 'Price', 'Nal'])
    df.to_csv(file_name, encoding=encoding)
 
 
if __name__ == '__main__':
    url = "https://comfy.ua/ua/catalogsearch/result/index/?q=+Gazer&search_provider=anyquery&strategy=vectors%2Czero_queries_predictor"
    url = "https://comfy.ua/ua/catalogsearch/result/index/?p=8&q=+Gazer&search_provider=anyquery&strategy=vectors%2Czero_queries_predictor"
    items = parse(url)
    print(f'Total goods: {len(items)}')
 
    file_name = f'comfy_parser_{DT.datetime.now():%Y-%m-%d}.csv'
    print(f'Saved to {file_name}')
    save_goods(file_name, items)