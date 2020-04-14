FROM pytorch/pytorch:1.4-cuda10.1-cudnn7-runtime

RUN pip install transformers --no-cache-dir --compile && \
    python -c "from transformers import *; x='hfl/chinese-roberta-wwm-ext'; BertModel.from_pretrained(x); BertTokenizer.from_pretrained(x)"

# jina is not public yet, so we add from the local host and install it
ADD jina .src

RUN pip install .src/.

ENV TMP_WORKSPACE /tmp/jina/news/
ENV BATCH_SIZE 8

ADD *.py *.yml ./

ENTRYPOINT ["jina", "pod", "--yaml_path", "encoder.yml"]