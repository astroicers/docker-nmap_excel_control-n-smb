Docker for nmap_excel_control and smb
===================

## Dockerfile
```
FROM alpine:3.6

RUN set -xe \
    && apk update \
    && apk upgrade \
    && apk add --update \
    && apk add samba \
    && apk add samba-common-tools \
    && apk add supervisor \
    && apk add python \
    && apk add python-dev \
    && apk add py-pip \
    && apk add build-base \
    && apk add vim \
    && apk add nmap \
    && pip install --upgrade pip \
    && pip install python-nmap \
    && pip install openpyxl \
    && pip install requests \
    && pip install BeautifulSoup4 \
    && pip install pymongo \
    && rm -rf /var/cache/apk/* \
    && mkdir /config /shared \
    && chmod 777 /shared

VOLUME /config /shared
COPY *.conf /config/
COPY *.py /config/
COPY nselib /usr/share/nmap/nselib
COPY scripts /usr/share/nmap/scripts
COPY nse_main.lua /usr/share/nmap

#RUN addgroup -g 1000 hmg \
#    && adduser -D -H -G hmg -s /bin/false -u 1000 hmg \
#    && echo -e "1qaz@WSX3edc\n1qaz@WSX3edc" | smbpasswd -a -s -c /config/smb.conf hmg

EXPOSE 137/udp 138/udp 139 445

ENTRYPOINT ["supervisord", "-c", "/config/supervisord.conf"]

#Reference pwntr/samba-alpine

```
## docker-compose.yml
```
version: '3.1'

services:
  mongo:
    container_name: mongo
    image: mongo
    restart: always
    ports:
      - '27017:27017'
    environment:
      MONGO_INITDB_ROOT_USERNAME: root
      MONGO_INITDB_ROOT_PASSWORD: example

  mongo-express:
    container_name: mongo_gui
    image: mongo-express
    restart: always
    ports:
      - 127.0.0.1:8081:8081
    environment:
      ME_CONFIG_MONGODB_ADMINUSERNAME: root
      ME_CONFIG_MONGODB_ADMINPASSWORD: example


  alpine:
    container_name: alpine
    image: astroicers/docker-nmap_excel_control-n-smb
    restart: always
    volumes:
      - /path/to/share/:/shared
    ports:
      - '139:139'
      - '445:445'
      - '137:137/udp'
      - '138:138/udp'
    network_mode: "host"
```
## Build 
```sh
docker build -t docker-nmap_excel_control-n-smb .
```

## Run
```sh
docker run -dit --net=host -v /path/to/share/:/shared --name scan_machine astroicers/docker-nmap_excel_control-n-smb
```

## HOW TO USE
```sh
docker exec -it scan_machine sh
cd /config
python muti_nmap_mongo.py -l [fiil_path] -t [number of threads]
```
## REFER TO

#### Docker hub
[pwntr/samba-alpine](https://hub.docker.com/r/pwntr/samba-alpine/)

#### Blog
[Vixual-安裝 Samba 伺服器](http://www.vixual.net/blog/archives/82)

[nixCraft-How to enable and start services on Alpine Linux](https://www.cyberciti.biz/faq/how-to-enable-and-start-services-on-alpine-linux/)

[掙扎的豬-python調用nmap進行掃描](https://www.cnblogs.com/darkpig/p/5691469.html)

[RUNOOB.COM-Python多執行緒](http://www.runoob.com/python/python-multithreading.html)

[MongoDB入門指南](https://jockchou.gitbooks.io/getting-started-with-mongodb/content/index.html)

[Python3及應用-pymongo](https://ecmadao.gitbooks.io/python3/content/pymongo.html)

[Docker Documentation-Docker run reference](https://docs.docker.com/engine/reference/run/#expose-incoming-ports)

[Docker -從入門到實踐-Docker Compose](https://yeasy.gitbooks.io/docker_practice/compose/)

## ABOUT
This is my dockerhub.
You can pull it easily.<br>
[docker-nmap_excel_control-n-smb](https://hub.docker.com/r/astroicers/docker-nmap_excel_control-n-smb/)
