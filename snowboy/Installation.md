# Snowboy installation steps #

## Python wrapper from source (Ubuntu/Debian) ##

### Dependecies ###
- sudo apt install -y build-essential automake autoconf git

### Swig 3 version ###
- swig -version 
- if version < 3.0.10)
  - sudo apt install -y build-essential libpcre3-dev libboost-dev
  - sudo apt install -y autoconf automake libtool bison git python-dev python3-dev
  - git clone https://github.com/swig/swig.git /tmp/swig && cd /tmp/swig
  - ./autogen.sh && ./configure --prefix=/usr && make -j 4
  - sudo make install
  - swig -version
  - cd && rm -rf /tmp/swig

### Get source code ###
- git clone https://github.com/Kitt-AI/snowboy.git /tmp/snowboy && cd /tmp/snowboy

### Installation ###
- cd swig/Python
- make -j 4

### Move snowboy wrapper files ###
- cp snowboydetect.py MAYORDOMO_CLIENT_PATH/snowboy/
- cp _snowboydetect.so MAYORDOMO_CLIENT_PATH/snowboy/

### Remove git reposity ###
- cd && rm -rf /tmp/snowboy