FROM pytorch/manylinux-cuda100:latest

RUN pip3 install transformers --no-cache-dir --compile
RUN python3 -c "from transformers import BertModel, BertTokenizer; x='hfl/chinese-roberta-wwm-ext'; BertModel.from_pretrained(x); BertTokenizer.from_pretrained(x)"

RUN pip install jina==0.4.1

ENV TMP_WORKSPACE /tmp/jina/news/
ENV BATCH_SIZE 32

ADD *.py *.yml ./

ENTRYPOINT ["jina", "pod", "--uses", "roberta.yml"]
