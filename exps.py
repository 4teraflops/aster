import os
import requests
import sys
import itertools
from datetime import datetime
import time
import pickle
from selenium import webdriver
from threading import Thread
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# задаем параметры вебдрайверу
driverPath = os.getcwd() + os.sep + 'chromedriver'  # Chrome Driver Directory
chromeOptions = Options()
# chromeOptions.add_argument('--headless')  # скрывать окна хрома
chromeOptions.add_argument('--no-sandbox')
chromeOptions.add_argument('--disable-dev-shm-usage')
# chromeOptions.add_argument("start-maximized") # на весь экран
driver = webdriver.Chrome(driverPath, chrome_options=chromeOptions)
driver.implicitly_wait(3)  # неявное ожидание драйвера
wait = WebDriverWait(driver, 3)  # Задал переменную, чтоб настроить явное ожидание элемента (сек)
aut_url = 'http://supporthelp:qwerty@voip.bisys.ru/queue-stats/index.php'
url = 'http://voip.bisys.ru/queue-stats/index.php'
dict_daily_calls = {}
all_calls = {}


def user_input():
    try:
        d1 = int(input('Введи с какого числа нужна стата (формат - DD): '))
        d2 = int(input('Введи по какое число нужна стата (формат - DD): '))
        m = int(input('Введи номер месяца: '))
        period = d2 - d1
        print(period)
        if period == 0:
            print('Погнали.')
            open_daily_distribution(d1, d2, m)
        elif period < 0:
            print(f'Не получится собрать стату с {d2} числа по {d1} число!')
        elif period > 0:
            print(f'Запрошена стата за {period} дней.. Поехали.')
            d2 += 1
            days = [i for i in range(d1, d2)]
            print(days)
    except TimeoutException:
        print('Не, ну если ты не хочешь вводить, то я завершаюсь.')


def get_daily_distribution_stat():
    print('Собираю стату за день...')
    hours = [i for i in range(1, 24)]  # создал кортеж от 1 до 23
    for h in hours:
        hour_element = wait.until(EC.presence_of_element_located((By.XPATH, f'//*[@id="table2"]/tbody/tr[{h}]/td[1]')))
        hour = int(hour_element.get_attribute('innerHTML'))
        accept_calls_element = wait.until(EC.presence_of_element_located((By.XPATH, f'//*[@id="table2"]/tbody/tr[{h}]/td[2]')))
        accept_calls = accept_calls_element.get_attribute('innerHTML')
        miss_calls_element = wait.until(EC.presence_of_element_located((By.XPATH, f'//*[@id="table2"]/tbody/tr[{h}]/td[4]')))
        miss_calls = miss_calls_element.get_attribute('innerHTML')
        dict_daily_calls[hour] = (int(accept_calls) + int(miss_calls))
    print('ok')


def open_daily_distribution(d1, d2, m):
    driver.get(aut_url)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="left"]/table/tbody/tr/td[2]/a[3]'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="left"]/table/tbody/tr/td[2]/a[3]'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '// *[ @ id = "right"] / table / tbody / tr / td[2] / a[3]'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="rest"]/table/tbody/tr[1]/td[2]/select[2]/option[{d1}]'))).click()  # ищем форму для ввода дня
    wait.until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="rest"]/table/tbody/tr[1]/td[2]/select[3]/option[{m}]'))).click()  # и все остальное
    wait.until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="rest"]/table/tbody/tr[2]/td[2]/select[2]/option[{d2}]'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="rest"]/table/tbody/tr[2]/td[2]/select[3]/option[{m}]'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="rest"]/input'))).click()
    print('ok')
    print('Перехожу в распределения звонков...')
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="primary"]/li[7]/a'))).click()
    print('ok')
    get_daily_distribution_stat()


if __name__ == '__main__':
    try:
        user_input()
    except(KeyboardInterrupt, SystemExit):
        print('\nПрограмма остановлена.')
