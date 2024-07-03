Создание пользователя:  

    adduser demo  
      
    usermod -aG sudo demo  
    usermod -aG www-data demo  
    su demo  

Директория должна быть следующая: /var/www/insight (на сервере)

По этому пути находятся папка проекта и файл для зависимостями: `insight`, `requirements.txt`

Устанавлием python:  
`python3 -m venv venv и source venv/bin/activate` - должна появиться папка `venv`

Установка зависимостей: `pip install -r requirements.txt` 

станавливаем postgreSQL: `sudo apt install postgresql` <br/>
Подключаемся к postgres: `sudo -u postgres psql` и прописываем команды <br/>
Если база данных еще не создана - создаём ее, если создана пропускаем шаг <br/>
 `CREATE DATABASE [databaseName] WITH ENCODING='UTF-8';`

Далее создаём пользователя, даём ему полные права. 
На демо стенде этот пользователь и эта база даннхы уже существуют
```
 CREATE USER user_blog WITH PASSWORD 'jfjsdDJUIA';
 GRANT ALL PRIVILEGES ON DATABASE blog TO user_blog;
 ALTER DATABASE blog OWNER TO user_blog; 
```
\q - выходим из терминала postgres

Меняем настройки в `/var/www/insight/insight/blog/settings.py` для подключения к БД

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'blog',
        'USER': 'user_blog',
        'PASSWORD': 'jfjsdDJUIA',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
Раскомментируем и закоментируем строчки в настройках в /var/www/insight/insight/blog/settings.py для сборки статики
```
 STATIC_URL = 'static/'
 #STATICFILES_DIRS = [
 #    BASE_DIR / 'static'
 #]
 STATIC_ROOT = BASE_DIR / 'static'
```
Для скрытия ошибок меняем в `/var/www/insight/insight/blog/settings.py`
`DEBUG=False`


Применяем миграции: python manage.py migrate <br/> 
Пробуем запустить проект через runserver: python manage.py runserver `0.0.0.0:8000` 
(статика может не грузится, это нормально, мы ее оставили для nginx) <br/>
Далее переходим в браузере по адресу `http://<ip_нашего_сервера>:8000`


Уствновка и настройка gunicorn <br/> 
Устанавливаем gunicorn внутри виртуального окружения (если не было указано в requirements): 
`pip install gunicorn`

Прописываем или создаём sudo nano /etc/systemd/system/gunicorn.socket и вставляем туда следующее:
```
 [Unit]
 Description=gunicorn socket
 
 [Socket]
 ListenStream=/run/gunicorn.sock
 
 [Install]
 WantedBy=sockets.target
```

Прописываем sudo nano /etc/systemd/system/gunicorn.service и вставляем туда следующее:
```
 [Unit]
 Description=gunicorn daemon
 Requires=gunicorn.socket
 After=network.target
 
 [Service]
 User=root
 Group=www-data
 WorkingDirectory=/var/www/insight/insight
 ExecStart=/var/www/insight/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/run/gunicorn.sock blog.wsgi:application
 
 [Install]
 WantedBy=multi-user.target
```

Далее запускаем этот сервис и проверяем статус (ничего не должно гореть красным, запускаем каждую строку поочередно) 

    sudo systemctl enable gunicorn.socket 
    sudo systemctl start gunicorn.socket 
    sudo systemctl status gunicorn.socket 
    curl --unix-socket /run/gunicorn.sock localhost 
    file /run/gunicorn.sock 
    sudo systemctl status gunicorn

Если видим зеленую надпись Active running, то значит ошибок нет, и все идет по плану.

Устанавливаем nginx: 
`sudo apt install nginx` 
Далее переходим в браузере по адресу http://<ip_нашего_сервера> Если мы видим текст nginx (Welcome to nginx), значит все в порядке

Создаем файл конфигурации nginx: 
`sudo nano etc/nginx/sites-available/insight`

    server {  
      listen 80;  
      server_name 167.172.96.11;  
       
      location = /favicon.ico { access_log off; log_not_found off; }  
       
      location /static/ {  
        root /var/www/insight/insight;  
      }  
      location /media/ {  
        root /var/www/insight/insight;  
      }  
      location /admin/static/ {  
        root /var/www/insight;  
      }
      location / {  
        include proxy_params;  
        proxy_pass http://unix:/run/gunicorn.sock;  
      }  
    } 

Создаем символическую ссылку:
`sudo ln -s /etc/nginx/sites-available/insight /etc/nginx/sites-enabled/insight`


`sudo nginx -t` - проверяем "syntax is ok"
`sudo systemctl restart nginx` - перезапускаем nginx и переходим по ссылке нашего сайта, все должно работать.
