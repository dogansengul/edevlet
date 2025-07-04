# 🚀 E-Devlet Automation Service

Basit Flask API + Background Job sistemi.

## ⚡ Hızlı Başlangıç

```bash
# 1. Environment setup
cp env.template .env
# .env dosyasını düzenle

# 2. Virtual environment
source venv/bin/activate

# 3. Servisi başlat
cd src
python main.py &

# 4. Logs'u izle
tail -f logs/edevlet_service.log
```

## 📋 Nasıl Çalışır

1. **Event Reception**: Backend API'den POST `/api/events` ile events alır
2. **Queue**: SQLite veritabanında events saklar
3. **Background Job**: 2 saatte bir events'leri işler
4. **E-Devlet Check**: Belge doğrulaması yapar
5. **Result**: PUT ile backend'e sonuç gönderir

## 🔧 Endpoints

- `POST /api/events` - Event alma
- `GET /api/stats` - Kuyruk istatistikleri
- `POST /api/process` - Manuel işlem
- `GET /health` - Health check

## ⚙️ Configuration (.env)

```bash
# Flask
FLASK_HOST=0.0.0.0
FLASK_PORT=5002

# Database
DATABASE_PATH=queue_clean.db

# Backend API
BACKEND_API_BASE_URL=https://your-backend.com
BACKEND_API_EMAIL=email@domain.com
BACKEND_API_PASSWORD=password

# Processing
PROCESSING_INTERVAL_HOURS=2
BATCH_SIZE=1

# Browser (for real E-Devlet)
BROWSER_HEADLESS=true
BROWSER_TIMEOUT=30
```

## 🎯 Production

```bash
# Arka planda çalıştır
cd src
nohup python main.py > /dev/null 2>&1 &

# Process kontrol
ps aux | grep main.py

# Durdur
pkill -f main.py

# Logları izle
tail -f logs/edevlet_service.log
```

## 📊 Event Format

```json
{
  "event": {
    "userId": "user-123",
    "identityNumber": "12345678901",
    "eventType": "UserEducationCreated",
    "eventData": {
      "id": "edu-456",
      "documentNumber": "BARCODE789"
    }
  }
}
```

## 🛠️ Production Setup

Service gerçek E-Devlet otomasyonu ile çalışır.

Tamam! 🎉
