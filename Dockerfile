FROM ubuntu:19.10

ENV DEBIAN_FRONTEND noninteractive

RUN set -ex && \
    apt-get update -qy --fix-missing && \
    apt-get upgrade -qy

RUN set -ex && \
    apt-get install -qy \
    libdw-dev \
    libasound2-dev \
    libsbc-dev \
    libspeexdsp-dev \
    libspeex-dev \
    libspeex1

RUN set -ex && \
    apt-get install -qy \
    autoconf \
    automake \
    autotools-dev \
    bison \
    build-essential \
    check \
    dbus-x11 \
    flex \
    fuse \
    libcairo2-dev \
    libcap-ng-dev \
    libdbus-glib-1-dev \
    libebook1.2-dev \
    libfuse-dev \
    libgirepository1.0-dev \
    libglib2.0-dev \
    libical-dev \
    libjson-c-dev \
    libreadline-dev \
    libtool \
    libudev-dev \
    python3-pip \
    udev \
    wget \
    apt-utils \
    git \
    dbus \
    socat

RUN set -ex && \
    apt-get install -qy \
    libssl-dev

RUN sed -i 's/^#user_allow_other$/user_allow_other/' /etc/fuse.conf

ENV GOSU_VERSION 1.11
RUN set -ex && \
	wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$(dpkg --print-architecture)" && \
	chmod +xs /usr/local/bin/gosu && \
	gosu nobody true

RUN mkdir /var/run/dbus

# preinstall some of the dependencies to speed up image creation
RUN set -ex && \
    pip3 install \
    bitstring==3.1.5 \
	bluetooth-mesh==0.1.27 \
	construct==2.9.52 \
	dbus-next==0.1.3 \
	docopt==0.6.2 \
	fusepy==3.0.1 \
	marshmallow==3.0.1 \
	pytest==4.1.0 \
	pytest-asyncio==0.10.0 \
	pytest-runner==4.2

RUN set -ex && \
	pip3 install \
	requests==2.22.0 \
	urllib3==1.25.3 \
	setuptools==41.0.1 \
	requests-toolbelt==0.9.1 \
	pyopenssl==19.0.0 \
	auth0-python==3.9.0 \
	packaging==19.0 \
	wcwidth==0.1.7 \
	idna==2.8 \
	certifi==2019.6.16 \
	chardet==3.0.4 \
	pyparsing==2.4.0 \
	pytest==5.0.1 \
	git+https://github.com/drbild/sslpsk.git@d88123a75786953f82f5e25d6c43d9d9259acb62 \
	pytest-paramark==0.1.0 \
	pytest-repeat==0.8.0

RUN set -ex && \
    apt-get install -qy \
    strace \
    vim \
    lcov

RUN groupadd -r -g 1000 user
RUN useradd -r -u 1000 -g user -d /home/user -m user

COPY docker-dbus.conf /etc/dbus-1/system.d/docker-dbus.conf

USER user

COPY --chown=user:user ell /home/user/ell
COPY --chown=user:user bluez /home/user/bluez

RUN set -ex && \
	cd /home/user/bluez && \
	./bootstrap-configure --disable-systemd && \
	make -j$(nproc) && \
	gosu root make install

RUN set -ex && \
	cd /home/user/bluez && \
	gosu root install -m 0666 ./mesh/bluetooth-mesh.conf /etc/dbus-1/system.d/bluetooth-mesh.conf

COPY --chown=user:user . /usr/src/bluez-tests

RUN set -ex && \
    cd /usr/src/bluez-tests && \
    gosu root pip3 install --upgrade --trusted-host pypi.silvair.lan --extra-index-url http://pypi.silvair.lan --index-url http://pypi.silvair.lan/simple -e '.[doc,tools]'

ENTRYPOINT ["bash", "/usr/src/bluez-tests/docker-entrypoint.sh"]

CMD ["bash"]
