## О данном проекте 
* Back-end для магазина книг с api эндпоинтами
* Для API настроены разрешения, фильтр, поиск, добавление, редактирование и удаление
* Оптимизированны ORM запросы, кэш для оценок книг 
* 80% покрытия тестами по данным coverage
* Настроена авторизация через Github (без key и secret)


### Запуск
1. Клонируем проект с репозитория
```python
git clone https://github.com/yottabufer/BooksStore.git
```
2. Переходим в папку созданную папку
```python
cd BooksStore
```
3. Создаём виртуально окружение для работы с проектом
```python
python -m venv venv_bookstore
```
4. Активируем виртуальное окружение
	
+ Linux
```python
source venv_bookstore/bin/activate
```
+ Windows
```python
venv_bookstore\Scripts\activate.bat 
```
5. Устанавливаем зависимости
```python
pip install -r requirements.txt
```
6. Проверяем всё ли в порядке
```python
python manage.py runserver
```
7. Запуск тестов
```python
python manage.py test . 
```
> ВАЖНО
>> Тесты упадут без подключения к базе PostgreSQL в setting.DATABASES
