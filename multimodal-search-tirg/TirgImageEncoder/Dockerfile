FROM jinaai/jina

# setup the workspace
COPY . /workspace
WORKDIR /workspace

# Get model and texts file
RUN apt-get -y update \
    && apt-get -y install wget \
    && wget https://storage.googleapis.com/image_retrieval_css/pretrained_models/checkpoint_css3d.pth \
    && wget https://github.com/bwanglzu/tirg-css/raw/main/texts.pkl

# install the third-party requirements
RUN pip install -r requirements.txt


ENTRYPOINT ["jina", "pod", "--uses", "config.yml"]