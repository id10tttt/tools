#!/usr/bin/env bash

ROOT_PATH='/home/1di0t/Codes/91T'
B2B_PATH=$ROOT_PATH'/B2B/'
DWH_PATH=$ROOT_PATH'/DWH/'
BASE_PATH=$ROOT_PATH'/Base/'
ERP_PATH=$ROOT_PATH'/ERP/'
CRM_PATH=$ROOT_PATH'/CRM/'

git_pull_code() {
    code_path=$1
    cd $code_path
    echo "更新代码: "$code_path
    git fetch --all
    current_branch=`git branch | awk '{print $2}'`
    git config pull.rebase false
    git pull origin $current_branch
}

cron_update_git_code() {
    for path_id in $B2B_PATH $DWH_PATH $BASE_PATH $ERP_PATH $CRM_PATH
    do
        for git_path_id in `ls $path_id`
        do
            git_pull_code $path_id$git_path_id
        done
    done
}

cron_update_git_code
