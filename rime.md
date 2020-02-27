# ibus-rime

* 下载 词库(http://thuocl.thunlp.org/)

* curl -fsSL https://git.io/rime-install | bash

* bash plum/rime-install emoji

* bash plum/rime-install emoji:customize:schema=luna_pinyin_simp

* 横屏
	
	tee ~/.config/ibus/rime/build/ibus_rime.yaml <<-'EOF'
	style:
   		horizontal: true
	EOF

* 每排字数 ~/.config/ibus/rime/default.custom.yaml
	
	patch:
  		"menu/page_size": 9
* 安装字体
	
	#!/usr/bin/env bash
	for x in `ls | grep -v .sh`;
	do
		echo $x
		rime_dict_manager --import luna_pinyin /home/jx/Videos/txt/$x
	done

* 同步
	* 在 ~/.config/ibus/rime/installation.yaml 里面添加
	sync_dir: "custome_save_config_path"
	* 部署 > 同步
	* 部署 > 同步 > 部署
