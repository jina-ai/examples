FROM jinaai/jina:master-debian

ENV TMP_WORKSPACE /tmp/jina/webqa/

ADD title_compound_chunk_indexer.yml ./

ENTRYPOINT ["jina", "pod", "--yaml_path", "title_compound_chunk_indexer.yml"]