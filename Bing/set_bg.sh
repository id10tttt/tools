#!/usr/bin/env bash

BASE_DIR='/home/1di0t/Pictures/Bing/'

random_pic_name=`ls $BASE_DIR | shuf -n1`

random_pic_path=$BASE_DIR$random_pic_name

set_background(){
	random_pic_name=`ls $BASE_DIR | shuf -n1`
	random_pic_path=$BASE_DIR$random_pic_name
	/usr/bin/gsettings set org.gnome.desktop.background picture-uri file://$random_pic_path
}

set_background

