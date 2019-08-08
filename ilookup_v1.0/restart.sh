#!/bin/bash
sudo /etc/init.d/nginx restart
cd /codecommit/ilookup/
source venv bin activate
cd ilookup_v1.0/
gunicorn ilookup:app
