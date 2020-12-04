FROM jinaai/jina

# setup the workspace
COPY . /workspace
WORKDIR /workspace

# fix: add to path
ENV PATH="/root/.local/bin:${PATH}"

RUN apt-get update && \
    apt-get -y install wget && \
    apt-get -y install unzip

RUN cd models && \
    wget https://www.dropbox.com/s/sh2h9o5yd7v4ku6/bert-qa.zip && \
    mkdir bert-qa && \
    unzip bert-qa.zip -d bert-qa && \
    wget https://www.dropbox.com/s/12uiuumz4vbqvhk/2_finbert-qa-50_512_16_3e6.pt && \
    cd ..
    

# install the third-party requirements
RUN pip install -r requirements.txt

RUN pip uninstall -y dataclasses

# for testing the image
RUN pip install pytest && pytest

ENTRYPOINT ["jina", "pod", "--uses", "config.yml"]