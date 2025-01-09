#!/usr/bin/env bash
BASE_DIR="${HOME}/Pictures/Bing/"

random_pic_name=$(ls $BASE_DIR | shuf -n1)

random_pic_path=$BASE_DIR$random_pic_name

set_background(){
  random_pic_name=$(ls $BASE_DIR | shuf -n1)
  random_pic_path=$BASE_DIR$random_pic_name
  picture_uri="file://${random_pic_path}"
  /usr/bin/gsettings set org.gnome.desktop.background picture-uri-dark "${picture_uri}"
  /usr/bin/gsettings set org.gnome.desktop.background picture-uri "${picture_uri}"
}

set_background
