# This is the Dockerfile used by HistomicsTK people adding modules
#to Histomics TK shoudl extend from this image
#This image include itk(default modules and IOOpenSlide) and conda.
#To add modules to itk it is necesary to modify the base image, 
#rebuild it and extend from that modified image
 
#dsarchive/histomicstk:v0.1.4

FROM dsarchive/base_docker_image

MAINTAINER Deepak Chittajallu <deepak.chittajallu@kitware.com>

# git clone install ctk-cli
RUN git clone https://github.com/cdeepakroy/ctk-cli.git && cd ctk-cli \
    git checkout 979d8cb671060e787b725b0226332a72a551592e && \
    python setup.py install

# copy HistomicsTK files
ENV htk_path=$PWD/HistomicsTK
RUN mkdir -p $htk_path
COPY . $htk_path/
WORKDIR $htk_path

# Install HistomicsTK and its dependencies
RUN conda config --add channels https://conda.binstar.org/cdeepakroy && \
    conda install --yes pip libgfortran==1.0 openslide-python \
    --file requirements.txt --file requirements_c_conda.txt && \
    pip install -r requirements_c.txt && \
    # Install HistomicsTK
    python setup.py install && \
    # clean up
    conda clean -i -l -t -y && \
    rm -rf /root/.cache/pip/*



# pregenerate font cache
RUN python -c "from matplotlib import pylab"

# define entrypoint through which all CLIs can be run
WORKDIR $htk_path/server
ENTRYPOINT ["/build/miniconda/bin/python", "cli_list_entrypoint.py"]
