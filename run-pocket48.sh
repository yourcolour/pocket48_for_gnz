#!/bin/sh
echo "start coolq server"
python coolq_http_server.py

echo "start service"
python main.py

