# E-Devlet Belge Doğrulama ve İndirme Otomasyonu

Bu proje, E-Devlet üzerinden belge doğrulama ve indirme işlemlerini otomatikleştiren bir Python uygulamasıdır.

## Özellikler

- E-Devlet belge doğrulama sayfasına otomatik erişim
- Barkod numarası ve TC Kimlik numarası ile belge doğrulama
- Doğrulanan belgeleri otomatik indirme
- İndirilen dosyaları yönetme ve raporlama
- İnsan benzeri davranışlar ile captcha korumasını aşma
- Proxy ve User-Agent rotasyonu ile IP engellemelerini önleme

## Dosya Yapısı

- `config.py`: Yapılandırma ayarları ve sabitler
- `driver_manager.py`: WebDriver kurulumu ve yönetimi
- `document_validator.py`: Belge doğrulama işlemleri
- `file_manager.py`: Dosya indirme ve yönetme işlemleri
- `main.py`: Ana program akışı
- `human_behavior.py`: İnsan benzeri davranışları simüle eden sınıf
- `install_certificates.py`: macOS için SSL sertifikalarını yükleyen betik
- `fix_macos_ssl.py`: macOS için SSL sertifika sorununu çözen betik

## Gereksinimler

- Python 3.6+
- Selenium
- undetected-chromedriver
- Chrome WebDriver

## Kurulum

1. Gerekli paketleri yükleyin:

   ```
   pip install -r requirements.txt
   ```

2. `.env` dosyasını düzenleyin ve proxy bilgilerinizi ekleyin.

3. macOS kullanıcıları için SSL sertifika sorununu çözmek için:

   ```
   python fix_macos_ssl.py
   ```

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

## macOS SSL Sertifika Sorunu Çözümü

macOS'ta SSL sertifika doğrulama hatası alıyorsanız, aşağıdaki adımları izleyin:

1. SSL sertifikalarını yükleyin:

   ```bash
   python fix_macos_ssl.py
   ```

2. Veya manuel olarak şu komutu çalıştırın:

   ```bash
   cd /Applications/Python 3.x/ && ./Install\ Certificates.command
   ```

3. Ortam değişkenlerini ayarlayın:

   ```bash
   export SSL_CERT_FILE=/path/to/cacert.pem
   export REQUESTS_CA_BUNDLE=/path/to/cacert.pem
   ```

4. Bu değişkenleri kalıcı yapmak için `.zshrc` veya `.bash_profile` dosyanıza ekleyin.

## Sorun Giderme

### SSL Sertifika Hatası

```
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate
```

Bu hata, SSL sertifikalarının doğrulanamamasından kaynaklanır. Çözüm için:

1. `fix_macos_ssl.py` betiğini çalıştırın.
2. Veya `driver_manager.py` dosyasında SSL doğrulamasını devre dışı bırakın.

### Proxy Hatası

Proxy bağlantı hatası alıyorsanız, `.env` dosyasındaki proxy listesini güncelleyin veya proxy kullanımını devre dışı bırakın.
