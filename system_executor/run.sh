#!/bin/bash

# Puente seguro entre Antigravity y el sistema host

case "$1" in
    stop-redis)
        sudo systemctl stop redis-server
        ;;
    start-redis)
        sudo systemctl start redis-server
        ;;
    restart-redis)
        sudo systemctl restart redis-server
        ;;
    docker-up)
        cd /opt/deco/agent_runtime/docker && sudo docker compose up -d
        ;;
    docker-down)
        cd /opt/deco/agent_runtime/docker && sudo docker compose down
        ;;
    kill-port)
        sudo fuser -k $2/tcp
        ;;
    *)
        echo "Comando no autorizado"
        exit 1
        ;;
esac
