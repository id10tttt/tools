# Ubuntu 下面安装 geenplum-db 集群

* 安装依赖
        
        apt install openssh-server vim net-tools python3-pip -y

* 更改 Ubuntu 源
        
        # 默认注释了源码镜像以提高 apt update 速度，如有需要可自行取消注释
        deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic main restricted universe multiverse
        # deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic main restricted universe multiverse
        deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-updates main restricted universe multiverse
        # deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-updates main restricted universe multiverse
        deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-backports main restricted universe multiverse
        # deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-backports main restricted universe multiverse
        deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-security main restricted universe multiverse
        # deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-security main restricted universe multiverse
        
        # 预发布软件源，不建议启用
        # deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-proposed main restricted universe multiverse
        # deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-proposed main restricted universe multiverse

 <hr/>
 
* 更改 pip

        mkdir ~/.pip
        cd ~/.pip
        echo "[global]
        index-url = https://pypi.tuna.tsinghua.edu.cn/simple" > pip.conf
        
* 使用到的 hosts

|IP | Name|
|:---:|:---:|
|192.168.50.86|mdw|
|192.168.50.81|sdw1
|192.168.50.250|sdw2
|192.168.50.134|sdw3
 
 <hr/>
* 新建用户: gpadmin

        groupadd -g 530 gpadmin
        useradd -g 530 -u 530 -m -d /home/gpadmin -s /bin/bash gpadmin
        chown -R gpadmin:gpadmin /home/gpadmin
        
        usermod -a -G sudo gpadmin

* 分别在每一个 node 上面执行： ssh-keygen 生成 key

        ssh-keygen -t rsa

* 复制保存为 authorized_keys

        cat ~/.ssh/id_rsa.pub | ssh gpadmin@mdw "cat - > authorized_keys"
 
* 安装 greenplum-db

        sudo add-apt-repository ppa:greenplum/db
        sudo apt update
        sudo apt install greenplum-db

* 新建 /home/gpadmin/hostlist
        
        mdw
        sdw1
        sdw2
        sdw3
* 新建 /home/gpadmin/seg_hosts

        sdw1
        sdw2
        sdw3
        
* 测试
        
        source /home/gpadmin/greenplum-db/greenplum_path.sh 
        gpssh-exkeys -f /home/gpadmin/hostlist
    * 如果不执行
    
            source /home/gpadmin/greenplum-db/greenplum_path.sh
    会报错没有 **gpssh-exkeys**

* 交换成功后，后续就可以使用一些命令执行批量操作
    * 使用gpssh-exkeys命令时一定要使用gpadmin用户，
    因为会在/home/gpadmin/.ssh中生成ssh的免密码登录秘钥，
    如果使用其它账号登录，则会在其它账号下生成密钥，
    在gpadmin账号下就无法使用gpssh的批处理命令
    
            gpssh -f /home/gpadmin/hostlist
    * 批量发送
            
            gpscp -f /home/gpadmin/seg_hosts file_u_want_2_send =:/home/gpadmin
    * 批量安装， **gpssh**批量执行命令
            
            gpssh -f /home/gpadmin/seg_hosts
            sudo apt install greenplum-db -y
* 初始化安装数据库
        
         gpssh -f /home/gpadmin/hostlist
         mkdir gpdata
         cd gpdata
         mkdir gpmaster gpdatap1 gpdatap2 gpdatam1 gpdatam2
         
    * 在master节点上修改.bash_profile配置环境变量，并发送给其他子节点，确保这些环境变量生效
            
            vim .bash_profile 
            source /opt/gpadmin/greenplum-db/greenplum_path.sh
            export MASTER_DATA_DIRECTORY=/home/gpadmin/gpdata/gpmaster/gpseg-1
            export PGPORT=15432
            export PGDATABASE=testDB
            source .bash_profile
    * 同步
            
            gpscp -f /home/gpadmin/seg_hosts /home/gpadmin/.bash_profile
            gpssh -f /home/gpadmin/seg_hosts
            source .bash_profile
* 初始化配置文件
        
        vim /home/gpadmin/gpinitsystem_config
        
        ARRAY_NAME="Greenplum"
        MACHINE_LIST_FILE=/home/gpadmin/seg_hosts
        
        # Segment 的名称前缀
        SEG_PREFIX=gpseg
        # Primary Segment 起始的端口号
        PORT_BASE=33000
        # 指定 Primary Segment 的数据目录
        declare -a DATA_DIRECTORY=(/home/gpadmin/gpdata/gpdatap1 /home/gpadmin/gpdata/gpdatap2)
        # Master 所在机器的 Hostname
        MASTER_HOSTNAME=mdw
        # 指定 Master 的数据目录
        MASTER_DIRECTORY=/home/gpadmin/gpdata/gpmaster
        # Master 的端口 
        MASTER_PORT=15432
        # 指定Bash的版本
        TRUSTED_SHELL=/usr/bin/ssh
        # Mirror Segment起始的端口号
        MIRROR_PORT_BASE=43000
        # Primary Segment 主备同步的起始端口号
        REPLICATION_PORT_BASE=34000
        # Mirror Segment 主备同步的起始端口号
        MIRROR_REPLICATION_PORT_BASE=44000
        # Mirror Segment 的数据目录
        declare -a MIRROR_DATA_DIRECTORY=(/home/gpadmin/gpdata/gpdatam1 /home/gpadmin/gpdata/gpdatam2)

* 初始化数据库

        gpinitsystem -c /home/gpadmin/gpinitsystem_config -s sdw3
    * 其中，-s sdw3是指配置master的standby节点

* 使用 psql 远程访问

        cd /home/gpadmin/gpdata/gpmaster/default/gpseg-1/

    * 修改postgresql.conf
    
            listen_addresses = '*'
    * 修改 pg_hba.conf
            
            host	all			all		0.0.0.0/0       md5
    * 重启
            
            gpstop -u

<hr/>
* 如果出现 reduce shared memory 错误
        
        更改:
        gpconfig -c shared_buffers -v 1000MB