#!/bin/bash
# 
# Builds a Docker image and pushes to an AWS ECR repository
#
# Invoked by the terraform-aws-ecr-docker-image Terraform module.
#
# Usage:
#
# # Acquire an AWS session token eg.
# $ ./push.sh . <aws-instance>/hello-world latest
#

set -e

source_path="$1"
repository_url="$2"
tag="${3:-latest}"

region="$(echo "$repository_url" | cut -d. -f4)"
image_name="$(echo "$repository_url" | cut -d/ -f2)"

(cd "$source_path" && docker build -t "$image_name" .)

aws ecr get-login-password --region "$region" | docker login --username AWS --password-stdin "$repository_url"
docker tag "$image_name" "$repository_url":"$tag"
docker push "$repository_url":"$tag"