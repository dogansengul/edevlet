#!/bin/bash

# 🔐 E-Devlet Automation SSL Setup Script
# Bu script SSL sertifikası kurulumunu otomatikleştirir

set -e

echo "🔐 E-Devlet Automation SSL Kurulum Script'i"
echo "=============================================="

# Kullanıcıdan bilgi al
read -p "Domain adınız var mı? (y/n): " has_domain
if [[ $has_domain == "y" || $has_domain == "Y" ]]; then
    read -p "Domain adınızı girin (örn: mydomain.com): " domain_name
    ssl_type="letsencrypt"
else
    read -p "Sunucu IP adresinizi girin: " server_ip
    ssl_type="selfsigned"
fi

read -p "Backend sunucunuzun IP adresini girin (event'ler bu IP'den gelecek): " backend_ip

echo ""
echo "🔧 Kurulum bilgileri:"
echo "SSL Tipi: $ssl_type"
if [[ $ssl_type == "letsencrypt" ]]; then
    echo "Domain: $domain_name"
else
    echo "Sunucu IP: $server_ip"
fi
echo "Backend IP: $backend_ip"
echo ""

read -p "Kuruluma devam etmek istiyor musunuz? (y/n): " confirm
if [[ $confirm != "y" && $confirm != "Y" ]]; then
    echo "❌ Kurulum iptal edildi"
    exit 1
fi

echo "🚀 Kurulum başlıyor..."

# 1. Nginx kurulumu
echo "📦 Nginx kuruluyor..."
sudo apt update
sudo apt install -y nginx

# 2. SSL Sertifikası kurulumu
if [[ $ssl_type == "letsencrypt" ]]; then
    echo "🔒 Let's Encrypt SSL sertifikası alınıyor..."
    sudo apt install -y certbot python3-certbot-nginx
    
    # Nginx konfigürasyonunu güncelle
    sed "s/your_domain_or_ip.com/$domain_name/g" nginx_proxy.conf > /tmp/edevlet-app
    sudo cp /tmp/edevlet-app /etc/nginx/sites-available/edevlet-app
    
    # Site'ı etkinleştir
    sudo ln -sf /etc/nginx/sites-available/edevlet-app /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Nginx'i test et ve başlat
    sudo nginx -t
    sudo systemctl reload nginx
    
    # SSL sertifikası al
    sudo certbot --nginx -d $domain_name --non-interactive --agree-tos --email admin@$domain_name
    
else
    echo "🔒 Self-signed SSL sertifikası oluşturuluyor..."
    sudo mkdir -p /etc/nginx/ssl
    sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/nginx/ssl/nginx-selfsigned.key \
        -out /etc/nginx/ssl/nginx-selfsigned.crt \
        -subj "/C=TR/ST=Turkey/L=Istanbul/O=Organization/OU=OrgUnit/CN=$server_ip"
    
    # Nginx konfigürasyonunu güncelle
    cat > /tmp/edevlet-app << EOF
server {
    listen 80;
    server_name $server_ip;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl;
    server_name $server_ip;

    # Self-signed SSL Configuration
    ssl_certificate /etc/nginx/ssl/nginx-selfsigned.crt;
    ssl_certificate_key /etc/nginx/ssl/nginx-selfsigned.key;
    
    # SSL ayarları
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # Proxy settings
    proxy_connect_timeout       300;
    proxy_send_timeout          300;
    proxy_read_timeout          300;
    send_timeout                300;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Forwarded-Port \$server_port;
        proxy_buffering off;
        proxy_request_buffering off;
        proxy_set_header Connection "";
        proxy_http_version 1.1;
    }

    location /health {
        proxy_pass http://127.0.0.1:5001/health;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_valid 200 30s;
        add_header X-Cache-Status \$upstream_cache_status;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:5001/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        client_max_body_size 10M;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    access_log /var/log/nginx/edevlet_access.log;
    error_log /var/log/nginx/edevlet_error.log;
}
EOF
    
    sudo cp /tmp/edevlet-app /etc/nginx/sites-available/edevlet-app
    sudo ln -sf /etc/nginx/sites-available/edevlet-app /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
fi

# 3. Firewall ayarları
echo "🔥 Firewall ayarları..."
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# 4. IP Whitelist güncelleme
echo "🔒 IP Whitelist güncelleniyor..."
export ALLOWED_IPS="127.0.0.1,::1,$backend_ip,192.168.1.0/24"

# 5. Nginx'i test et ve başlat
echo "🔧 Nginx test ediliyor..."
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl reload nginx

# 6. Systemd service oluştur
echo "⚙️ Systemd service oluşturuluyor..."
cat > /tmp/edevlet-automation.service << EOF
[Unit]
Description=E-Devlet Event-Driven Automation System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 run_event_system.py
Restart=always
RestartSec=10
Environment=ALLOWED_IPS="127.0.0.1,::1,$backend_ip,192.168.1.0/24"

[Install]
WantedBy=multi-user.target
EOF

sudo cp /tmp/edevlet-automation.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable edevlet-automation

echo ""
echo "✅ SSL Kurulumu Tamamlandı!"
echo "=========================="
echo ""

if [[ $ssl_type == "letsencrypt" ]]; then
    echo "🌐 SSL URL: https://$domain_name"
    echo "🧪 Test komutu: curl https://$domain_name/health"
else
    echo "🌐 SSL URL: https://$server_ip"
    echo "🧪 Test komutu: curl -k https://$server_ip/health"
    echo "⚠️  Not: Self-signed sertifika kullandığınız için -k parametresi gerekli"
fi

echo ""
echo "📋 Başlatma komutları:"
echo "  sudo systemctl start edevlet-automation    # Servisi başlat"
echo "  sudo systemctl status edevlet-automation   # Servis durumunu kontrol et"
echo "  sudo systemctl logs -f edevlet-automation  # Logları takip et"
echo ""

echo "🔒 IP Whitelist:"
echo "  Authorized IP: $backend_ip"
echo "  Local IPs: 127.0.0.1, ::1, 192.168.1.0/24"
echo ""

echo "📊 Log dosyaları:"
echo "  Nginx Access: /var/log/nginx/edevlet_access.log"
echo "  Nginx Error: /var/log/nginx/edevlet_error.log" 
echo "  Application: journalctl -u edevlet-automation -f"
echo ""

read -p "Şimdi Flask uygulamasını başlatmak istiyor musunuz? (y/n): " start_app
if [[ $start_app == "y" || $start_app == "Y" ]]; then
    echo "🚀 Flask uygulaması başlatılıyor..."
    sudo systemctl start edevlet-automation
    sleep 3
    sudo systemctl status edevlet-automation
fi

echo ""
echo "🎉 Kurulum başarıyla tamamlandı!"

# Cleanup
rm -f /tmp/edevlet-app /tmp/edevlet-automation.service 