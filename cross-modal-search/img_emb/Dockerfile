FROM pytorch/pytorch:latest

RUN apt-get update && apt-get install --no-install-recommends -y git wget
RUN wget http://www.cs.toronto.edu/~faghri/vsepp/runs.tar && tar -xvf runs.tar && rm -rf runs/coco* && rm -rf runs/f30k_vse0/ && \
rm -rf runs/f30k_order*/ && rm -rf runs/f30k_vse++/ && rm -rf runs/f30k_vse++_resnet* && rm -rf runs/f30k_vse++_vggfull_finetune/ && \
rm -rf runs.tar

COPY . ./

RUN git clone https://github.com/JoanFM/vsepp.git -b works && mv vsepp/model.py . && rm -rf vsepp && \
pip install -r requirements.txt && \
python -c "import torchvision.models as models; model = getattr(models, 'vgg19')(pretrained=True).eval()"

RUN pip install pytest && pytest -v -s

ENTRYPOINT ["jina", "pod", "--uses", "config.yml"]
