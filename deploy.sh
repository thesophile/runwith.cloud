#!/bin/bash

# Exit on any error
set -e

# 1. Update the system and install dependencies
echo "Updating system and installing dependencies..."
sudo apt update -y
sudo apt upgrade -y
sudo apt install -y python3-pip python3-dev libpq-dev nginx

# 2. Navigate to the project folder (the repo is already cloned)
# cd /path/to/your/django/project

# 3. Install Python dependencies globally (no virtualenv)
echo "Installing project dependencies..."
sudo pip3 install -r requirements.txt

# 4. Set up Django settings for production
echo "Configuring Django settings..."
# You need to manually edit your `settings.py` file to include your domain or IP in `ALLOWED_HOSTS`
# Make sure DEBUG is set to False and that your DATABASES configuration is correct.

# Example:
# ALLOWED_HOSTS = ['your_domain.com', 'server_ip']
# DEBUG = False
# Ensure that DATABASES is configured correctly for SQLite
# DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR / 'db.sqlite3',
#    }
# }

# 5. Collect static files for production
echo "Collecting static files..."
python3 manage.py collectstatic --noinput

# 6. Set up Gunicorn to run the app
echo "Setting up Gunicorn..."
# Gunicorn is installed via the requirements.txt
# Here we will run Gunicorn with the desired number of workers
gunicorn --workers 3 --bind unix:/path/to/your/project/myproject.sock myproject.wsgi:application

# 7. Configure Gunicorn as a systemd service
echo "Configuring Gunicorn as a service..."
cat <<EOL | sudo tee /etc/systemd/system/gunicorn.service
[Unit]
Description=gunicorn daemon for Django project
After=network.target

[Service]
User=your_user
Group=www-data
WorkingDirectory=/path/to/your/project
ExecStart=/usr/local/bin/gunicorn --workers 3 --bind unix:/path/to/your/project/myproject.sock myproject.wsgi:application

[Install]
WantedBy=multi-user.target
EOL

# Enable and start the Gunicorn service
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn

# 8. Configure NGINX to proxy requests to Gunicorn
echo "Configuring NGINX..."
cat <<EOL | sudo tee /etc/nginx/sites-available/myproject
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://unix:/path/to/your/project/myproject.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias /path/to/your/project/static/;
    }

    location /media/ {
        alias /path/to/your/project/media/;
    }
}
EOL

# Enable the site in NGINX and restart the service
sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled
sudo systemctl restart nginx

# 9. Install and configure SSL (optional, with Let's Encrypt)
echo "Setting up SSL with Let's Encrypt..."
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com

# 10. Restart NGINX to apply SSL
sudo systemctl restart nginx

# 11. Run Django migrations (even for SQLite, just in case)
echo "Running migrations..."
python3 manage.py migrate

# 12. Check that everything is running
echo "Checking status of services..."
sudo systemctl status gunicorn
sudo systemctl status nginx

echo "Deployment completed successfully!"
