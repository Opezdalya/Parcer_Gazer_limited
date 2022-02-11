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
    sheet_instance = sheet.get_worksheet(2)
    sheet_instance.insert_rows(items.values.tolist())
def write_to_csv(items) -> None:
    """Функция принимает dataframe с элементами, преобразует их в list и записывает их в google sheet"""
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secrets.json', scope)

    client = gspread.authorize(creds)
    sheet = client.open('сводная наличия и ррц у партнеров online')
    sheet_instance = sheet.get_worksheet(24)
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

    driver = webdriver.Firefox()
    driver.implicitly_wait(0.1)

    try:
        page = last_page = 1
        while page <= last_page:
            url = url_search
            if page > 0:
                url = f'{url_search}&page={page}'

            print(f'Load: {url}')
            driver.get(url)

            for item_el in driver.find_elements_by_css_selector(".ut2-gl__body"):

                name = get_text_by_css(item_el, '.product-title', 'Null').strip('Видеорегистратор').strip(
                    'Блок для подключения к CAN-шине'
                    ).strip(
                        'Кабель питания'
                        ).strip(
                            'ереходная рамка'
                            ).strip(
                    'Мультимедийный видеоинтерфейс'
                    ).strip(
                        'Автомобильный монитор'
                        ).strip(
                    'Электропривод крышки багажника'
                    ).strip(
                        'Адаптер'
                        ).strip(
                            'ля слепых зон'
                            ).strip(
                    'ереходное крепление '
                    ).strip(
                        'Штатное зеркало'
                        ).strip(
                            'LTE'
                            ).strip(
                                'с охранным режимом'
                                ).strip(
                    'с видеорегистратором'
                    ).strip(
                        'Wi-Fi'
                        ).strip(
                            'автозатемнением'
                            ).strip(
                                'заменяемое'
                                ).rstrip(
                    'c GPS, Wi-Fi, LTE'
                    ).strip(
                        ' магнитола'
                        ).lstrip(
                            'PS'
                            ).strip(
                                'утренняя'
                                ).strip(
                                    'USB/SD'
                                    ).strip(
                    'пление к камере заднего вида '
                    ).strip(
                        'Система кругового обзора'
                        ).strip(\
                            '/переднего вида'
                                ).strip(
                    'Парктроник')
                try:
                    price = item_el.find_element_by_css_selector('.ty-price-update img[title]')
                except:
                    price = 0
                try:
                    discount_price = int(price.get_attribute('alt').strip('грн.'))
                except:
                    discount_price = 0

                try:
                    discount_size = int(
                        get_text_by_css(item_el, '.T-sticker.ab-sticker.rounded', '-1').strip('акция%').lstrip(
                            'хит продаж').strip(' ').strip('скидка'))
                except:
                    discount_size = 0

                natural_price_1 = discount_price * (1 - (discount_size * (-1) / 100))
                natural_price = round(natural_price_1)

                try:
                    nal = item_el.find_element_by_css_selector('.ty-qty-out-of-stock')
                    nal = 'Нет в наличии'
                except:
                    nal = 'Есть в наличии'

                row = name, f'{DT.datetime.now():%H:%M_%d-%m-%Y}', '', natural_price, nal
                # natural_price

                items.append(row)

            try:
                last_page = 11
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
    df = pd.DataFrame(items, columns=['Name', "Data", '',    'Price', 'Nal'])
    write_to_csv(df)
    write_to_csv_dont_clear_table(df)


if __name__ == '__main__':
    url = "https://winauto.ua/index.php?match=all&pcode_from_q=y&pshort=y&pfull=y&pname=y&pkeywords=y&search_performed=y&q=gazer&dispatch=products.search&search_id=45281&sort_by=popularity&sort_order=desc&items_per_page=128"
    items = parse(url)
    print(f'Total goods: {len(items)}')

    file_name = f'WinAuto_parser_{DT.datetime.now():%Y-%m-%d}.csv'
    print(f'Saved to {file_name}')
    save_goods(file_name, items)