FROM pytorch/pytorch:latest

RUN apt-get update && apt-get install --no-install-recommends -y git wget gcc

RUN wget http://www.cs.toronto.edu/~faghri/vsepp/runs.tar && wget http://www.cs.toronto.edu/~faghri/vsepp/vocab.tar && \
tar -xvf runs.tar && tar -xvf vocab.tar && rm -rf runs/coco* && rm -rf runs/f30k_vse0/ && rm -rf runs/f30k_order*/ && \
rm -rf runs/f30k_vse++/ && rm -rf runs/f30k_vse++_resnet* && rm -rf runs/f30k_vse++_vggfull_finetune/ && \
rm -rf vocab/coco* && rm -rf vocab/f8k* && rm -rf vocab/10crop*/ && rm -rf vocab/f30k_precomp* && \
rm -rf runs.tar && rm -rf vocab.tar

COPY . ./

RUN git clone https://github.com/JoanFM/vsepp.git -b works && mv vsepp/model.py . && mv vsepp/vocab.py . && rm -rf vsepp && \
pip install -r requirements.txt && \
python -c "import torchvision.models as models; model = getattr(models, 'vgg19')(pretrained=True).eval()" && \
python -c "import nltk; nltk.download('punkt')"

RUN pip install pytest && pytest -v -s

ENTRYPOINT ["jina", "pod", "--uses", "config.yml"]
