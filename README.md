# Пиццерия в Телеграм

Телеграм магазин подключен к CMS [elasticpath](https://www.elasticpath.com/). 
Выводится список товаров из CMS в ввиде inline кнопок.


* Пример магазина в [Телеграм](https://t.me/new_pizza_dewmnabot)

### Как установить

У вас уже должен быть установлен Python 3. Если его нет, то установите.
Так же нужно установить необходимые пакеты:
```
pip3 install -r requirements.txt
```

### Как пользоваться скриптом

Для работы скрипта нужно создать файл ```.env``` в директории где лежит скрипт.

#### Настройки для Telegram

1. Создать бота в телеграм. Написать [Отцу ботов](https://telegram.me/BotFather):
    * /start
    * /newbot
    
2. Отец ботов попросит ввести два имени.
    * Первое — как он будет отображаться в списке контактов, можно написать на русском.
    * Второе — имя, по которому бота можно будет найти в поиске. 
      Должно быть английском и заканчиваться на bot (например, notification_bot)

3. Вставьте ваш токен бота в файл ```.env```:
    ```
    TELEGRAM_TOKEN=95132391:wP3db3301vnrob33BZdb33KwP3db3F1I
    ```
4. Получить тестовый токен для оплаты (Tranzzo Test):
    ```
    TELEGRAM_PAYMENT=410694247:TEST:65219df2-7569-423d-ae9d-bea4c90b3f6b
    ```
5. Вставить телеграм id курьера:
    ```
    COURIER_ID=335031317
    ```
7. Вставить ID чата текущего пользователя telegram:
   ```
   TG_CHAT_ID=335031317
   ```

#### Настройки для CMS

1. Создать магазин в [elasticpath](https://www.elasticpath.com/).

2. Во вкладке Home найти ```Client ID``` и ```Client secret``` и вставить в файл ```.env```:
    ```
    MOLTIN_CLIENT_ID=6WMl2ibq6G68UFt67QZECoX0T5o9WMAaVcgvM5H5a7
    MOLTIN_CLIENT_SECRET=7ktj8MmQR3NZsFsouo3fc0zwNhImBILIWNnd0n7OVl
    ```
3. Добавить валюту (RUB) в [настройках](https://dashboard.elasticpath.com/app/settings):
   
    3.1 Нажать кнопку - ```New currency```;
   
    3.2 Code (Required) = ```RUB```;
   
    3.3 Exchange Rate (Required) = 10;
   
    3.4 Format (Required) = ```{price}```;
   
    3.5 Decimal Point (Required) = ```.``` (точка);
   
    3.6 Thousand Separator (Required) = ``` ``` (пробел)

#### Настройки для базы данных (Redis)

Вставить ваши данные в файл ```.env```:

``` 
REDIS_HOST='redis-16156.c263.us-east-1-2.ec2.cloud.redislabs.com'
REDIS_PORT=16156
REDIS_PASSWORD='tUN6QoJldZNMSXr9uV7DmSbWf2IwZwLX'
```

#### Настройки для API Яндекс-геокодера

Получить API ключ в [кабинете разработчика](https://developer.tech.yandex.ru/services/):
``` 
YANDEX_APIKEY='d6b4f8cf-2523-46ca-af1e-11a7f736488a'
```

#### Настройки для базы данных (Redis)
Для работы скрипта нужны 2 файла с адресами и меню. Пример файлов лежит в папке ```json```

### Создание магазина
Для запуска магазина вам необходимо запустить командную строку и перейти в каталог со скриптом:
```
>>> python3 create_shop.py
```

### Запуск бота
Перейти в папку ```tg_bot``` и запустить команду:
```
>>> python3 start_bot.py
```

### Цели проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).