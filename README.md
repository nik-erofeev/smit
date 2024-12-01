# Установка и запуск
Создайте в корне приложения файл **.env** и определите в нём все переменные, указанные в [.env_example](./.env_example).

## Запуск через docker-compose

#### Собрать и запустить/остановить приложение с помощью
```sh
$ make up
$ make up_re

$ make down
```



#### Перейти на swagger [http://localhost:8000/docs](http://localhost:8000)
```sh
http://localhost:8000/docs
```


## Локально

#### Установить и активировать виртуальное окружение с помощью команд:
```sh
$ python3.12 -m venv venv
$ source venv/bin/activate
```

#### Установить зависимости:
```sh
$ pip install poetry
$ poetry install
```

#### Запустить/остановить контейнеры кроме API:
```sh
$ make up_local
$ make down
```

<br>

#### Загрузить ЕНВы из файла .env(при локальном  смотреть коммент в [.env_example](./.env_example)) 

<br>

#### Прогнать миграции с помощью с помощью [alembic](https://alembic.sqlalchemy.org/en/latest/):
```sh
$ alembic upgrade head
```


#### Запустить приложение с помощью:
```sh
python3 main.py
```

<br>

#### Перейти на swagger [http://localhost:8000/docs](http://localhost:8000)
```sh
http://localhost:8000/docs
```

<br>

#### Перейти на веб интерфейс kafka (topik) [http://localhost:8090](http://localhost:8090)
в кафку отправляются по 2 батчам
```sh
http://localhost:8090
```

