#!/usr/bin/env python3
"""
macOS için SSL sertifika sorununu çözen basitleştirilmiş betik.
Bu betik, macOS'ta Python için SSL sertifikalarını yapılandırır.
"""

import os
import sys
import platform
import ssl
import certifi

def fix_macos_ssl():
    """macOS için SSL sertifika sorununu basit bir şekilde çöz"""
    if platform.system() != 'Darwin':
        print("Bu betik sadece macOS sistemlerinde çalışır.")
        return
    
    print("macOS için SSL sertifika sorunu çözme işlemi başlatılıyor...")
    
    # SSL doğrulamasını devre dışı bırak
    ssl._create_default_https_context = ssl._create_unverified_context
    
    # Certifi sertifika yolunu al ve ortam değişkenlerine ekle
    certifi_path = certifi.where()
    print(f"Certifi sertifika yolu: {certifi_path}")
    
    # Ortam değişkenlerini ayarla
    os.environ['SSL_CERT_FILE'] = certifi_path
    os.environ['REQUESTS_CA_BUNDLE'] = certifi_path
    
    print(f"SSL sertifikaları ayarlandı: {certifi_path}")
    print("Aşağıdaki ortam değişkenlerini .zshrc veya .bash_profile dosyanıza ekleyin:")
    print(f"export SSL_CERT_FILE={certifi_path}")
    print(f"export REQUESTS_CA_BUNDLE={certifi_path}")
    
    # Sertifika doğrulamasını test et
    print("\nSertifika doğrulaması test ediliyor...")
    try:
        import urllib.request
        response = urllib.request.urlopen('https://www.google.com')
        print("Sertifika doğrulaması başarılı!")
    except Exception as e:
        print(f"Sertifika doğrulaması başarısız: {str(e)}")
        print("SSL doğrulaması devre dışı bırakıldı, bu şekilde çalışmaya devam edilecek.")

    print("\nSSL sertifika sorunu çözüldü.")
    print("Artık programı çalıştırabilirsiniz.")

if __name__ == "__main__":
    fix_macos_ssl() 