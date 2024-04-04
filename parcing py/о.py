import requests
from bs4 import BeautifulSoup
import sqlite3
import json

# Функція для отримання HTML-коду сторінки за URL
def get_html(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print("Сталася помилка при отриманні сторінки:", response.status_code)
        return None

# Функція для отримання даних зі сторінки та їх збереження у базу даних та JSON файл
def parse_page_and_save(url, db_name, json_file):
    html = get_html(url)
    if html:
        soup = BeautifulSoup(html, 'html.parser')

        # Підключення до бази даних SQLite
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Створення таблиці
        cursor.execute('''CREATE TABLE IF NOT EXISTS phone (
                            id INTEGER PRIMARY KEY,
                            name TEXT,
                            price REAL,
                            discount REAL,
                            description TEXT
                                            );
                                                ''')

        # Отримання інформації про товари
        products_data = []

        products = soup.find_all('div', class_='goods-tile')
        for product in products:
            name = product.find('span', class_='goods-tile__title').text.strip()

            # Отримання ціни товару
            price_element = product.find('span', class_='goods-tile__price-value')
            price_str = price_element.text.strip()

            # Отримання знижки на товар, якщо вона є
            discount = 0.0  # Ініціалізація змінної discount перед умовою
            discount_element = product.find('span', class_='goods-tile__discount')
            if discount_element:
                discount_str = discount_element.text.strip()
                # Видалення всіх символів, які не є цифрами або крапкою
                discount_str_cleaned = ''.join(char for char in discount_str if char.isdigit() or char == '.')
                discount = float(discount_str_cleaned)
                # Видалення всіх символів, які не є цифрами або крапкою
                price_str_cleaned = ''.join(char for char in price_str if char.isdigit() or char == '.')
                price = float(price_str_cleaned) + discount
            else:
                # Якщо знижки немає, просто конвертуємо рядок у число
                price_str_cleaned = ''.join(char for char in price_str if char.isdigit() or char == '.')
                price = float(price_str_cleaned)

            # Вставка даних у таблицю
            cursor.execute('''INSERT INTO phone (name, price, discount, description) VALUES (?, ?, ?, ?)''',
                           (name, price, discount, price_str))

            # Збереження даних у форматі JSON
            product_data = {
                'name': name,
                'price': price,
                'discount': discount,
                'description': price_str
            }
            products_data.append(product_data)

        # Збереження змін у базі даних
        conn.commit()
        conn.close()

        # Збереження даних у JSON файл
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(products_data, f, ensure_ascii=False, indent=4)

        print("Дані успішно збережено у базу даних та у JSON файл", db_name, json_file)

# URL сторінки, яку потрібно спарсити (приклад для категорії телефонів)
url = 'https://rozetka.com.ua/ua/telefony/c4627900/'

# Ім'я бази даних SQLite
db_name = 'phones.db'

# Ім'я JSON файлу
json_file = 'phones.json'

# Виклик функції для парсингу сторінки та збереження даних у базу даних та JSON файл
parse_page_and_save(url, db_name, json_file)