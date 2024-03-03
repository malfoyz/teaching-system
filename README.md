<h2 align="center">Система для обучения на Django</h2>

Тестовое задание от HardQode. Система для обучения на Django.

### Инструменты разработки

**Стек:**
- Python = 3.10.0
- Django = 4.2.10

## Старт

#### 1) Создать образ

    docker-compose build

##### 2) Запустить контейнер

    docker-compose up
    
##### 3) Перейти по адресу

    http://127.0.0.1:8000/

## Разработка с Docker

##### 1) Сделать форк репозитория

##### 2) Клонировать репозиторий

    git clone ссылка_сгенерированная_в_вашем_репозитории

##### 3) В корне проекта создать .env.dev

    DEBUG=1
    SECRET_KEY=django-insecure-#jfxf#qja0p3o6#q57)^ezp7lg(sl+xcf-mvl=7j=1z&j-1urx
    DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]
    
##### 4) Создать образ

    docker-compose build

##### 5) Запустить контейнер

    docker-compose up
    
##### 6) Создать суперюзера

    docker exec -it teaching-system-teaching_system-1 python manage.py createsuperuser
                                                        
##### 7) Если нужно очистить БД

    docker-compose down -v

## API

#### Корень API расположен по адреcу:

    http://127.0.0.1:8000/api/v1/