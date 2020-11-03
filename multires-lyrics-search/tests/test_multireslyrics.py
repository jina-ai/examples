__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import json
import os
import sys
import subprocess

from jina.flow import Flow
import pytest

NUM_DOCS = 100
TOP_K = 3
INDEX_FLOW_FILE_PATH = "flows/index.yml"
QUERY_FLOW_FILE_PATH = "flows/query.yml"


def config(tmpdir):
    parallel = 2 if sys.argv[1] == "index" else 1

    os.environ.setdefault("JINA_MAX_DOCS", "100")
    os.environ.setdefault("JINA_PARALLEL", str(parallel))
    os.environ.setdefault("JINA_SHARDS", str(1))
    os.environ.setdefault("JINA_WORKSPACE", "./workspace")
    os.makedirs(os.environ["JINA_WORKSPACE"], exist_ok=True)

    os.environ["JINA_DATA_FILE"] = "tests/data-index.csv"
    os.environ["JINA_WORKSPACE"] = str(tmpdir)
    os.environ["JINA_PORT"] = str(45678)


def index_documents():
    f = Flow().load_config(INDEX_FLOW_FILE_PATH)

    with f:
        f.index_lines(
            filepath=os.environ["JINA_DATA_FILE"], batch_size=8, size=NUM_DOCS
        )


def call_api(
    url, payload=None, headers={"Content-Type": "application/json; charset=utf-8"}
):
    import requests

    return requests.post(url, data=json.dumps(payload), headers=headers).json()


def get_results(query, top_k=TOP_K):
    return call_api(
        "http://0.0.0.0:45678/api/search", payload={"top_k": top_k, "data": [query]}
    )


def get_flow():
    f = Flow().load_config(QUERY_FLOW_FILE_PATH)
    f.use_rest_gateway()
    return f


@pytest.fixture
def queries():
    return [
        (
            "Trudging slowly\n",
            [
                '"Trudging slowly over wet sand. Back to the bench where your clothes were stolen. This is a coastal town. That they forgot to close down. Armagedon - come armagedon come armagedon come. Everyday is like sunday. Everyday is silent and grey. Hide on a promanade. Etch on a post card:. How I dearly wish I was not here. In the seaside town. That they forgot to bomb. Come',
                "\"These are. These are days you'll remember. Never before and never since",
                "[ music: Dennis Drew/lyric: Natalie Merchant ]. . science. is truth for life. watch religion fall obsolete. science. will be truth for life. technology as nature. science. truth for life. in fortran tongue the. answer. with wealth and prominence. man so near perfection. possession. it's an absence of interim. secure no demurrer. defense against divine. defense against his true. image. human conflict number five. discovery. dissolved all illusion. mystery. destroyed with conclusion. and illusion never restored. any modern man can see. that religion is. obsolete. piety. obsolete. ritual. obsolete. martyrdom. obsolete. prophetic vision. obsolete. mysticism. obsolete. commitment. obsolete. sacrament. obsolete. revelation. obsolete.",
            ],
        ),
        ("I could feel at the time\n", ['"A lie to say', "\"Don't talk"]),
        (
            "I promise.\n",
            [
                "\"These are. These are days you'll remember. Never before and never since",
                "[ music: Dennis Drew/lyric: Natalie Merchant ]. . science. is truth for "
                "life. watch religion fall obsolete. science. will be truth for life. "
                "technology as nature. science. truth for life. in fortran tongue the. "
                "answer. with wealth and prominence. man so near perfection. possession. it's "
                "an absence of interim. secure no demurrer. defense against divine. defense "
                "against his true. image. human conflict number five. discovery. dissolved "
                "all illusion. mystery. destroyed with conclusion. and illusion never "
                "restored. any modern man can see. that religion is. obsolete. piety. "
                "obsolete. ritual. obsolete. martyrdom. obsolete. prophetic vision. obsolete. "
                "mysticism. obsolete. commitment. obsolete. sacrament. obsolete. revelation. "
                "obsolete.",
                "\"Don't talk",
            ],
        ),
    ]


def test_query(tmpdir, queries):
    config(tmpdir)
    index_documents()
    f = get_flow()
    with f:
        for query, exp_result in queries:
            output = get_results(query)
            matches = output["search"]["docs"][0]["matches"]
            assert len(matches) <= TOP_K  # check the number of docs returned
            result = []
            for match in matches:
                # the lyrics text in the .csv is the fourth column
                match_text = match["text"].split(",")[3]
                result.append(match_text)
            assert result == exp_result
