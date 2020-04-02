FROM jinaai/jina:master-debian

ENV TMP_WORKSPACE /tmp/jina/webqa/

ADD extractor.py answer_extractor.yml ./

ENTRYPOINT ["jina", "pod", "--yaml_path", "answer_extractor.yml"]