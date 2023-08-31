#!/bin/bash

service="comfyui"
port=${COMFYUI_PORT:-8188}

if [[ -z $CF_QUICK_TUNNELS ]]; then
    printf "\n** You have not enabled Cloudflare quick tunnels **\n\n"
    printf "To enable, you can do the following:\n\n"
    printf "1. export CF_QUICK_TUNNELS=true\n"
    printf "2. supervisorctl restart %s\n\n" $service
    exit 1
fi

if [[ -f /var/log/supervisor/quicktunnel-${service}.log ]]; then
    grep -b0 -a0 'trycloudflare.com' /var/log/supervisor/quicktunnel-${service}.log
    if [[ $? -gt 0 ]]; then
        printf "\n** Something may have gone wrong setting up the %s tunnel **\n\n" $service
        printf "To set up manually you can run the following command:\n\n"
        printf "cloudflared tunnel --url localhost:%s > /var/log/supervisor/quicktunnel-%s.log 2>&1 &\n\n" $port $service
    fi
else
    printf "** The %s tunnel has not yet started **\n\n"
    if [[ -f /run/provisioning_script ]]; then
        printf "The container is still being provisioned. Check the logs for progress (logtail.sh)\n\n"
    else
        printf "Please wait a moment and try again.\n\n"
    fi
fi