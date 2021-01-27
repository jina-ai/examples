variable "image_name" {
  description = "Name of Docker image"
  type        = string
  default = "jinaai/hub.app.distilbert-southpark"
}

variable "source_path" {
  description = "Path to Docker image source (Dockerfile)"
  type        = string
  default     = "tests/distributed/Dockerfile"
}

variable "tag" {
  description = "Tag to use for deployed Docker image"
  type        = string
  default     = "latest"
}

variable "repository_url" {
  description = "Tag to use for deployed Docker image"
  type        = string
  default     = ""
}

variable "region" {
  description = "Region AWS"
  type        = string
  default     = "us-east2"
}