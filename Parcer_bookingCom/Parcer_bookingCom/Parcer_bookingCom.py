from selenium import webdriver
import bs4
import time
from selenium.webdriver.chrome.options import Options
import requests
import xlsxwriter

URL = "https://www.google.com/travel/hotels/%D0%A3%D0%BA%D1%80%D0%B0%D0%B8%D0%BD%D0%B0?g2lb=4596364%2C4597339%2C4258168%2C4371335%2C4317915%2C4401769%2C4640247%2C4270442%2C4306835%2C26481799%2C4624411%2C2503771%2C4419364%2C4641139%2C4515404%2C4605861%2C2503781%2C2502548%2C4659203%2C4291517%2C4270859%2C4284970&hl=ru-UA&gl=ua&cs=1&ssta=1&ap=EgAwA2gB&q=%D0%9E%D1%82%D0%B5%D0%BB%D0%B8%20%D0%A3%D0%BA%D1%80%D0%B0%D0%B8%D0%BD%D1%8B&rp=EO3vjoP4lLOdAhDTsbPF-fPdrzAQpZyaoPSHs6ysARCQt6aCjOPDgckBOAFAAEgCogEO0KPQutGA0LDQuNC90LA&ictx=1&sa=X&utm_campaign=sharing&utm_medium=link&utm_source=htls&ts=CAESCgoCCAMKAggDEAAaMgoUEhA6DtCj0LrRgNCw0LjQvdCwGgASGhIUCgcI5Q8QCxgQEgcI5Q8QCxgRGAEyAhAAKgsKBygBOgNVQUgaAA&ved=0CAAQ5JsGahgKEwjIpNTMgYH0AhUAAAAAHQAAAAAQjAQ"
LINK = "https://www.google.com/travel/hotels/Украина"
driver = webdriver.Chrome()
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
data = []


def parse(number_of_pages,sleep):
    driver = webdriver.Chrome()
    driver.get(URL)
    for i in range(number_of_pages):
        time.sleep(sleep)
        soup = bs4.BeautifulSoup(driver.page_source, features='lxml')
        all_links = soup.find_all("a", class_='r2Avjb uVGdUc')
        for i in all_links:
            r = requests.get(LINK + i['data-href'])
            soup = bs4.BeautifulSoup(r.text, features='lxml')
            time.sleep(sleep)
            try:
                name = soup.find('h1', class_='fZscne').text
                price = soup.find('span', class_='qQOQpe prxS3d').text
                number = soup.find('span', class_='CFH2De').next.next.next.next.next.next.next.next
                place = soup.find('span', class_='CFH2De').next.next.next.next
                try:
                    number = number.text
                except:
                    pass
                try:
                    place = place.text
                except:
                    pass
                data.append(
                {
                    "name": name,
                    "price": price,
                    "number": number,
                    "place": place,
                    "url":LINK+i['data-href']
                })
            except:
                continue
            print (f'Имя: {name}',f'Цена: {price}',f'Номер телефона: {number}',f'Адрес: {place}')
        driver.execute_script("window.scrollTo(0, 5000)")
        time.sleep(sleep)
        try:
            element = driver.find_element_by_xpath("//span[text()='Далее']")
            element.click()
        except: break





def data_in_csv(data):
    workbook = xlsxwriter.Workbook('ParcerOtelei.xlsx')
    worksheet = workbook.add_worksheet()
    row = 0
    col = 0

    for item in data:
        if item['number'] == '':
            continue
        worksheet.write(row, col, item['name'])
        worksheet.write(row, col + 1, item['price'])
        worksheet.write(row, col + 2, item['number'])
        worksheet.write(row, col + 3, item['place'])
        worksheet.write(row, col + 4, item['url'])
        row += 1

    workbook.close()
    print (f'Информация сохранена в {workbook}')


if __name__ == '__main__':
    parse(200,sleep=2) # Сколько страниц спарсить и время ожидания при каком-то действии
    data_in_csv(data=data)


