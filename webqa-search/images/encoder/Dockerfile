FROM jinaai/jina:master-debian

ENV TMP_WORKSPACE /tmp/jina/webqa/

RUN pip install -i  https://pypi.tuna.tsinghua.edu.cn/simple transformers --no-cache-dir --compile

ADD encoder.yml ./

ENTRYPOINT ["jina", "pod", "--yaml_path", "encoder.yml", "--timeout_ready", "60000"]