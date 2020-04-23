FROM jinaai/jina:master-debian

ENV TMP_WORKSPACE /tmp/jina/webqa/

ADD *.yml ./

ENTRYPOINT ["jina", "pod", "--yaml_path", "answer_meta_doc_indexer.yml"]