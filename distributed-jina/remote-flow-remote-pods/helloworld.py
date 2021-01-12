import os
from typing import List
from contextlib import ExitStack

import requests
from jina.parsers import set_client_cli_parser
from jina.clients import Client
from jina.clients.sugary_io import _input_ndarray


def create_flow(flow_url: str, yamlspec: str, uses_files: List, pymodules_files: List):
    with ExitStack() as file_stack:
        files = []

        if yamlspec:
            files.append(('yamlspec', file_stack.enter_context(open(yamlspec, 'rb'))))
        if uses_files:
            files.extend([('uses_files', file_stack.enter_context(open(fname, 'rb')))
                          for fname in uses_files])
        if pymodules_files:
            files.extend([('pymodules_files', file_stack.enter_context(open(fname, 'rb')))
                          for fname in pymodules_files])
        if not files:
            return True
        try:
            r = requests.put(url=flow_url, files=files, timeout=5)
            if r.status_code == requests.codes.ok:
                print(f'Got status {r.json()["status"]} from remote!')
                return r.json()['flow_id']
            else:
                print('Remote Flow creation failed!')
        except requests.exceptions.RequestException as ex:
            print(f'something wrong on remote: {ex!r}')


def download_partial_data():
    _url = 'https://raw.githubusercontent.com/jina-ai/latency-tracking/main/original'
    for _type in ['index', 'query']:
        response = requests.get(f'{_url}/{_type}')
        with open(_type, 'wb') as f:
            f.write(response.content)


def erase_partial_data():
    for _type in ['index', 'query']:
        if os.path.isfile(_type):
            os.remove(_type)


def send_index_requests():
    args = set_client_cli_parser().parse_args(['--host', '0.0.0.0', '--port-expose', '45678'])
    grpc_client = Client(args)
    grpc_client.index(_input_ndarray('index'), batch_size=512)


def send_query_requests():
    args = set_client_cli_parser().parse_args(['--host', '0.0.0.0', '--port-expose', '45678'])
    grpc_client = Client(args)
    grpc_client.search(_input_ndarray('query'), batch_size=512)


def delete_flow(flow_url):
    try:
        r = requests.delete(url=flow_url)
        if r.status_code == requests.codes.ok:
            print(f'Successfully terminated remote Flow!\n')
    except requests.exceptions.RequestException as ex:
        print(f'something wrong on remote: {ex!r}')


def main():
    print('Creating a remote Flow..\n')
    flow_id = create_flow(flow_url='http://localhost:8000/flow/yaml',
                          yamlspec='helloworld.flow.index.yml',
                          uses_files=['helloworld.encoder.yml', 'helloworld.indexer.yml'],
                          pymodules_files=['components.py'])
    if flow_id:
        print(f'Flow successfully created with id {flow_id}\n\n')
    print('Downloading (partial) fashion-mnist data\n')
    download_partial_data()

    print('\n\nSending index requests')
    send_index_requests()

    print('\n\nSending query requests')
    send_query_requests()

    erase_partial_data()

    print('\n\nSending Flow termination request')
    delete_flow(flow_url=f'http://localhost:8000/flow?flow_id={flow_id}')


if __name__ == '__main__':
    main()
