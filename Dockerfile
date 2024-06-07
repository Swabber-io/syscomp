FROM ubuntu:latest

# Set working directory
WORKDIR '/usr/src/swabber'

# Install required system packages
RUN apt-get update --fix-missing && \
    apt-get install -y wget bzip2 ca-certificates curl git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python 
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Switch back to bash
SHELL ["/bin/bash","-c"]
