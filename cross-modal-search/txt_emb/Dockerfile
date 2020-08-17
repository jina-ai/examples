FROM pytorch/pytorch:latest

RUN apt-get update && apt-get install --no-install-recommends -y git wget
RUN wget http://www.cs.toronto.edu/~faghri/vsepp/runs.tar
RUN wget http://www.cs.toronto.edu/~faghri/vsepp/vocab.tar
RUN tar -xvf runs.tar
RUN tar -xvf vocab.tar
RUN rm -rf runs/coco* && rm -rf runs/f30k_vse0/ && rm -rf runs/f30k_order*/ && rm -rf runs/f30k_vse++/ && rm -rf runs/f30k_vse++_resnet* && rm -rf runs/f30k_vse++_vggfull_finetune/
RUN rm -rf vocab/coco* && rm -rf vocab/f8k* && rm -rf vocab/10crop*/ && rm -rf vocab/f30k_precomp*
RUN rm -rf runs.tar
RUN rm -rf vocab.tar
ADD requirements.txt install.sh ./
RUN apt-get install --no-install-recommends -y gcc
RUN pip install -r requirements.txt
RUN bash install.sh
ADD VSETextEncoder.py encode.yml ./

ENTRYPOINT ["jina", "pod", "--uses", "encode.yml", "--timeout-ready", "60000"]
