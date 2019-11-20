import os
import csv
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# задаем параметры вебдрайверу
driverPath = os.getcwd() + os.sep + 'chromedriver'  # Chrome Driver Directory
chromeOptions = Options()
chromeOptions.add_argument('--headless')  # скрывать окна хрома
chromeOptions.add_argument('--no-sandbox')
chromeOptions.add_argument('--disable-dev-shm-usage')
# chromeOptions.add_argument("start-maximized") # на весь экран
# представляем глобальные переменные
aut_url = 'http://supporthelp:qwerty@voip.bisys.ru/queue-stats/index.php'
url = 'http://voip.bisys.ru/queue-stats/index.php'
all_calls = {}
path = 'output.csv'  # Путь то выходного файла


def user_input():

    d1 = int(input('Введи с какого числа нужна стата (формат - DD): '))
    d2 = int(input('Введи по какое число нужна стата (формат - DD): '))
    m = int(input('Введи номер месяца: '))
    period = d2 - d1
    if period == 0:
        print('Погнали.')
        open_daily_distribution(d1, d2, m, d2)
    elif period < 0:
        print(f'Не получится собрать стату с {d2} числа по {d1} число!')
    elif period > 0:# если несколько дней, то собираем словарь с кортежем в значении (ключ - дата)
        d2 += 1
        days = [i for i in range(d1, d2)]# сделал кортеж из диапазона дат
        print(f'Запрошена стата за {len(days)} дней.. Поехали.')
        for day in days:
            open_daily_distribution(day, day, m, day)#итерация по функции за каждый день из диапазона


def open_daily_distribution(d1, d2, m, day):

    print('Открываю стату за день...', end='')
    driver = webdriver.Chrome(driverPath, chrome_options=chromeOptions)
    driver.implicitly_wait(3)  # неявное ожидание драйвера
    wait = WebDriverWait(driver, 3)  # Задал переменную, чтоб настроить явное ожидание элемента (сек)
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
    print('Перехожу в распределения звонков...', end='')
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="primary"]/li[7]/a'))).click()
    print('ok')
    print('Собираю стату за день...', end='')
    hours = [i for i in range(1, 25)]  # создал кортеж от 0 до 24, чтоб собрать данные за каждый час
    daily_calls = []# переменная для статы по дню
    for h in hours:
        accept_calls_element = wait.until(EC.presence_of_element_located((By.XPATH, f'//*[@id="table2"]/tbody/tr[{h}]/td[2]')))
        accept_calls = accept_calls_element.get_attribute('innerHTML')
        miss_calls_element = wait.until(EC.presence_of_element_located((By.XPATH, f'//*[@id="table2"]/tbody/tr[{h}]/td[4]')))
        miss_calls = miss_calls_element.get_attribute('innerHTML')
        daily_calls.append(int(accept_calls) + int(miss_calls))# записал значение в кортеж
    date = f'{day}.{m}.{2019}'
    all_calls[date] = daily_calls# словарь. Ключ - дата, значение - кортеж со звонками по часам
    print('ok')
    driver.quit()


def csv_writer(data, path):  # разбираем словарь на части и записываем в csv
    with open("output.csv", "w") as outfile:
        writer = csv.writer(outfile, delimiter=",")
        writer.writerow(data)
        writer.writerows(zip(*[data[key] for key in data]))  # записвает так, что ключ в первой ячейке слолбца, остальные данные под ним идут столбцом


if __name__ == '__main__':
    try:
        user_input()
        csv_writer(all_calls, path)
        print('Информация собрана в файле output.csv')
    except(KeyboardInterrupt, SystemExit):
        print('\nПрограмма остановлена.')
