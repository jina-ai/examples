__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import sys
import click

from jina.flow import Flow

MAX_DOCS = int(os.environ.get("JINA_MAX_DOCS", 50))
image_src = "data/**/*.jpg"


def config():
    num_encoders = 1 if sys.argv[1] == "index" else 1
    shards = 8

    os.environ["JINA_DATA_PATH"] = os.environ.get("JINA_DATA_PATH", "data/*/**.jpg")
    os.environ["JINA_SHARDS"] = str(num_encoders)
    os.environ["JINA_SHARDS_INDEXERS"] = str(shards)
    os.environ["JINA_WORKSPACE"] = "./workspace"
    os.environ["JINA_PORT"] = os.environ.get("JINA_PORT", str(45678))


# for index
def index(num_docs=MAX_DOCS):
    f = Flow.load_config("flows/index.yml")

    with f:
        f.index_files(image_src, request_size=64, read_mode="rb", size=num_docs)


# for search
def query():
    f = Flow.load_config("flows/query.yml")

    with f:
        f.block()


@click.command()
@click.option(
    "--task",
    "-t",
    type=click.Choice(
        ["index", "index_restful", "query", "query_restful", "dryrun"],
        case_sensitive=False,
    ),
)
@click.option("--num_docs", "-n", default=MAX_DOCS)
def main(task, num_docs):
    config()
    workspace = os.environ["JINA_WORKSPACE"]
    if "index" in task:
        if os.path.exists(workspace):
            print(
                f"\n +------------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                           | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again.  | \
                    \n |                                   🤖🤖🤖                                           | \
                    \n +------------------------------------------------------------------------------------+"
            )
            sys.exit(1)

    print(f"### task = {task}")
    if task == "index":
        index(num_docs)
    elif task == "query":
        if not os.path.exists(workspace):
            print(
                f"The directory {workspace} does not exist. Please index first via `python app.py -t index`"
            )
        query()


if __name__ == "__main__":
    main()
    # if len(sys.argv) < 2:
    # print('choose between "index" and "search" mode')
    # exit(1)
    # if sys.argv[1] == 'index':
    # config()
    # workspace = os.environ['JINA_WORKSPACE']
    # if os.path.exists(workspace):
    # print(f'\n +---------------------------------------------------------------------------------+ \
    # \n |                                   🤖🤖🤖                                        | \
    # \n | The directory {workspace} already exists. Please remove it before indexing again. | \
    # \n |                                   🤖🤖🤖                                        | \
    # \n +---------------------------------------------------------------------------------+')
    # sys.exit()
    # index()
    # elif sys.argv[1] == 'search':
    # config()
    # query()
    # else:
    # raise NotImplementedError(f'unsupported mode {sys.argv[1]}')
