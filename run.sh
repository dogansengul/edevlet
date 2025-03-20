#!/bin/bash

# SSL sertifikalarını kontrol et
python3 src/utils/fix_macos_ssl.py > /dev/null 2>&1

# Ana programı çalıştır
python3 -m src.core.main 

#./run.sh ile çalıştırın