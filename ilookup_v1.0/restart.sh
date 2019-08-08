#!/bin/bash
cd /home/ubuntu/CodeCommit/ilookup/ilookup_v1.0
gunicorn ilookup:app
