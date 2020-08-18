FROM pytorch/pytorch:latest

RUN apt-get update && apt-get install --no-install-recommends -y git wget
RUN wget http://www.cs.toronto.edu/~faghri/vsepp/runs.tar
RUN tar -xvf runs.tar
RUN rm -rf runs/coco* && rm -rf runs/f30k_vse0/ && rm -rf runs/f30k_order*/ && rm -rf runs/f30k_vse++/ && rm -rf runs/f30k_vse++_resnet* && rm -rf runs/f30k_vse++_vggfull_finetune/
RUN rm -rf runs.tar
ADD requirements.txt install.sh ./
RUN bash install.sh
RUN pip install -r requirements.txt
ADD VSEImageEncoder.py encode.yml ./

RUN python -c "import torchvision.models as models; model = getattr(models, 'vgg19')(pretrained=True).eval()"
ENTRYPOINT ["jina", "pod", "--uses", "encode.yml"]
