#installs nginx compatible to python
sudo apt get install python-pip nginx

# starts the daemon nginx server
sudo /etc/init.d/nginx/ start

# deletes the default config file in sites-enabled folder of nginx
sudo rm /etc/nginx/sites-enabled/default

# creates new config file for nginx 
sudo touch /etc/nginx/sites-available/flask_settings

# creates a connection between two confi files
sudo ln -s /etc/nginx/sites-available/flask_setings /etc/nginx/sites-enabled/flask_setings

# config for nginx to pass traffic to gunicorn
echo "
server {
	location / {
		proxy_pass http://127.0.0.1:8000
		proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
}
}
" > /etc/nginx/sites-available/flask_settings

# restart the daemon nginx server
sudo /etc/init.d/nginx/ restart

# starts guncorn
gunicorn ilookup:app