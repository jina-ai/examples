# Distributed Jina

### Jina-daemon allows users to run jina remotely!


#### Steps to run this example -

1. Simulate remote environment locally using `docker-compose` .
   This creates 3 docker images with jina-daemon
   - remote-flow-remote-pods_flow_1
   - remote-flow-remote-pods_encoder_1
   - remote-flow-remote-pods_indexer_1
    ```bash
    docker-compose -f docker-compose.yml --project-directory . up --build -d
    ```

2.  Run `helloworld.py`.
    - Flow gets created in docker image `remote-flow-remote-pods_flow_1`
    - Flow creates a remote Pod for encoder in docker image `remote-flow-remote-pods_encoder_1`
    - Flow creates another remote Pod for indexer in docker image `remote-flow-remote-pods_indexer_1`
    - Jina client indexes helloworld documents on the remote Flow.
    - Jina client queries helloworld documents on the remote Flow.
    - Finally Flow gets terminated on the remote host.


3. To remove the docker images after tests -
    ```bash
    docker-compose -f docker-compose.yml --project-directory . down
    ```
