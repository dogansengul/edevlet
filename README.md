# 🎯 E-Devlet Event-Driven Belge Doğrulama ve İndirme Otomasyonu

Bu proje, **E-Devlet** platformu üzerinden belge doğrulama ve indirme işlemlerini **event-driven (olay tabanlı)** mimaride otomatikleştiren gelişmiş bir Python uygulamasıdır. Sistem, backend API'den gelen olayları işleyerek, kullanıcı belgelerini otomatik olarak doğrular ve sonuçları günceller.

## 📋 İçindekiler

- [Özellikler](#-özellikler)
- [Mimari Yapı](#-mimari-yapı)
- [Kurulum](#-kurulum)
- [Konfigürasyon](#-konfigürasyon)
- [Kullanım](#-kullanım)
- [Production Deployment](#-production-deployment)
- [Güvenlik](#-güvenlik)
- [Monitoring ve Logs](#-monitoring-ve-logs)
- [Sorun Giderme](#-sorun-giderme)

## 🚀 Özellikler

### Temel Özellikler

- ✅ **Event-Driven Architecture**: Backend API'den gelen olayları SQLite queue ile güvenli işleme
- ✅ **Otomatik Belge Doğrulama**: E-Devlet platformu üzerinden barkod ve TC kimlik numarası ile belge doğrulama
- ✅ **Akıllı Batch Processing**: 2 saatte bir toplu işlem yapmak için Smart Orchestrator
- ✅ **Flask-based Event Receiver**: HTTP API endpoint'leri ile olay alma
- ✅ **IP Whitelisting**: Güvenlik için IP tabanlı erişim kontrolü
- ✅ **SSL/HTTPS Desteği**: Nginx reverse proxy ile HTTPS
- ✅ **İnsan Benzeri Davranış**: Captcha korumasını aşmak için gelişmiş simülasyon
- ✅ **Robust Error Handling**: Kapsamlı hata yönetimi ve recovery
- ✅ **Production Ready**: Gunicorn, systemd ve monitoring desteği

### Gelişmiş Özellikler

- 🔄 **Automatic Token Management**: Backend API token yönetimi ve yenileme
- 📊 **Queue Statistics**: Gerçek zamanlı kuyruk istatistikleri
- 🛡️ **Security Headers**: HSTS, X-Frame-Options, CSP desteği
- 📱 **Health Check Endpoints**: Sistem durumu kontrolü
- 🗄️ **SQLite Database**: Güvenilir event queue ve state management
- 🔧 **Modular Architecture**: Clean Architecture prensipleri
- 📝 **Comprehensive Logging**: Detaylı log sistemi

## 🏗️ Mimari Yapı

### Event-Driven Architecture

```
┌─────────────────┐    HTTP POST     ┌─────────────────┐
│   Backend API   │ ──────────────► │ Event Receiver  │
│   (Events)      │                 │   (Flask API)   │
└─────────────────┘                 └─────────┬───────┘
                                              │
                                              ▼
                                    ┌─────────────────┐
                                    │ SQLite Queue    │
                                    │ (Event Storage) │
                                    └─────────┬───────┘
                                              │
                                              ▼
                                    ┌─────────────────┐
                                    │ Smart           │
                                    │ Orchestrator    │
                                    │ (Batch Process) │
                                    └─────────┬───────┘
                                              │
                                              ▼
                                    ┌─────────────────┐
                                    │ E-Devlet        │
                                    │ Automation      │
                                    │ (WebDriver)     │
                                    └─────────────────┘
```

### Proje Klasör Yapısı

```
edevlet-automazition/
├── src/
│   ├── __init__.py                 # Ana giriş noktası
│   ├── models/                     # Veri modelleri
│   │   ├── __init__.py
│   │   └── entities.py            # User, ValidationResult sınıfları
│   ├── constants/                  # Sabit değerler
│   │   └── __init__.py            # ErrorType, LogLevel, mesajlar
│   ├── exceptions/                 # Özel hata sınıfları
│   │   └── __init__.py            # Custom exception'lar
│   ├── utils/                      # Yardımcı fonksiyonlar
│   │   ├── logging.py             # Log yönetimi
│   │   ├── sqlite_queue.py        # SQLite event queue
│   │   ├── system_setup.py        # Sistem kurulumu
│   │   ├── driver_manager.py      # WebDriver yönetimi
│   │   └── file_manager.py        # Dosya işlemleri
│   ├── services/                   # İş mantığı katmanları
│   │   ├── __init__.py
│   │   ├── document_verification_service.py    # E-Devlet doğrulama
│   │   ├── backend_integration_service.py      # Backend API entegrasyonu
│   │   └── document_processing_service.py      # Belge işleme iş akışı
│   ├── core/                       # Ana bileşenler
│   │   ├── orchestrator.py        # Smart Orchestrator (2 saatte bir)
│   │   ├── event_receiver.py      # Flask Event Receiver API
│   │   ├── backend_service.py     # Backend API client
│   │   ├── main.py               # Legacy giriş noktası
│   │   ├── edevlet.py            # E-Devlet işlemleri
│   │   ├── document_validator.py  # Belge doğrulama
│   │   └── human_behavior.py      # İnsan benzeri davranış
│   └── config/                     # Konfigürasyon
│       ├── __init__.py
│       └── config.py              # Sistem ayarları
├── downloads/                      # İndirilen belgeler
├── logs/                          # Log dosyaları
├── screenshots/                   # Hata ekran görüntüleri
├── .env                          # Environment variables
├── requirements.txt              # Python dependencies
├── wsgi.py                      # Production WSGI entry point
├── run_event_system.py          # Event system launcher
├── gunicorn.conf.py            # Gunicorn configuration
├── nginx_proxy.conf            # Nginx reverse proxy config
├── production_deployment.sh    # Production deployment script
└── setup_ssl.sh               # SSL certificate setup
```

## 📦 Kurulum

### 1. Sistem Gereksinimleri

#### Minimum Sistem Gereklilikleri

- **CPU**: 2 cores (önerilen 4 cores)
- **RAM**: 4GB (önerilen 8GB)
- **Storage**: 50GB SSD
- **Network**: 100Mbps
- **OS**: Ubuntu 20.04 LTS veya üzeri

#### Yazılım Gereksinimleri

- Python 3.8+
- Chrome/Chromium browser
- SQLite3
- Nginx (production için)

### 2. Projeyi İndirme

```bash
git clone https://github.com/kullanici/edevlet-automazition.git
cd edevlet-automazition
```

### 3. Python Bağımlılıklarını Yükleme

```bash
# Virtual environment oluştur (önerilen)
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# veya
venv\Scripts\activate     # Windows

# Bağımlılıkları yükle
pip install -r requirements.txt
```

### 4. Sistem Kurulumu

```bash
# macOS kullanıcıları için SSL sertifika sorunu çözümü
python src/utils/fix_macos_ssl.py

# SSL sertifikalarını yükle
python src/utils/install_certificates.py
```

## ⚙️ Konfigürasyon

### 1. Environment Variables (.env dosyası)

**ZORUNLU**: Aşağıdaki `.env` dosyasını proje ana dizininde oluşturun:

```bash
# ====== ZORUNLU BACKEND API AYARLARI ======
BACKEND_API_BASE_URL=https://your-backend-api.com
BACKEND_API_EMAIL=your-api-email@domain.com
BACKEND_API_PASSWORD=your-secure-password

# ====== GÜVENLİK AYARLARI ======
FLASK_ENV=production
SECRET_KEY=your-super-secure-random-key-minimum-32-characters

# IP Whitelist (virgülle ayrılmış)
ALLOWED_IPS=127.0.0.1,::1,your_backend_ip,192.168.1.0/24

# ====== İŞLEM AYARLARI ======
# Processing interval (saniye cinsinden - varsayılan 2 saat)
PROCESSING_WAIT_INTERVAL_SECONDS=7200

# WebDriver ayarları
HEADLESS=true
WINDOW_SIZE=1920,1080

# Bekleme süreleri
MIN_WAIT=1
MAX_WAIT=3
PAGE_LOAD_WAIT=5
ELEMENT_LOAD_WAIT=2

# İnsan benzeri davranış
MOUSE_MOVEMENT_SPEED=0.8
SCROLL_SPEED=0.5
TYPING_SPEED=0.2
PAUSE_BETWEEN_ACTIONS=1.0

# ====== LOG AYARLARI ======
LOG_LEVEL=INFO
LOG_DIR=logs
LOG_MAX_SIZE=10485760
LOG_BACKUP_COUNT=5

# ====== PRODUCTION AYARLARI ======
MAX_WORKERS=4
WORKER_TIMEOUT=120
MAX_REQUESTS=10000
ENABLE_METRICS=true
HEALTH_CHECK_INTERVAL=300
```

### 2. Dosya İzinleri

```bash
# .env dosyasını güvenli hale getir
chmod 600 .env
chown $USER:$USER .env

# SQLite database için dizin oluştur
mkdir -p logs downloads screenshots
chmod 755 logs downloads screenshots
```

## 🚀 Kullanım

### 1. Development Modunda Çalıştırma

```bash
# Event-driven sistem başlat (önerilen)
python3 run_event_system.py
```

Bu komut şunları başlatır:

- **Event Receiver**: Flask API (port 5001)
- **Smart Orchestrator**: 2 saatte bir batch processing

### 2. Legacy Mod (Tek Seferlik İşlem)

```bash
# Eski stil - tek seferlik belge doğrulama
python -m src.core.main
```

### 3. Production Modunda Çalıştırma

```bash
# Production deployment script ile
bash production_deployment.sh

# Veya manuel olarak
gunicorn -c gunicorn.conf.py wsgi:app
```

### 4. Programatik Kullanım

```python
# Event gönderme örneği
import requests
import json

event_data = {
    "event": {
        "userId": "user-guid-123",
        "identityNumber": "12345678901",
        "eventType": "UserCvCreated",
        "eventData": {
            "id": "cv-guid-456",
            "documentNumber": "BARCODE12345"
        }
    }
}

response = requests.post(
    'https://your-domain.com/api/events',
    json=event_data,
    headers={'Content-Type': 'application/json'}
)

print(response.json())
```

## 🔧 API Endpoints

### Event Receiver Endpoints

| Method | Endpoint           | Açıklama              | IP Kısıtlaması |
| ------ | ------------------ | --------------------- | -------------- |
| POST   | `/api/events`      | Event gönderme        | ✅ Evet        |
| GET    | `/health`          | Sistem durumu         | ❌ Hayır       |
| GET    | `/api/queue/stats` | Kuyruk istatistikleri | ❌ Hayır       |

### Event Formatı

```json
{
  "event": {
    "userId": "guid-here",
    "identityNumber": "12345678901",
    "eventType": "UserCvCreated",
    "eventData": {
      "id": "cv-guid-here",
      "documentNumber": "BARCODE12345"
    }
  }
}
```

### API Yanıt Formatları

#### Başarılı Event Alma

```json
{
  "success": true,
  "message": "Event received and queued successfully",
  "event_id": 1,
  "queue_stats": {
    "total_events": 1,
    "new_events": 1,
    "processing_events": 0,
    "completed_events": 0,
    "failed_events": 0
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### Hata Yanıtı

```json
{
  "success": false,
  "message": "Access denied: IP address not authorized",
  "client_ip": "203.0.113.10",
  "error_code": "IP_NOT_WHITELISTED",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## 🏭 Production Deployment

### 1. Nginx Reverse Proxy Kurulumu

```bash
# Nginx kurulumu
sudo apt update
sudo apt install nginx

# Konfigürasyon dosyasını kopyala
sudo cp nginx_proxy.conf /etc/nginx/sites-available/edevlet-app

# Domain/IP güncellemesi yap
sudo nano /etc/nginx/sites-available/edevlet-app
# 'your_domain_or_ip.com' -> gerçek domain/IP

# Site'ı etkinleştir
sudo ln -s /etc/nginx/sites-available/edevlet-app /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Nginx test ve restart
sudo nginx -t
sudo systemctl reload nginx
```

### 2. SSL Sertifikası Kurulumu

#### Domain ile Let's Encrypt (Önerilen)

```bash
# Certbot kurulumu
sudo apt install certbot python3-certbot-nginx

# SSL sertifikası al
sudo certbot --nginx -d yourdomain.com
```

#### IP Adresi ile Self-Signed

```bash
# Self-signed sertifika oluştur
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/nginx-selfsigned.key \
    -out /etc/nginx/ssl/nginx-selfsigned.crt \
    -subj "/C=TR/ST=Turkey/L=Istanbul/O=Organization/CN=YOUR_IP"
```

### 3. Systemd Service Kurulumu

```bash
# Service dosyası oluştur
sudo nano /etc/systemd/system/edevlet-automation.service
```

```ini
[Unit]
Description=E-Devlet Event-Driven Automation System
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/your/edevlet-automation
ExecStart=/usr/bin/python3 run_event_system.py
Restart=always
RestartSec=10
Environment=FLASK_ENV=production

[Install]
WantedBy=multi-user.target
```

```bash
# Service'i etkinleştir
sudo systemctl daemon-reload
sudo systemctl enable edevlet-automation
sudo systemctl start edevlet-automation
```

### 4. Firewall Ayarları

```bash
# HTTP ve HTTPS trafiğine izin ver
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

## 🔒 Güvenlik

### IP Whitelisting

Sistem, **IP Whitelisting** ile korunmaktadır. Sadece izin verilen IP adreslerinden gelen istekler işlenir.

#### Konfigürasyon

```bash
# .env dosyasında
ALLOWED_IPS="127.0.0.1,::1,192.168.1.0/24,production_backend_ip"
```

#### Desteklenen Formatlar

- **Exact IP**: `192.168.1.100`
- **IPv6**: `2001:db8::1`
- **CIDR Network**: `192.168.1.0/24`, `10.0.0.0/8`

### Güvenlik Headers

Nginx konfigürasyonu aşağıdaki güvenlik header'larını ekler:

- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`

### SSL/TLS

- TLS 1.2 ve 1.3 desteği
- Strong cipher suites
- Perfect Forward Secrecy

## 📊 Monitoring ve Logs

### Log Dosyaları

| Dosya                               | Açıklama                                    |
| ----------------------------------- | ------------------------------------------- |
| `event_receiver.log`                | Event Receiver Flask API logları            |
| `orchestrator.log`                  | Smart Orchestrator batch processing logları |
| `edevlet_automation.log`            | Legacy sistem logları                       |
| `/var/log/nginx/edevlet_access.log` | Nginx access logları                        |
| `/var/log/nginx/edevlet_error.log`  | Nginx error logları                         |

### Health Check

```bash
# Sistem durumu kontrolü
curl -k https://your-domain.com/health

# Kuyruk istatistikleri
curl -k https://your-domain.com/api/queue/stats

# Service durumu
sudo systemctl status edevlet-automation
sudo systemctl status nginx
```

### Monitoring Komutları

```bash
# Real-time log takibi
tail -f event_receiver.log orchestrator.log

# Sistem kaynak kullanımı
htop
df -h
free -h

# Port kontrolü
sudo netstat -tlnp | grep 5001
sudo lsof -i :443
```

## 🐛 Sorun Giderme

### Yaygın Sorunlar

#### 1. Port 5001 Meşgul

```bash
# Hangi process kullanıyor?
sudo lsof -i :5001

# Process'i öldür
sudo kill -9 <PID>
```

#### 2. SSL Sertifika Hatası

```bash
# Let's Encrypt yenileme
sudo certbot renew --dry-run
sudo systemctl reload nginx

# macOS SSL sorunu
python src/utils/fix_macos_ssl.py
```

#### 3. WebDriver Hatası

```bash
# Chrome kurulumu (Ubuntu)
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install google-chrome-stable

# ChromeDriver güncellemesi
pip install --upgrade undetected-chromedriver webdriver-manager
```

#### 4. .env Dosyası Eksik

```bash
# .env dosyası kontrolü
ls -la .env

# Örnek .env oluştur
cp .env.example .env
nano .env
```

#### 5. IP Whitelist Hatası

```bash
# Mevcut IP'nizi öğrenin
curl ifconfig.me

# ALLOWED_IPS'e ekleyin
echo "ALLOWED_IPS=127.0.0.1,::1,$(curl -s ifconfig.me)" >> .env
```

#### 6. Database Lock Hatası

```bash
# SQLite database'i unlock et
sqlite3 queue.db "PRAGMA busy_timeout=30000;"

# Database'i yeniden oluştur
rm queue.db
python3 -c "from src.utils.sqlite_queue import SQLiteEventQueue; SQLiteEventQueue('queue.db')"
```

### Debug Modunda Çalıştırma

```bash
# Verbose logging ile
export LOG_LEVEL=DEBUG
python3 run_event_system.py

# Headless mode kapatma (WebDriver görünür)
export HEADLESS=false
python3 -m src.core.main
```

### Log Analizi

```bash
# Hata loglarını filtrele
grep -i "error\|exception\|failed" event_receiver.log orchestrator.log

# Son 100 log satırı
tail -n 100 event_receiver.log

# Belirli tarih aralığı
grep "2024-01-15" orchestrator.log
```

## 📖 Kullanım Senaryoları

### 1. Backend Integration

Sistem, backend API'den gelen events'leri otomatik olarak işler:

1. Backend API, kullanıcı CV'si oluşturduğunda event gönderir
2. Event Receiver, eventi SQLite kuyruğuna ekler
3. Smart Orchestrator, 2 saatte bir kuyrukta event işler
4. Belge doğrulama yapılır ve sonuç backend'e gönderilir

### 2. Manual Testing

Test amaçlı manuel event gönderimi:

```bash
curl -X POST https://your-domain.com/api/events \
  -H 'Content-Type: application/json' \
  -d '{
    "event": {
      "userId": "test-user-123",
      "identityNumber": "12345678901",
      "eventType": "UserCvCreated",
      "eventData": {
        "id": "test-cv-456",
        "documentNumber": "TEST_BARCODE_123"
      }
    }
  }'
```

### 3. Bulk Processing

Toplu belge işleme:

```bash
# Orchestrator'ı manuel başlat
python3 -m src.core.orchestrator --db-path queue.db --check-interval 5
```

## 📚 Referanslar

### Python Dependencies

- **selenium**: WebDriver automation
- **undetected-chromedriver**: Anti-detection WebDriver
- **flask**: HTTP API framework
- **requests**: HTTP client
- **python-dotenv**: Environment variable management
- **gunicorn**: WSGI HTTP server
- **gevent**: Async I/O
- **psutil**: System monitoring

### External Services

- **E-Devlet**: Türkiye.gov.tr belge doğrulama platformu
- **Backend API**: Your custom backend service
- **Chrome/Chromium**: WebDriver browser

---

**⚠️ Önemli**: Production ortamında kullanmadan önce tüm konfigürasyonları doğrulayın ve güvenlik ayarlarını kontrol edin.
