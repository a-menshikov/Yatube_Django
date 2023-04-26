# Описание

Cоциальна сеть для блогеров. Поддерживает CRUD для постов с иллюстрациями, групп, комментариев.
Фронт реализован через Django-шаблоны. Проект покрыт тестами.

## Стек

```text
Python=3.7
Django==2.2.16
```

## Как запустить проект

Клонировать репозиторий и перейти в него в командной строке:

```bash
git clone https://github.com/a-menshikov/api_final_yatube.git
```

Cоздать и активировать виртуальное окружение:

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```bash
python3 -m pip install --upgrade pip
```

```bash
pip install -r requirements.txt
```

Выполнить миграции:

```bash
python3 manage.py migrate
```

Запустить проект:

```bash
python3 manage.py runserver
```
