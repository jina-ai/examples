FROM pytorch/pytorch:1.6.0-cuda10.1-cudnn7-runtime

RUN apt-get update && apt-get install --no-install-recommends -y git wget gcc unzip libmagic1

RUN wget http://www.cs.toronto.edu/~faghri/vsepp/runs.tar && tar -xvf runs.tar && rm -rf runs/coco* && rm -rf runs/f30k_vse0/ && \
rm -rf runs/f30k_order*/ && rm -rf runs/f30k_vse++/ && rm -rf runs/f30k_vse++_resnet* && rm -rf runs/f30k_vse++_vggfull_finetune/ && \
rm -rf runs.tar && \
wget http://www.cs.toronto.edu/~faghri/vsepp/vocab.tar && \
tar -xvf vocab.tar && \
rm -rf vocab/coco* && rm -rf vocab/f8k* && rm -rf vocab/10crop*/ && rm -rf vocab/f30k_precomp* && \
rm -rf runs.tar && rm -rf vocab.tar

COPY . /workspace
WORKDIR /workspace

RUN pip install -r requirements.txt && \
python -c "import torchvision.models as models; model = getattr(models, 'vgg19')(pretrained=True).eval()" && \
python -c "import nltk; nltk.download('punkt')"

ENV JINA_USES_VSE_IMAGE_ENCODER='yaml/hub-image-encoder.yml'
ENV JINA_USES_VSE_TEXT_ENCODER='yaml/hub-text-encoder.yml'
ENV JINA_SHARDS='2'

RUN ./prepare_data.sh && python app.py -t index -n 20000 && rm -rf data

EXPOSE 45678

ENTRYPOINT ["python", "app.py", "-t", "query-restful"]

LABEL author="Jina AI Dev-Team (dev-team@jina.ai)"
LABEL type="app"
LABEL kind="example"
LABEL avatar="None"
LABEL description="Jina App to do cross modal search between images and captions using Flickr8k and VSE++ models"
LABEL documentation="https://github.com/jina-ai/examples/tree/master/cross-modal-search"
LABEL keywords="[examples, cross-modal, VSE++, Flickr8k]"
LABEL license="apache-2.0"
LABEL name="crossmodalsearch"
LABEL platform="linux/amd64"
LABEL update="None"
LABEL url="https://github.com/jina-ai/examples/tree/master/cross-modal-search"
LABEL vendor="Jina AI Limited"
LABEL version="0.0.2"
