# 🖥️ متطلبات السيرفر (Server Requirements)

## الحد الأدنى من المتطلبات

### نظام التشغيل
- **Ubuntu 20.04 LTS** أو أحدث (موصى به)
- **Debian 10** أو أحدث
- **CentOS 8** / **RHEL 8** (مدعوم)

### الموارد

#### للاختبار والتطوير
- **CPU:** 2 أنوية (2 vCPU)
- **RAM:** 2 GB
- **Storage:** 20 GB SSD
- **Network:** 100 Mbps

#### للإنتاج (موصى به)
- **CPU:** 4 أنوية (4 vCPU) أو أكثر
- **RAM:** 4 GB أو أكثر
- **Storage:** 50 GB SSD
- **Network:** 1 Gbps

#### للإنتاج الثقيل (عدد كبير من الوكلاء أو بيانات كثيفة)
- **CPU:** 8 أنوية (8 vCPU)
- **RAM:** 8-16 GB
- **Storage:** 100+ GB NVMe SSD
- **Network:** 1+ Gbps

---

## البرامج المطلوبة

### أساسي

```bash
# Python 3.9+
python3 --version

# pip (مدير حزم Python)
pip3 --version

# Git
git --version

# systemd (لإدارة الخدمات)
systemctl --version
```

### قاعدة البيانات

```bash
# PostgreSQL 12+ (موصى به)
psql --version

# أو MongoDB 4.4+ (اختياري)
mongod --version
```

### أدوات إضافية

```bash
# rsync (للنقل السريع)
rsync --version

# curl (لاختبار الاتصالات)
curl --version

# htop (لمراقبة الموارد - اختياري)
htop --version
```

---

## الأذونات والمستخدمين

### إنشاء مستخدم منفصل (موصى به)

```bash
# إنشاء مستخدم للنظام
sudo useradd -m -s /bin/bash aiagent

# إضافة صلاحيات sudo (إذا لزم الأمر)
sudo usermod -aG sudo aiagent

# إنشاء مجلد SSH
sudo mkdir -p /home/aiagent/.ssh
sudo chmod 700 /home/aiagent/.ssh

# إضافة المفتاح العام
sudo nano /home/aiagent/.ssh/authorized_keys
# الصق المفتاح العام هنا

sudo chmod 600 /home/aiagent/.ssh/authorized_keys
sudo chown -R aiagent:aiagent /home/aiagent/.ssh
```

### إعداد المجلدات

```bash
# إنشاء المجلد الأساسي
sudo mkdir -p /srv/ai_system

# منح الصلاحيات للمستخدم
sudo chown -R aiagent:aiagent /srv/ai_system
sudo chmod 755 /srv/ai_system

# إنشاء البنية
sudo -u aiagent mkdir -p /srv/ai_system/{releases,backups,logs}
```

---

## الأمان

### Firewall (UFW)

```bash
# تثبيت وتفعيل UFW
sudo apt install ufw
sudo ufw enable

# السماح بـ SSH
sudo ufw allow 22/tcp

# السماح بالمنافذ المطلوبة (إذا كان هناك واجهة ويب)
# sudo ufw allow 5000/tcp

# فحص الحالة
sudo ufw status
```

### SSH Security

```bash
# تحرير إعدادات SSH
sudo nano /etc/ssh/sshd_config

# التوصيات:
# PermitRootLogin no
# PasswordAuthentication no  # بعد إعداد SSH keys
# PubkeyAuthentication yes
# Port 22  # أو منفذ مخصص

# إعادة تشغيل SSH
sudo systemctl restart sshd
```

### Fail2ban (حماية من Brute Force)

```bash
# التثبيت
sudo apt install fail2ban

# التفعيل
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## تثبيت PostgreSQL

### Ubuntu/Debian

```bash
# تثبيت PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# تشغيل الخدمة
sudo systemctl start postgresql
sudo systemctl enable postgresql

# إنشاء مستخدم وقاعدة بيانات
sudo -u postgres psql

# في PostgreSQL shell:
CREATE USER aiagent WITH PASSWORD 'your_secure_password';
CREATE DATABASE ai_system OWNER aiagent;
GRANT ALL PRIVILEGES ON DATABASE ai_system TO aiagent;
\q

# اختبار الاتصال
psql -U aiagent -d ai_system -h localhost
```

### إعداد المتغيرات البيئية

```bash
# إنشاء ملف .env
nano /srv/ai_system/.env

# أضف:
PGHOST=localhost
PGPORT=5432
PGDATABASE=ai_system
PGUSER=aiagent
PGPASSWORD=your_secure_password
```

---

## تثبيت Python والمكتبات

### Python 3.9+

```bash
# تثبيت Python 3.9+
sudo apt install python3.9 python3.9-venv python3-pip

# التأكد من الإصدار
python3 --version

# تثبيت virtualenv (اختياري لكن موصى به)
pip3 install virtualenv
```

### إعداد البيئة الافتراضية (اختياري)

```bash
# في مجلد المشروع
cd /srv/ai_system/current
python3 -m venv venv
source venv/bin/activate

# تثبيت المكتبات
pip install -r requirements.txt
```

---

## إعداد systemd Service

### إنشاء ملف الخدمة

```bash
sudo nano /etc/systemd/system/ai_agents.service
```

أنظر `systemd/ai_agents.service` للمحتوى الكامل.

### تفعيل الخدمة

```bash
# إعادة تحميل systemd
sudo systemctl daemon-reload

# تفعيل الخدمة
sudo systemctl enable ai_agents

# تشغيل الخدمة
sudo systemctl start ai_agents

# فحص الحالة
sudo systemctl status ai_agents

# فحص السجلات
sudo journalctl -u ai_agents -f
```

---

## Monitoring & Logs

### Log Rotation

```bash
# إنشاء إعدادات logrotate
sudo nano /etc/logrotate.d/ai_agents

# المحتوى:
/srv/ai_system/current/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 aiagent aiagent
}
```

### Monitoring Tools (اختياري)

```bash
# htop - مراقبة الموارد
sudo apt install htop

# ncdu - فحص استخدام القرص
sudo apt install ncdu

# nethogs - مراقبة الشبكة
sudo apt install nethogs
```

---

## النسخ الاحتياطي

### إعداد Cron للنسخ الاحتياطي التلقائي

```bash
# تحرير crontab
crontab -e

# إضافة: نسخ احتياطي يومي في 2 صباحاً
0 2 * * * cd /srv/ai_system/current && /usr/bin/python3 src/setup/backup_database.py >> /srv/ai_system/logs/backup.log 2>&1

# نسخ احتياطي أسبوعي للملفات
0 3 * * 0 tar -czf /srv/ai_system/backups/weekly_backup_$(date +\%Y\%m\%d).tar.gz /srv/ai_system/current
```

---

## اختبار النظام

### اختبار شامل

```bash
# 1. اختبار Python
python3 --version
pip3 list

# 2. اختبار قاعدة البيانات
psql -U aiagent -d ai_system -h localhost -c "SELECT version();"

# 3. اختبار الصلاحيات
touch /srv/ai_system/test && rm /srv/ai_system/test

# 4. اختبار systemd
sudo systemctl status ai_agents

# 5. اختبار الوكلاء
cd /srv/ai_system/current
python3 main.py status
```

---

## تقدير التكلفة

### VPS Providers (تقديري)

#### DigitalOcean
- **Basic Droplet** (2GB RAM, 1 vCPU): ~$12/month
- **Recommended** (4GB RAM, 2 vCPU): ~$24/month
- **Production** (8GB RAM, 4 vCPU): ~$48/month

#### Hetzner
- **CX21** (4GB RAM, 2 vCPU): ~€5.83/month (~$6)
- **CX31** (8GB RAM, 2 vCPU): ~€10.76/month (~$11)
- **CPX31** (8GB RAM, 4 vCPU): ~€14.29/month (~$15)

#### AWS EC2
- **t3.small** (2GB RAM, 2 vCPU): ~$15/month
- **t3.medium** (4GB RAM, 2 vCPU): ~$30/month
- **t3.large** (8GB RAM, 2 vCPU): ~$60/month

---

## Performance Tuning

### PostgreSQL Tuning

```bash
# تحرير postgresql.conf
sudo nano /etc/postgresql/13/main/postgresql.conf

# التوصيات للذاكرة 4GB:
shared_buffers = 1GB
effective_cache_size = 3GB
maintenance_work_mem = 256MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 10MB
min_wal_size = 1GB
max_wal_size = 4GB

# إعادة تشغيل PostgreSQL
sudo systemctl restart postgresql
```

### System Tuning

```bash
# زيادة حدود الملفات المفتوحة
sudo nano /etc/security/limits.conf

# إضافة:
aiagent soft nofile 65536
aiagent hard nofile 65536

# تطبيق التغييرات
ulimit -n 65536
```

---

## Checklist النهائي

قبل تشغيل النظام، تأكد من:

- [ ] Ubuntu/Debian محدث
- [ ] Python 3.9+ مثبت
- [ ] PostgreSQL مثبت ويعمل
- [ ] المستخدم `aiagent` منشأ ولديه صلاحيات
- [ ] المجلد `/srv/ai_system` منشأ
- [ ] SSH keys معدة
- [ ] Firewall معد
- [ ] systemd service معد
- [ ] المتغيرات البيئية معدة
- [ ] النسخ الاحتياطي التلقائي معد
- [ ] جميع الاختبارات نجحت

---

**آخر تحديث:** 2025-11-14  
**الإصدار:** 1.0.0
