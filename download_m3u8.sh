#!/usr/bin/env sh
read -p "Url: " url_download_path
read -p "File name: " file_name
ffmpeg -protocol_whitelist file,http,https,tcp,tls,crypto -i $url_download_path -c copy $file_name.mp4
