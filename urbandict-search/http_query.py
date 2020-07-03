__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import click

from jina.clients import py_client


def read_query_data(text):
    yield "{}".format(text).encode("utf8")


def print_topk(resp, word):
    for d in resp.search.docs:
        print(f"Ta-Dah🔮, here are what we found for: {word}")
        for idx, kk in enumerate(d.topk_results):
            score = kk.score.value
            if score <= 0.0:
                continue
            print(
                "{:>2d}:({:f}):{}".format(idx, score, kk.match_doc.buffer.decode())
            )


@click.command()
@click.argument("text")
@click.option("--host", default="localhost")
@click.option("--top_k", "-k", default=5)
def main(text, host, top_k):
    py_client(host=host, port_expose=56798).dry_run()
    ppr = lambda x: print_topk(x, text)

    py_client(host=host, port_expose=56798, top_k=top_k).search(
        input_fn=read_query_data(text), output_fn=ppr
    )


if __name__ == "__main__":
    main()
