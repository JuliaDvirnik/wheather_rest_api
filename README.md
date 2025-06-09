# Реализация REST-API на Django REST Framework для получения реальной текущей погоды и прогноза на ближайшие дни с возможностью ручного переопределения прогноза.

## Функциональность

1. **GET** `/api/weather/current?city={city}`  
   Возвращает текущую температуру (°C) и локальное время в указанном городе.

2. **GET** `/api/weather/forecast?city={city}&date={dd.MM.yyyy}`  
   Возвращает прогноз (min/max °C) на указанную дату (от сегодня до +8 дней).

3. **POST** `/api/weather/forecast`  
   Позволяет вручную задать или переопределить прогноз для города на дату (от сегодня до +8 дней).  
   После сохранения все GET `/forecast` с теми же параметрами возвращают переопределённые данные.

## Установка и запуск

1. **Клонировать репозиторий**  
```bash
   git clone https://github.com/your-username/weather-api.git
   cd weather-api
```
2. **Установить зависимости**

```bash
pip install -r requirements.txt
```
3. **Скопировать файл и заполнить ключ API от OpenWeather**

```bash
cp .env.template .env
# В .env указать:
# OPENWEATHER_API_KEY=ваш_ключ_здесь
```
4. **Применить миграции и создать суперпользователя**

```bash
python manage.py migrate
python manage.py createsuperuser
```

5.**Запустить сервер**

```bash
python manage.py runserver
```
По умолчанию доступно на http://127.0.0.1:8000/


## Конфигурация
Файл .env.template содержит шаблон для переменных:

```bash
OPENWEATHER_API_KEY=your_api_key_here
```

## API Endpoints
1. **GET /api/weather/current**
Query-параметры

city (string, обязателен) — название города на англ. (Moscow, Amsterdam).

Успешный ответ (200)

```bash
{
  "temperature": 22.1,
  "local_time": "16:45"
}
```
Ошибки
400 — неверные параметры.
404 — город не найден или ошибка внешнего API.

2. **GET /api/weather/forecast**
Query-параметры

city (string, обязателен)

date (string, формат dd.MM.yyyy, обязателен; от сегодня до +8 дней)

Успешный ответ (200)

```bash
{
  "min_temperature": 11.1,
  "max_temperature": 24.5
}
```
Ошибки

400 — неверный формат даты или вне диапазона.

404 — город не найден или прогноз недоступен.

3. **POST /api/weather/forecast**
Body (application/json)

```bash
{
  "city": "Berlin",
  "date": "11.06.2025",
  "min_temperature": 10.0,
  "max_temperature": 18.5
}
```
Успешный ответ (200)
Тело запроса в JSON.

## Валидация

Дата: от сегодня до +8 дней.

min_temperature ≤ max_temperature.

## Поведение

Сохраняет/перезаписывает прогноз в БД.


## Технологии
Python 3.8+

Django 3.2

Django REST Framework

SQLite

OpenWeather Geocoding API: https://openweathermap.org/api/geocoding-api

OpenWeather One Call API v3.0: https://openweathermap.org/api/one-call-3

