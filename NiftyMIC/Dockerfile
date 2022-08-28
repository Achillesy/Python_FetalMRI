# docker build -t ahsoka/niftymic:0.1.0 .
FROM renbem/niftymic:latest
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=America/Chicago
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get -qq update && \
    apt-get -qq -y upgrade && \
    apt-get -qq install -y dcm2niix && \
    rm -rf /var/cache/apt/*