set -e

if [ "${PWD##*/}" != "southpark-search" ]
  then
    echo "test_integration.sh should only be run from the southpark-search base directory"
    exit 1
fi

# Setting env variables localls for this script
export $(grep -v '^#' tests/distributed/.env | xargs -d '\n')

docker-compose -f tests/distributed/docker-compose.yml --project-directory . up  --build -d

sleep 5

FLOW_ID=$(curl -s --request PUT "http://localhost:8000/v1/flow/yaml" \
    -H  "accept: application/json" \
    -H  "Content-Type: multipart/form-data" \
    -F "uses_files=@pods/encode.yml" \
    -F "uses_files=@pods/extract.yml" \
    -F "uses_files=@pods/index.yml" \
    -F "pymodules_files=@pods/text_loader.py" \
    -F "yamlspec=@tests/distributed/flow-query.yml"\
    | jq -r .flow_id)

echo "Successfully started the flow: ${FLOW_ID}"

curl --request POST -d '{"top_k": 10, "data": ["text:hey, dude"]}' -H 'Content-Type: application/json' '0.0.0.0:45678/api/search' | \
    jq -e ".search.docs[] | .matches[] | .text"

curl --request GET "http://0.0.0.0:8000/v1/flow/${FLOW_ID}" -H "accept: application/json" | jq -e ".status_code"

curl --request DELETE "http://0.0.0.0:8000/v1/flow?flow_id=${FLOW_ID}" -H "accept: application/json" | jq -e ".status_code"

docker-compose -f tests/distributed/docker-compose.yml --project-directory . down
