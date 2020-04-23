FROM jinaai/jina:master-debian

ENV TMP_WORKSPACE /tmp/jina/news/

ADD *.yml ./

ENTRYPOINT ["jina", "pod", "--yaml_path", "compound_chunk_indexer.yml"]