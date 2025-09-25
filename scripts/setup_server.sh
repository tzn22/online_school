#!/bin/bash

# Скрипт для полной настройки сервера Ubuntu

echo "🚀 Полная настройка сервера Ubuntu для онлайн-школы"
echo "================================================"

# Проверка прав доступа
if [ "$EUID" -ne 0 ]
  then echo "Пожалуйста, запустите скрипт от имени root"
  exit 1
fi

DOMAIN="fluencyclub.fun"
PROJECT_DIR="/var/www/online_school"

echo "Домен: $DOMAIN"
echo "Директория проекта: $PROJECT_DIR"

# 1. Обновление системы
echo "🔄 Обновление системы..."
apt update && apt upgrade -y

# 2. Установка необходимых пакетов
echo "📦 Установка пакетов..."
apt install -y \
    curl wget git vim nano htop net-tools ufw fail2ban \
    nginx postgresql postgresql-contrib redis-server \
    docker.io docker-compose python3-pip python3-venv \
    supervisor nodejs npm unzip zip tar gzip bzip2 rsync \
    openssh-server openssh-client python3-dev build-essential \
    libpq-dev libjpeg-dev zlib1g-dev libffi-dev libssl-dev \
    python3-setuptools python3-wheel python3-cffi \
    software-properties-common apt-transport-https \
    ca-certificates gnupg lsb-release

# 3. Настройка Docker
echo "🐳 Настройка Docker..."
usermod -aG docker $SUDO_USER
systemctl start docker
systemctl enable docker

# 4. Настройка баз данных
echo "🐘 Настройка баз данных..."
systemctl start postgresql
systemctl enable postgresql
systemctl start redis-server
systemctl enable redis-server

# 5. Настройка веб-сервера
echo "🌐 Настройка Nginx..."
systemctl start nginx
systemctl enable nginx

# 6. Настройка безопасности
echo "🛡 Настройка безопасности..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 'Nginx Full'
ufw --force enable

systemctl enable fail2ban
systemctl start fail2ban

# 7. Создание swap файла
echo "💾 Создание swap файла..."
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' | tee -a /etc/fstab

# 8. Настройка времени
echo "⏰ Настройка времени..."
timedatectl set-timezone Europe/Moscow

# 9. Создание директорий проекта
echo "📁 Создание директорий..."
mkdir -p $PROJECT_DIR
mkdir -p /var/backups/online_school
mkdir -p /var/log/online_school
mkdir -p $PROJECT_DIR/{staticfiles,media,logs,data}

# 10. Установка прав доступа
echo "🔧 Установка прав доступа..."
chown -R $SUDO_USER:$SUDO_USER $PROJECT_DIR
chmod -R 755 $PROJECT_DIR

# 11. Создание базы данных PostgreSQL
echo "🔧 Создание базы данных..."
sudo -u postgres psql << EOF
CREATE USER online_school_user WITH PASSWORD 'online_school_pass';
CREATE DATABASE online_school_prod WITH OWNER online_school_user;
GRANT ALL PRIVILEGES ON DATABASE online_school_prod TO online_school_user;
ALTER USER online_school_user CREATEDB;
\q
EOF

# 12. Установка Certbot для SSL
echo "🔐 Установка Certbot..."
apt install -y certbot python3-certbot-nginx

# 13. Настройка автоматических обновлений
echo "🔄 Настройка автоматических обновлений..."
apt install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades

echo "✅ Сервер успешно настроен!"
echo ""
echo "Следующие шаги:"
echo "1. Клонируйте репозиторий в $PROJECT_DIR"
echo "2. Запустите скрипт деплоя: $PROJECT_DIR/scripts/deploy.sh"
echo "3. Настройте домен DNS"
echo "4. Получите SSL сертификат"