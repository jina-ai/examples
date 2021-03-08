FROM jinaai/jina

RUN apt-get -y update && apt-get install -y git wget gcc unzip libmagic1

COPY . /workspace
WORKDIR /workspace

# install the third-party requirements
RUN pip install git+https://github.com/openai/CLIP.git click && pip uninstall -y jina && pip install -r requirements.txt && pip uninstall -y dataclasses && python -c "import clip; clip.load('ViT-B/32')"

ENV JINA_IMAGE_ENCODER='yaml/clip/hub-image-encoder.yml'
ENV JINA_TEXT_ENCODER='yaml/clip/hub-text-encoder.yml'
ENV JINA_SHARDS='2'

RUN ./prepare_data.sh && python app.py -t index -n 20000 && rm -rf data

EXPOSE 45678

ENTRYPOINT ["python", "app.py", "-t", "query"]

LABEL author="Jina AI Dev-Team (dev-team@jina.ai)"
LABEL type="app"
LABEL kind="example"
LABEL avatar="None"
LABEL description="Jina App to do cross modal search between images and captions using Flickr8k and CLIP models"
LABEL documentation="https://github.com/jina-ai/examples/tree/master/cross-modal-search"
LABEL keywords="[examples, cross-modal, CLIP, Flickr8k, Computer Vision, NLP]"
LABEL license="apache-2.0"
LABEL name="crossmodalsearch"
LABEL platform="linux/amd64"
LABEL update="None"
LABEL url="https://github.com/jina-ai/examples/tree/master/cross-modal-search"
LABEL vendor="Jina AI Limited"
LABEL version="0.0.3"
