FROM pytorch/pytorch:latest

ADD requirements.txt install.sh ./
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install --no-install-recommends -y git wget
RUN bash install.sh
RUN wget http://www.cs.toronto.edu/~faghri/vsepp/runs.tar
RUN tar -xvf runs.tar
RUN rm -rf runs/coco* && rm -rf runs/f30k_vse0/ && rm -rf runs/f30k_order*/ && rm -rf runs/f30k_vse++/ && rm -rf runs/f30k_vse++_resnet* && rm -rf runs/f30k_vse++_vggfull_finetune/
ADD VSEImageEncoder.py encode.yml

ENTRYPOINT ["jina", "pod", "--uses", "encode.yml"]
