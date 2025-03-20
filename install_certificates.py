#!/usr/bin/env python3
"""
macOS için SSL sertifikalarını yükleyen basitleştirilmiş betik.
Bu betik, macOS'ta Python için SSL sertifikalarını yükler.
"""

import os
import sys
import subprocess
import platform
import certifi

def install_certificates():
    """macOS için SSL sertifikalarını yükle"""
    if platform.system() != 'Darwin':
        print("Bu betik sadece macOS sistemlerinde çalışır.")
        return
    
    print("macOS için SSL sertifikalarını yükleme işlemi başlatılıyor...")
    
    # Certifi sertifika yolunu al
    certifi_path = certifi.where()
    print(f"Certifi sertifika yolu: {certifi_path}")
    
    # Ortam değişkenlerini ayarla
    os.environ['SSL_CERT_FILE'] = certifi_path
    os.environ['REQUESTS_CA_BUNDLE'] = certifi_path
    
    print(f"SSL sertifikaları ayarlandı: {certifi_path}")
    print("Aşağıdaki ortam değişkenlerini .zshrc veya .bash_profile dosyanıza ekleyin:")
    print(f"export SSL_CERT_FILE={certifi_path}")
    print(f"export REQUESTS_CA_BUNDLE={certifi_path}")
    
    # Homebrew ile Python yüklendiyse
    try:
        # Python yolunu al
        python_path = sys.executable
        print(f"Python yolu: {python_path}")
        
        # Homebrew Python sertifika yükleme betiği
        if 'homebrew' in python_path.lower() or '/opt/homebrew' in python_path:
            cmd = f"{python_path} -m pip install --upgrade certifi"
            print(f"Homebrew Python sertifika yükleme komutu çalıştırılıyor: {cmd}")
            subprocess.run(cmd, shell=True, check=True)
    except Exception as e:
        print(f"Sertifika yükleme hatası: {e}")
    
    print("SSL sertifikaları başarıyla yüklendi.")

if __name__ == "__main__":
    install_certificates() 