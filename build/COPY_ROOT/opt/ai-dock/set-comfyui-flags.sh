#!/bin/bash

echo "$@" > /etc/comfyui_flags.conf
supervisorctl restart comfyui