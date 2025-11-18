# 🖥️ دليل إعداد السيرفر

> **📍 أنت هنا**: `09_SERVER_SETUP/SERVER_CONFIG.md`  
> **🏠 العودة للدليل**: [`../INDEX.md`](../INDEX.md)

**تاريخ الإنشاء**: 2025-11-18  
**آخر تحديث**: 2025-11-18  
**الحالة**: ✅ جاهز

---

## 🎯 الهدف من هذا الملف

**ما ستتعلمه**:
- ✅ متطلبات السيرفر
- ✅ خطوات الإعداد الأولي
- ✅ تثبيت Dependencies
- ✅ إعداد البيئة

**المدة**: قراءة 15 دقيقة + تنفيذ 30-60 دقيقة

---

## 💻 متطلبات السيرفر

### الحد الأدنى (Development)

```yaml
OS: Ubuntu 22.04 LTS (أو Debian 12)
CPU: 2 cores
RAM: 4GB
Storage: 20GB SSD
Network: 100 Mbps
```

### الموصى به (Production)

```yaml
OS: Ubuntu 22.04 LTS
CPU: 4 cores
RAM: 8GB
Storage: 50GB SSD
Network: 1 Gbps
Backup: Automated daily backups
```

### السعر المتوقع

| المزود | المواصفات | السعر/شهر |
|--------|-----------|-----------|
| **DigitalOcean** | 2 CPU, 4GB RAM | $24/mo |
| **Hetzner** | 2 CPU, 4GB RAM | $5-10/mo ✅ |
| **Vultr** | 2 CPU, 4GB RAM | $18/mo |
| **Linode** | 2 CPU, 4GB RAM | $18/mo |

**الخيار الأفضل**: **Hetzner Cloud** - أرخص وموثوق

---

## 🔧 الإعداد الأولي

### 1. تحديث النظام

```bash
# تحديث قوائم الحزم
sudo apt update

# ترقية الحزم المثبتة
sudo apt upgrade -y

# تثبيت الأدوات الأساسية
sudo apt install -y \
  curl \
  wget \
  git \
  build-essential \
  software-properties-common \
  apt-transport-https \
  ca-certificates \
  gnupg \
  lsb-release
```

---

### 2. إنشاء مستخدم للمشروع

```bash
# إنشاء مستخدم جديد
sudo adduser workspace
sudo usermod -aG sudo workspace

# التبديل للمستخدم الجديد
su - workspace

# إعداد SSH key (اختياري ولكن موصى به)
ssh-keygen -t ed25519 -C "workspace@server"
```

---

### 3. إعداد Firewall

```bash
# تفعيل UFW
sudo ufw enable

# السماح بـ SSH
sudo ufw allow 22/tcp

# السماح بـ HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# السماح بـ Application Port (مثلاً 3000)
sudo ufw allow 3000/tcp

# التحقق من الحالة
sudo ufw status
```

---

## 📦 تثبيت Dependencies

### 1. Node.js (لـ Next.js)

```bash
# تثبيت Node.js 20 LTS
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# التحقق من التثبيت
node --version   # v20.x.x
npm --version    # 10.x.x

# تثبيت pnpm (اختياري ولكن أسرع)
npm install -g pnpm
```

---

### 2. Python (لـ ServerAutomationAI)

```bash
# تثبيت Python 3.11
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip

# جعل Python 3.11 الافتراضي
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# التحقق
python3 --version   # Python 3.11.x
```

---

### 3. PostgreSQL (Database)

```bash
# تثبيت PostgreSQL 15
sudo apt install -y postgresql postgresql-contrib

# بدء الخدمة
sudo systemctl start postgresql
sudo systemctl enable postgresql

# إنشاء قاعدة بيانات
sudo -u postgres psql << EOF
CREATE DATABASE workspace_db;
CREATE USER workspace_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE workspace_db TO workspace_user;
\q
EOF
```

---

### 4. Git

```bash
# Git مثبت مسبقاً، فقط الإعداد
git config --global user.name "Workspace Server"
git config --global user.email "server@workspace.com"

# إضافة GitHub SSH key (للـ auto pull)
ssh-keygen -t ed25519 -C "github-deploy@workspace"
# أضف المفتاح العام إلى GitHub Deploy Keys
cat ~/.ssh/id_ed25519.pub
```

---

### 5. Docker (اختياري)

```bash
# تثبيت Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# إضافة المستخدم لمجموعة Docker
sudo usermod -aG docker workspace

# تفعيل الخدمة
sudo systemctl enable docker
sudo systemctl start docker

# التحقق
docker --version
```

---

## 📁 إعداد هيكل المشروع

```bash
# إنشاء المجلدات
mkdir -p ~/workspace/{app,logs,backups,data}

# استنساخ المشروع من GitHub
cd ~/workspace/app
git clone git@github.com:username/workspace-platform.git .

# تحديد الصلاحيات
chmod 755 ~/workspace
chmod 700 ~/workspace/data  # بيانات حساسة
```

---

## 🔑 إعداد Environment Variables

### 1. إنشاء ملف .env

```bash
cd ~/workspace/app
nano .env
```

### 2. المحتوى

```bash
# ========================
# Application
# ========================
NODE_ENV=production
APP_URL=https://workspace.example.com
PORT=3000

# ========================
# Database
# ========================
DATABASE_URL="postgresql://workspace_user:your_password@localhost:5432/workspace_db"

# ========================
# NextAuth
# ========================
NEXTAUTH_URL=https://workspace.example.com
NEXTAUTH_SECRET=your-super-secret-key-min-32-chars

# ========================
# AI Keys (ServerAutomationAI)
# ========================
GROQ_API_KEY=sk-proj-xxx...
GEMINI_API_KEY=AI-xxx...
MISTRAL_API_KEY=xxx...

# ========================
# Secrets Encryption
# ========================
ENCRYPTION_KEY=your-fernet-key-here

# ========================
# Bridge Tool
# ========================
GITHUB_TOKEN=ghp_xxx...
GITHUB_REPO=username/workspace-platform

# ========================
# Notifications (اختياري)
# ========================
TELEGRAM_BOT_TOKEN=xxx
TELEGRAM_CHAT_ID=xxx
```

### 3. تأمين الملف

```bash
chmod 600 .env
```

---

## 🚀 تثبيت المشروع

### 1. Frontend (Next.js)

```bash
cd ~/workspace/app

# تثبيت Dependencies
npm install
# أو
pnpm install

# بناء المشروع
npm run build

# اختبار التشغيل
npm run start
# يجب أن يعمل على http://localhost:3000
```

---

### 2. Backend (ServerAutomationAI)

```bash
cd ~/workspace/app/ServerAutomationAI

# إنشاء virtual environment
python3 -m venv venv

# تفعيل
source venv/bin/activate

# تثبيت Dependencies
pip install -r requirements.txt

# تشغيل
python3 -m dev_platform.web.app
# يجب أن يعمل على http://localhost:5000
```

---

### 3. Database Migrations

```bash
cd ~/workspace/app

# تهيئة Prisma
npx prisma generate

# تطبيق Migrations
npx prisma migrate deploy

# تحقق من الاتصال
npx prisma db pull
```

---

## 🔄 إعداد Process Manager (PM2)

### 1. تثبيت PM2

```bash
npm install -g pm2
```

---

### 2. ملف ecosystem.config.js

```javascript
// ~/workspace/app/ecosystem.config.js
module.exports = {
  apps: [
    {
      name: 'workspace-frontend',
      script: 'npm',
      args: 'start',
      cwd: '/home/workspace/workspace/app',
      env: {
        NODE_ENV: 'production',
        PORT: 3000
      },
      instances: 2,
      exec_mode: 'cluster',
      autorestart: true,
      watch: false,
      max_memory_restart: '1G'
    },
    {
      name: 'workspace-backend',
      script: 'python3',
      args: '-m dev_platform.web.app',
      cwd: '/home/workspace/workspace/app/ServerAutomationAI',
      interpreter: '/home/workspace/workspace/app/ServerAutomationAI/venv/bin/python3',
      env: {
        FLASK_ENV: 'production'
      },
      autorestart: true,
      watch: false,
      max_memory_restart: '500M'
    }
  ]
};
```

---

### 3. تشغيل PM2

```bash
cd ~/workspace/app

# بدء جميع التطبيقات
pm2 start ecosystem.config.js

# حفظ التكوين
pm2 save

# تشغيل تلقائي عند إعادة التشغيل
pm2 startup
# اتبع التعليمات

# مراقبة
pm2 monit
pm2 logs
pm2 status
```

---

## 🌐 إعداد Nginx (Reverse Proxy)

### 1. تثبيت Nginx

```bash
sudo apt install -y nginx
```

---

### 2. ملف التكوين

```bash
sudo nano /etc/nginx/sites-available/workspace
```

```nginx
server {
    listen 80;
    server_name workspace.example.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name workspace.example.com;

    # SSL Certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/workspace.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/workspace.example.com/privkey.pem;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Next.js Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Python Backend API
    location /api/agents {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket Support
    location /socket.io {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
    }
}
```

---

### 3. تفعيل وتشغيل

```bash
# تفعيل الموقع
sudo ln -s /etc/nginx/sites-available/workspace /etc/nginx/sites-enabled/

# اختبار التكوين
sudo nginx -t

# إعادة تشغيل Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

## 🔐 إعداد SSL (Let's Encrypt)

```bash
# تثبيت Certbot
sudo apt install -y certbot python3-certbot-nginx

# الحصول على شهادة
sudo certbot --nginx -d workspace.example.com

# تجديد تلقائي (cron)
sudo crontab -e
# أضف:
0 12 * * * /usr/bin/certbot renew --quiet
```

---

## ✅ التحقق من الإعداد

```bash
# 1. التحقق من الخدمات
systemctl status nginx
pm2 status

# 2. التحقق من Ports
sudo netstat -tlnp | grep -E ':(80|443|3000|5000)'

# 3. اختبار التطبيق
curl http://localhost:3000
curl http://localhost:5000/api/health

# 4. اختبار HTTPS
curl https://workspace.example.com
```

---

## 🔗 الروابط ذات الصلة

**للمزيد**:
- 📖 [`../05_OPERATIONS/MONITORING_GUIDE.md`](../05_OPERATIONS/MONITORING_GUIDE.md) - المراقبة
- 📖 [`../05_OPERATIONS/BACKUP_RECOVERY.md`](../05_OPERATIONS/BACKUP_RECOVERY.md) - النسخ الاحتياطي
- 📖 [`../04_SECURITY/SECURITY_POLICY.md`](../04_SECURITY/SECURITY_POLICY.md) - الأمان

**للرجوع**:
- 🏠 [`../INDEX.md`](../INDEX.md) - الدليل الرئيسي

---

**آخر تحديث**: 2025-11-18  
**المسؤول**: DevOps Team  
**الحالة**: ✅ جاهز للاستخدام
