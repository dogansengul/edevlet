# E-Devlet Belge Doğrulama ve İndirme Otomasyonu

Bu proje, E-Devlet üzerinden belge doğrulama ve indirme işlemlerini otomatikleştiren bir Python uygulamasıdır.

## Özellikler

- E-Devlet belge doğrulama sayfasına otomatik erişim
- Barkod numarası ve TC Kimlik numarası ile belge doğrulama
- Doğrulanan belgeleri otomatik indirme
- İndirilen dosyaları yönetme ve raporlama
- İnsan benzeri davranışlar ile captcha korumasını aşma
- Gelişmiş hata yönetimi ve alternatif yöntemler
- Akıllı fare hareketleri ve sayfa etkileşimleri

## Proje Yapısı

```
edevlet-automazition/
├── src/
│   ├── core/           # Ana uygulama mantığı
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── edevlet.py
│   │   ├── document_validator.py
│   │   └── human_behavior.py
│   ├── utils/          # Yardımcı fonksiyonlar
│   │   ├── __init__.py
│   │   ├── driver_manager.py
│   │   ├── file_manager.py
│   │   ├── install_certificates.py
│   │   └── fix_macos_ssl.py
│   ├── config/         # Yapılandırma dosyaları
│   │   ├── __init__.py
│   │   └── config.py
│   ├── screenshots/    # Hata ekran görüntüleri
│   └── logs/          # Log dosyaları
├── downloads/         # İndirilen dosyalar
├── .env              # Hassas bilgiler (git'e gönderilmez)
├── .gitignore
├── requirements.txt
└── README.md
```

## Gereksinimler

- Python 3.6+
- Selenium
- undetected-chromedriver
- Chrome WebDriver
- python-dotenv
- fake-useragent
- certifi
- requests

## Kurulum

1. Projeyi klonlayın:

   ```bash
   git clone https://github.com/kullanici/edevlet-automazition.git
   cd edevlet-automazition
   ```

2. Gerekli paketleri yükleyin:

   ```bash
   pip install -r requirements.txt
   ```

3. `.env` dosyasını oluşturun ve gerekli bilgileri ekleyin:

   ```env
   BARCODE_NUMBER=your_barcode_number
   TC_KIMLIK_NO=your_tc_kimlik_no
   ```

4. macOS kullanıcıları için SSL sertifika sorununu çözmek için:
   ```bash
   python src/utils/fix_macos_ssl.py
   ```

## Kullanım

1. Varsayılan değerlerle çalıştırmak için:

   ```bash
   python -m src.core.main
   ```

2. Özel parametrelerle programatik kullanım:

   ```python
   from src.core.main import validate_and_download_document

   result = validate_and_download_document(
       barcode="BARKOD_NUMARASI",
       tc_kimlik_no="TC_KIMLIK_NO"
   )

   if result["success"]:
       print(f"İndirilen dosyalar: {result['files']}")
   else:
       print(f"Hata: {result['error']['message']}")
   ```

## Özellikler ve Modüller

### Core Modülleri

- `main.py`: Ana program akışı ve koordinasyonu
- `document_validator.py`: Belge doğrulama işlemleri ve form yönetimi
- `human_behavior.py`: İnsan benzeri davranış simülasyonu ve bot tespitini önleme
- `edevlet.py`: E-Devlet servisleri ile etkileşim

### Utility Modülleri

- `driver_manager.py`: WebDriver kurulumu ve yönetimi
- `file_manager.py`: Dosya indirme ve yönetme işlemleri
- `install_certificates.py`: SSL sertifika yükleme
- `fix_macos_ssl.py`: macOS SSL sorunları için çözümler

### Yapılandırma

- `config.py`: Merkezi yapılandırma ve sabitler
- `.env`: Hassas bilgiler ve kişisel ayarlar

## Güvenlik Özellikleri

- Hassas bilgiler `.env` dosyasında saklanır ve git'e gönderilmez
- SSL sertifika doğrulama desteği
- İnsan benzeri davranışlar ile bot tespitini önleme
- Akıllı fare hareketleri ve sayfa etkileşimleri
- Alternatif yöntemler ile hata durumlarını yönetme

## Sorun Giderme

### SSL Sertifika Hatası

```
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
```

Çözüm:

1. SSL sertifikalarını yükleyin:
   ```bash
   python src/utils/fix_macos_ssl.py
   ```
2. Veya ortam değişkenlerini ayarlayın:
   ```bash
   export SSL_CERT_FILE=/path/to/cacert.pem
   export REQUESTS_CA_BUNDLE=/path/to/cacert.pem
   ```

### Element Bulunamama Hatası

```
NoSuchElementException: Message: no such element
```

Çözüm:

1. Sayfanın tamamen yüklenmesini bekleyin
2. Element ID'lerinin doğru olduğunu kontrol edin
3. Alternatif element bulma yöntemlerini kullanın

## Katkıda Bulunma

1. Bu depoyu fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/amazing_feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing_feature`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.
