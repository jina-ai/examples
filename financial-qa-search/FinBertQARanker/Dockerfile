FROM jinaai/jina

RUN apt-get update && \
    apt-get -y install wget && \
    apt-get -y install unzip

COPY ./requirements.txt /
RUN pip install -r requirements.txt
RUN pip uninstall -y dataclasses
RUN pip install pytest

RUN wget https://www.dropbox.com/s/sh2h9o5yd7v4ku6/bert-qa.zip
RUN wget https://www.dropbox.com/s/12uiuumz4vbqvhk/2_finbert-qa-50_512_16_3e6.pt

# setup the workspace
COPY  . /workspace
WORKDIR /workspace

RUN if [ ! -d models ]; then \
    mkdir models/ && cd models/ && \
    mv /bert-qa.zip                   . && \
    mv /2_finbert-qa-50_512_16_3e6.pt . && \
    mkdir bert-qa && \
    unzip bert-qa.zip -d bert-qa/; \
fi

RUN pytest -v -s

ENTRYPOINT ["jina", "pod", "--uses", "config.yml"]
