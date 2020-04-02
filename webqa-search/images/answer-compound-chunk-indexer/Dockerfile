FROM jinaai/jina:master-debian

ENV TMP_WORKSPACE /tmp/jina/webqa/

ADD answer_compound_chunk_indexer.yml ./

ENTRYPOINT ["jina", "pod", "--yaml_path", "answer_compound_chunk_indexer.yml"]