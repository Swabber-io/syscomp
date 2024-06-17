FROM ubuntu:latest

# Set working directory
WORKDIR '/usr/src/swabber'

# Install required system packages
RUN apt-get update --fix-missing && \
    apt-get install -y wget bzip2 ca-certificates curl git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Miniconda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    /opt/conda/bin/conda clean -a && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc

# Set environment variables
ENV PATH /opt/conda/bin:$PATH

# Create environment from yaml file
RUN conda create -n swabber python=3.12

# Set up bash to run with luxai_s2 conda environment
SHELL ["conda", "run", "-n", "swabber", "/bin/bash", "-c"]

# Set PATH for the Conda environment
ENV PATH /opt/conda/envs/swabber/bin:$PATH

# Install ipykernel
RUN pip install --no-cache-dir ipykernel

# Add Lux conda env to ipykernel to run Notebooks
RUN python -m ipykernel install --user --name=swabber --display-name "Swabber"

# Install Lux AI Python packages
RUN pip install --no-cache-dir --upgrade pip

# Install basic dev tools, like GCC
RUN apt update -y && apt upgrade -y && apt install -y build-essential && apt-get install -y manpages-dev

# Switch back to bash
SHELL ["/bin/bash","-c"]

# Initialize conda
RUN conda init

# Activate swabber environment on bash startup
RUN echo 'conda activate swabber' >> ~/.bashrc

# Install requirements
RUN pip install --no-cache-dir mesa



