#!/bin/bash

# Must exit and fail to build if any command fails
set -eo pipefail

# Tidy up and keep image small
apt-get clean -y
micromamba clean -ay

# Remove build scripts
scripts_dir="/opt/ai-dock/bin/build/"

# Remove this layer's scripts
rm -rf ${scripts_dir}layer0

# Remove parent directory if this is the last build layer
if [[ $(ls -l ${scripts_dir} | grep -c ^d) -eq 0 ]]; then
    rm -rf ${scripts_dir}
fi