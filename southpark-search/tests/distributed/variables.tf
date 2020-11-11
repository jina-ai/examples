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

variable "push_script" {
  description = "Path to script to build and push Docker image"
  type        = string
  default     = ""
}

variable "docker_username" {
  description = "Docker registry username"
  type        = string
  default     = ""
}

variable "docker_password" {
  description = "Docker registry password"
  type        = string
  default     = ""
}

variable "docker_host" {
  description = "Docker registry host"
  type        = string
  default     = "sample_docker_host"
}