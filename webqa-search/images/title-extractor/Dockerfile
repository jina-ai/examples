FROM jinaai/jina:master-debian

ENV TMP_WORKSPACE /tmp/jina/webqa/

ADD extractor.py title_extractor.yml ./

ENTRYPOINT ["jina", "pod", "--yaml_path", "title_extractor.yml"]