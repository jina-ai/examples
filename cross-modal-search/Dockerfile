FROM pytorch/pytorch:1.6.0-cuda10.1-cudnn7-runtime

RUN apt-get update && apt-get install --no-install-recommends -y git wget

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

RUN python app.py -t index
