# Add support for querying while indexing to Wikipedia Search

This is an example of using [Jina](http://www.jina.ai) to support both querying and indexing simultaneously in our [Wikipedia sentence search example](https://github.com/jina-ai/examples/tree/master/wikipedia-sentences). 

## Prerequisites

- Run and understand our [Wikipedia sentence search example](https://github.com/jina-ai/examples/tree/master/wikipedia-sentences)

## What is querying while indexing?

Querying while indexing means you are able to still query your data while new data is simultaneously being inserted (or updated, or deleted).
Jina achieves this with its the dump-reload feature.
For more in-depth technical information about how Jina achieves this, refer to [the docs](https://docs.jina.ai/chapters/dump-reload/)

## Configuration changes

This feature requires you to split the Flow, one for Indexing (and Updates, Deletes) and one for Querying, and have them running at the same time.
Also, you will need to replace the indexers in Flows.
The Index Flow (also referred to as the DBMS Flow) will require a `DBMSIndexer`, while the Query Flow will require `QueryIndexer`.
In our case we use `BinaryPbDBMSIndexer` and `CompoundQueryExecutor` (made up of `BinaryPbQueryIndexer` and `NumpyQueryIndexer`).
These are the standard Indexers provided by Jina, but we also provide:

- [PostgreSQLDBMSIndexer](https://github.com/jina-ai/jina-hub/tree/master/indexers/dbms/PostgreSQLIndexer), which leverages the resilience of PostgreSQL as a storage engine
- [AnnoyQueryIndexer](https://github.com/jina-ai/jina-hub/tree/master/indexers/query/AnnoyQueryIndexer), which uses the [`annoy`](https://github.com/spotify/annoy) algorithm to provide faster query results

You can check the `flows` and `pods` directories for the changes to the files.

## Running the example

In order to run the example you will need to do the following:

1. In one terminal session, run `jinad`.

    `JinaD` is our platform for running Jina services (Flows, Pods) remotely, wherever you want to run them. In this example, we use `JinaD` to serve the two Flows (Index and Query). You can read more about it [in the docs](https://docs.jina.ai/chapters/remote/jinad).

2. In another terminal, run `python app.py -t flows`

    This will create the two Flows, and then repeatedly do the following, every 20 seconds:

    1. index 5 Documents
    2. send a `DUMP` request to the DBMS (Index) Flow to dump its data to a specific location
    3. send a `ROLLING_UPDATE` request to the Query Flow to take down its Indexers and start them again, with the new data located at the respective path
    
    **Notice** the logs of the operations.

    **Warning**: the data file is limited to 200 documents. Once that is exhausted, the process will terminate. If you want to use the entire dataset, run `bash get_data.sh` and then modify the `DATA_FILE` constant to point to that file.

3. Finally, in another terminal, run `python app.py -t client`

    This will prompt you for a query, send the query to the Query Flow, and then show you the results.

    **Notice** how the number of total matches grows as step **2** gets repeated.

    Alternatively, you can query the REST API with whatever client you are comfortable with, `cURL`, `Postman` etc.

### Next Steps

- ❓ Join our [Slack](https://slack.jina.ai/) to ask any further questions
- 📚 Check our [documentation](https://docs.jina.ai/index.html) for more information
- 🌟 [Star us](https://github.com/jina-ai/jina) on GitHub
