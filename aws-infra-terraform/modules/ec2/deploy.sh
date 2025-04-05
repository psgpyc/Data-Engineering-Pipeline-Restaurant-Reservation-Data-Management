#!/bin/bash
sudo yum update -y
sudo yum install -y python3-pip python3-venv 
sudo yum install -y git 
sudo yum install -y nginx

cd /home/ec2-user

git clone https://github.com/psgpyc/ozzy.git

python3 -m venv prodenv
source prodenv/bin/activate

pip install --upgrade pip
pip install fastapi uvicorn


sudo systemctl enable nginx
sudo systemctl start nginx

# Create Nginx reverse proxy config
cat << EOF | sudo tee /etc/nginx/conf.d/pipeline.conf
server {
    listen 80 default_server;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

sudo nginx -t && sudo systemctl reload nginx

cd ozzy/api-endpoints

uvicorn main:app --host 127.0.0.1 --port 8000 &
