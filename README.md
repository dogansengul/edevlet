# E-Devlet Belge Doğrulama ve İndirme Otomasyonu

Bu proje, E-Devlet üzerinden belge doğrulama ve indirme işlemlerini otomatikleştiren bir Python uygulamasıdır.

## Özellikler

- E-Devlet belge doğrulama sayfasına otomatik erişim
- Barkod numarası ve TC Kimlik numarası ile belge doğrulama
- Doğrulanan belgeleri otomatik indirme
- İndirilen dosyaları yönetme ve raporlama

## Dosya Yapısı

- `config.py`: Yapılandırma ayarları ve sabitler
- `driver_manager.py`: WebDriver kurulumu ve yönetimi
- `document_validator.py`: Belge doğrulama işlemleri
- `file_manager.py`: Dosya indirme ve yönetme işlemleri
- `main.py`: Ana program akışı

## Gereksinimler

- Python 3.6+
- Selenium
- Chrome WebDriver

## Kurulum

1. Gerekli paketleri yükleyin:

   ```
   pip install selenium
   ```

2. Chrome WebDriver'ı indirin ve PATH'e ekleyin.

## Kullanım

Varsayılan değerlerle çalıştırmak için:

```bash
python main.py
```

Özel parametrelerle çalıştırmak için `main.py` dosyasını düzenleyin veya kodu şu şekilde kullanın:

```python
from main import validate_and_download_document

downloaded_files = validate_and_download_document(
    barcode="BARKOD_NUMARASI",
    tc_kimlik_no="TC_KIMLIK_NO"
)
```
