from aiogram import Bot, Dispatcher, executor, types
import logging

#Файл с токеном. НЕ ЗАБУДЬТЕ ЕГО СОЗДАТЬ И НАПОЛНИТЬ!!!
import config

from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
from selenium import webdriver

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)
data_user = ''

@dp.message_handler(commands=['filter'])
async def prev(message: types.Message):
    global data_user
    if message.text != '/filter':
        dat = message.text.split(' ')
        data_user = dat[1]
        await message.answer(
            f'Установлена дата. Магазины, зарегистрированные в Kaspi.kz позже {data_user} не будут отображаться!')
    else:
        await message.answer('Отправьте дату вместе с комадой в формате ДД.ММ.ГГ.\nПример: /filter 01.01.2000')


@dp.message_handler(commands=['clear_filter'])
async def previ(message: types.Message):
    await message.answer('Фильтр успешно очищен!')
    global data_user
    data_user = ''


@dp.message_handler(commands=['views_filter'])
async def views(message: types.Message):
    if data_user != '':
        await message.answer(f'Дата: {data_user}')
    else:
        await message.answer(f'Дата: не установлена')


@dp.message_handler(commands=['list'])
async def list(message: types.Message):
    await message.answer(
        '/start - начать парсинг\n/filter - установить дату. После установки все магазины, зарегестрированные позже установленной даты, не отображаются\n/views_filter - показать настройки фильтра\n /clear_filter - сбросить настройки фильтра\n/help - инструкция по использованию бота')


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await message.answer('Для начало работы введите команду /start и пришлите ссылку на категорию.\n'
                         'ВНИМАНИЕ! Бот ссылки на общие категории обрабатывает не корректно, но c дочерними все в порядке. Пример: ссылка на категорию "Обувь" не обработвется, а ссылка на дочернюю "Женская обувь" успешно обработает')


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('Здравствуйте. Для начала парсинга отправьте ссылку на нужный каталог')

    @dp.message_handler()
    async def parsing(message: types.Message):
        urls = message.text
        if "https://kaspi.kz/shop/" in urls:
            try:
                await message.answer('Ожидайте')
                ite = 1
                options = Options()
                options.add_argument('--headless')
                options.add_argument('--disable-gpu')
                options.add_argument(
                    'user-agent: Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36')

                #Вместо PATH_TO_DRIVER нужно вставить полный путь до вашего chromedriver. На Linux может быть достаточно
                #ввести chromedriver
                driver = webdriver.Chrome(executable_path="PATH_TO_DRIVER",
                                          chrome_options=options)
                while True:
                    url = urls

                    # открываю сайт и записываю его
                    driver.get(url)
                    with open("category.html", "w", encoding='utf-8') as file:
                        file.write(driver.page_source)
                    with open("category.html", encoding='utf-8') as file:
                        f = file.read()

                    # начинаю парсить по файлу ссылку на товар
                    soup_start = BeautifulSoup(f, 'lxml')
                    for iter in range(len(soup_start.find_all(class_="item-card__name-link"))):
                        tovar_link = soup_start.find_all('a', class_="item-card__name-link")[iter].get('href')

                        # перехожу на сайт товара и записываю его
                        driver.get(tovar_link)
                        with open("tovar.html", "w", encoding='utf-8') as file_1:
                            file_1.write(driver.page_source)
                        with open("tovar.html", encoding='utf-8') as file_1:
                            f_1 = file_1.read()

                        # ищу ссылки на магазины
                        soup_tovar = BeautifulSoup(f_1, 'lxml')
                        try:
                            store = soup_tovar.find("table", class_="sellers-table__self").find('tbody').find_all('tr')

                            active = True
                            click = 1
                            # прохожусь по магазинам
                            while active:
                                for iterate in range(0, len(soup_tovar.find_all('tr')) - 1):
                                    store_ = store[iterate].find('td').find('a').get('href')
                                    href = "https://kaspi.kz" + store_
                                    driver.get(href)
                                    with open("store.html", "w", encoding='utf-8') as file_2:
                                        file_2.write(driver.page_source)
                                    with open("store.html", encoding='utf-8') as file_2:
                                        f_2 = file_2.read()
                                    soup = BeautifulSoup(f_2, 'lxml')

                                    data_ = soup.find(class_="merchant-profile__data-create").text
                                    data = ''
                                    num = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']
                                    for i in data_:
                                        if i in num:
                                            data += i
                                    data = data.split('.')
                                    data.pop(-1)

                                    data = [int(i) for i in data]
                                    global data_user
                                    d = data_user
                                    print(d)
                                    print(data)
                                    if d != '':
                                        d = d.split('.')
                                        d = [int(i) for i in d]

                                        if d[2] < data[2]:
                                            continue
                                        elif d[2] == data[2]:
                                            if d[1] < data[1]:
                                                continue
                                            elif d[1] == data[1]:
                                                if d[0] < data[0]:
                                                    continue
                                                else:
                                                    name = soup.find(class_="merchant-profile__name").text
                                                    number_phone = soup.find(
                                                        class_="merchant-profile__contact-text").text
                                                    await message.answer(
                                                        f'Магазин: {name}\nНомер: {number_phone}\nСсылка: {href}\n{data_}')
                                            else:
                                                name = soup.find(class_="merchant-profile__name").text
                                                number_phone = soup.find(class_="merchant-profile__contact-text").text
                                                await message.answer(
                                                    f'Магазин: {name}\nНомер: {number_phone}\nСсылка: {href}\n{data_}')
                                        else:
                                            name = soup.find(class_="merchant-profile__name").text
                                            number_phone = soup.find(class_="merchant-profile__contact-text").text
                                            await message.answer(
                                                f'Магазин: {name}\nНомер: {number_phone}\nСсылка: {href}\n{data_}')

                                    else:
                                        name = soup.find(class_="merchant-profile__name").text
                                        number_phone = soup.find(class_="merchant-profile__contact-text").text
                                        await message.answer(
                                            f'Магазин: {name}\nНомер: {number_phone}\nСсылка: {href}\n{data_}')

                                # нажимаю кнопку "Следующая"
                                try:
                                    button = soup_tovar.find('div', 'pagination').find_all('li')[-1].get('class')
                                    if button != ['pagination__el']:
                                        active = False
                                    else:
                                        driver.get(tovar_link)
                                        xpath = '/html/body/div[1]/div[5]/div[2]/div/div[1]/div/div/div/div[1]/div/div/div[2]/li[7]'
                                        for i in range(click):
                                            time.sleep(1)
                                            driver.find_element_by_xpath(xpath).click()
                                        click += 1
                                        with open("tovar.html", "w", encoding='utf-8') as file_1:
                                            file_1.write(driver.page_source)
                                        with open("tovar.html", encoding='utf-8') as file_1:
                                            f_1 = file_1.read()
                                        # ищу ссылки на магазины
                                        soup_tovar = BeautifulSoup(f_1, 'lxml')
                                        store = soup_tovar.find("table", class_="sellers-table__self").find(
                                            'tbody').find_all('tr')

                                # Если его нет то заканчиваем цикл и продолжаем парсить
                                except AttributeError:
                                    active = False
                                    break
                        except AttributeError:
                            continue

                    try:
                        soup_end = BeautifulSoup(f, 'lxml')
                        button = soup_end.find('div', 'pagination').find_all('li')[-1].get('class')
                        if button != ['pagination__el']:
                            break
                        else:
                            driver.get(url)
                            xpath = '/html/body/div[1]/div[3]/div/div[3]/div[2]/div[2]/li[7]'
                            for i in range(ite):
                                time.sleep(1)
                                driver.find_element_by_xpath(xpath).click()
                            ite += 1
                            with open("category.html", "w", encoding='utf-8') as file_1:
                                file.write(driver.page_source)
                            with open("category.html", encoding='utf-8') as file_1:
                                f = file.read()
                            # ищу ссылки на магазины
                            soup_start = BeautifulSoup(f, 'lxml')

                    except AttributeError:
                        break
            except Exception as ex:
                print(f'ОШИБКА! Что-то пошло не так. Проверьте работу сайта, отправленную ссылку и перезапустите бота.\n'
                      f'Если проблема осталась или нужна помощь - пишите разработчику @Stern145 и отправьте код ошибки -> {ex}')
            finally:
                driver.close()
                driver.quit()
                await message.answer('Парсинг закончен')
        else:
            await message.answer('Ссылка не корректна')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)