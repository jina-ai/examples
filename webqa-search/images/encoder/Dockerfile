FROM jinaai/jina:master-debian
FROM huggingface/transformers-cpu:latest

ENV TMP_WORKSPACE /tmp/jina/webqa/

ADD encoder.yml ./

ENTRYPOINT ["jina", "pod", "--yaml_path", "encoder.yml", "--timeout_ready", "60000"]