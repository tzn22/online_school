#!/bin/bash

# Скрипт для полного деплоя проекта на сервере

echo "🚀 Начало деплоя проекта на fluencyclub.fun"
echo "========================================"

# Проверка прав доступа
if [ "$EUID" -ne 0 ]
  then echo "Пожалуйста, запустите скрипт от имени root"
  exit 1
fi

# Переменные
PROJECT_DIR="/var/www/online_school"
DOMAIN="fluencyclub.fun"

echo "📁 Рабочая директория: $PROJECT_DIR"
echo "🌐 Домен: $DOMAIN"

# 1. Остановка существующих контейнеров
echo "⏹ Остановка существующих контейнеров..."
cd $PROJECT_DIR
docker-compose down

# 2. Удаление volumes (потеря данных!)
echo "🗑 Удаление volumes..."
docker volume rm postgres_data redis_data static_volume media_volume 2>/dev/null || true

# 3. Обновление кода
echo "🔄 Обновление кода..."
git pull origin main

# 4. Установка зависимостей
echo "📦 Установка зависимостей..."
pip3 install -r requirements.txt

# 5. Создание .env файла если его нет
if [ ! -f ".env" ]; then
    echo "🔧 Создание .env файла..."
    cat > .env << EOF
# Database settings
DB_NAME=online_school_prod
DB_USER=online_school_user
DB_PASSWORD=$(openssl rand -base64 32)
DB_HOST=db
DB_PORT=5432

# Redis settings
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Django settings
DEBUG=False
SECRET_KEY=$(openssl rand -base64 50)
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,$DOMAIN,www.$DOMAIN
CSRF_TRUSTED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN
CORS_ALLOWED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN

# Email settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=localhost
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@$DOMAIN
SERVER_EMAIL=admin@$DOMAIN

# Payment settings
YOOKASSA_SHOP_ID=your_yookassa_shop_id
YOOKASSA_SECRET_KEY=your_yookassa_secret_key
YOOKASSA_RETURN_URL=https://$DOMAIN/payment-success/

# Security settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Media and static files
MEDIA_URL=/media/
STATIC_URL=/static/
EOF
    echo "✅ .env файл создан"
fi

# 6. Сборка Docker образов
echo "🏗 Сборка Docker образов..."
docker-compose build --no-cache

# 7. Запуск контейнеров
echo "🚀 Запуск контейнеров..."
docker-compose up -d

# 8. Ожидание запуска базы данных
echo "⏳ Ожидание запуска базы данных..."
sleep 30

# 9. Выполнение миграций
echo "🔄 Выполнение миграций..."
docker-compose exec web python manage.py migrate

# 10. Создание суперпользователя
echo "👤 Создание суперпользователя..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@$DOMAIN', 'admin')" | docker-compose exec web python manage.py shell

# 11. Сбор статических файлов
echo "📦 Сбор статических файлов..."
docker-compose exec web python manage.py collectstatic --noinput

# 12. Настройка Nginx
echo "🌐 Настройка Nginx..."
cat > /etc/nginx/sites-available/$DOMAIN << EOF
upstream django {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    # Redirect all HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    # SSL certificate paths (настройте Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/$DOMAIN/chain.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https:  blob: 'unsafe-inline'" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone \$binary_remote_addr zone=login:10m rate=1r/s;

    # Root path
    location / {
        proxy_pass http://django;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        
        # Rate limiting
        limit_req zone=api burst=20 nodelay;
    }

    # Static files
    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        gzip_static on;
    }

    # Media files
    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 1y;
        add_header Cache-Control "public";
    }

    # API endpoints with rate limiting
    location ~ ^/api/ {
        proxy_pass http://django;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        
        # Rate limiting for API
        limit_req zone=api burst=10 nodelay;
    }

    # Login endpoints with stricter rate limiting
    location ~ ^/(api/auth/login|admin/login)/ {
        proxy_pass http://django;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        
        # Stricter rate limiting for login
        limit_req zone=login burst=3 nodelay;
    }

    # Health check endpoint
    location /health/ {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Error pages
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
EOF

# Включение сайта
ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Проверка и перезапуск Nginx
nginx -t && systemctl reload nginx

# 13. Получение SSL сертификата (если нужно)
echo "🔐 Получение SSL сертификата..."
if command -v certbot &> /dev/null; then
    certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
else
    echo "⚠️  Certbot не установлен. Установите его для SSL сертификатов:"
    echo "apt install certbot python3-certbot-nginx"
fi

# 14. Настройка автоматического обновления SSL
echo "🔄 Настройка автоматического обновления SSL..."
crontab -l | { cat; echo "0 12 * * * /usr/bin/certbot renew --quiet"; } | crontab -

echo "✅ Деплой проекта завершен!"
echo ""
echo "Доступ к приложению:"
echo "- Основное приложение: https://$DOMAIN"
echo "- Админка Django: https://$DOMAIN/admin/"
echo "- Swagger API: https://$DOMAIN/swagger/"
echo "- ReDoc API: https://$DOMAIN/redoc/"
echo ""
echo "Учетные данные администратора:"
echo "- Логин: admin"
echo "- Email: admin@$DOMAIN"
echo "- Пароль: admin"