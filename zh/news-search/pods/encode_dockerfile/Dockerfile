FROM pytorch/pytorch:latest

RUN pip install transformers --no-cache-dir --compile
RUN python -c "from transformers import *; x='hfl/chinese-roberta-wwm-ext'; BertModel.from_pretrained(x); BertTokenizer.from_pretrained(x)"

RUN pip install jina==0.3.8

ENV TMP_WORKSPACE '/tmp/jina/news/'
ENV BATCH_SIZE 2

ADD *.py *.yml ./

ENTRYPOINT ["jina", "pod", "--yaml-path", "roberta.yml"]
