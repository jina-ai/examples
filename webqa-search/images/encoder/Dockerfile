FROM jinaai/jina:master-debian

ENV TMP_WORKSPACE /tmp/jina/webqa/

RUN pip install transformers tensorflow-gpu torch torchvision -i --no-cache-dir --compile

ADD encoder.yml ./

ENTRYPOINT ["jina", "pod", "--yaml_path", "encoder.yml", "--timeout_ready", "1200000000"]