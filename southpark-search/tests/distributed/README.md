<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Terraform for setting up cloud infrastructure](#terraform-for-setting-up-cloud-infrastructure)
- [Creation of resources produces log:](#creation-of-resources-produces-log)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Terraform for setting up cloud infrastructure

Configure AWS provider for Terraform as per README:
https://github.com/jina-ai/cloud-ops

We fetch the ip adresses of the pod-machines in the cloud VPN, putting them into JINA_ENCODER_HOST and JINA_INDEX_HOST environment variables
Send the curl command below to the jinad on the flow machine in order to spin up the flow:
```
curl -s --request PUT "http://localhost:8000/v1/flow/yaml" \
    -H  "accept: application/json" \
    -H  "Content-Type: multipart/form-data" \
    -F "uses_files=@pods/encode.yml" \
    -F "uses_files=@pods/extract.yml" \
    -F "uses_files=@pods/index.yml" \
    -F "pymodules_files=@pods/text_loader.py" \
    -F "yamlspec=@tests/distributed/flow-query.yml"
```

Docker image generated via `tests/distributed/Dockerfile` jinad will automatically be running on each machine brought up by Terraform.

The provisioning sets up ECS cluster managed with Fargate setting up three containers:
1. Indexer
2. Encoder
3. Flow
The ECS Service needs an ECS Cluster and Task, which has been configured in the script. 
This further has a Load Balancer and Security Group attached to it.

The terraform script here spins up AWS resources, this is the output of running
`terraform apply`:

<details> 
<summary>Click here to see the outputs </summary>

```
data.aws_iam_policy_document.assume_role_policy: Refreshing state...

An execution plan has been generated and is shown below.
Resource actions are indicated with the following symbols:
  + create
 <= read (data resources)


Terraform will perform the following actions:

  # data.aws_subnet_ids.default will be read during apply
  # (config refers to values not yet known)
 <= data "aws_subnet_ids" "default"  {
      + id     = (known after apply)
      + ids    = (known after apply)
      + tags   = (known after apply)
      + vpc_id = (known after apply)
    }

  # aws_alb.application_load_balancer will be created
  + resource "aws_alb" "application_load_balancer" {
      + arn                        = (known after apply)
      + arn_suffix                 = (known after apply)
      + dns_name                   = (known after apply)
      + drop_invalid_header_fields = false
      + enable_deletion_protection = false
      + enable_http2               = true
      + id                         = (known after apply)
      + idle_timeout               = 60
      + internal                   = (known after apply)
      + ip_address_type            = (known after apply)
      + load_balancer_type         = "application"
      + name                       = "southpark-lb-tf"
      + security_groups            = (known after apply)
      + subnets                    = (known after apply)
      + vpc_id                     = (known after apply)
      + zone_id                    = (known after apply)

      + subnet_mapping {
          + allocation_id = (known after apply)
          + subnet_id     = (known after apply)
        }
    }

  # aws_default_vpc.default_vpc will be created
  + resource "aws_default_vpc" "default_vpc" {
      + arn                              = (known after apply)
      + assign_generated_ipv6_cidr_block = (known after apply)
      + cidr_block                       = (known after apply)
      + default_network_acl_id           = (known after apply)
      + default_route_table_id           = (known after apply)
      + default_security_group_id        = (known after apply)
      + dhcp_options_id                  = (known after apply)
      + enable_classiclink               = (known after apply)
      + enable_classiclink_dns_support   = (known after apply)
      + enable_dns_hostnames             = (known after apply)
      + enable_dns_support               = true
      + id                               = (known after apply)
      + instance_tenancy                 = (known after apply)
      + ipv6_association_id              = (known after apply)
      + ipv6_cidr_block                  = (known after apply)
      + main_route_table_id              = (known after apply)
      + owner_id                         = (known after apply)
    }

  # aws_ecr_repository.southpark will be created
  + resource "aws_ecr_repository" "southpark" {
      + arn                  = (known after apply)
      + id                   = (known after apply)
      + image_tag_mutability = "MUTABLE"
      + name                 = "sp-repo-db"
      + registry_id          = (known after apply)
      + repository_url       = (known after apply)
      + tags                 = {
          + "Name" = "southpark_repo"
        }
    }

  # aws_ecs_cluster.southpark_cluster will be created
  + resource "aws_ecs_cluster" "southpark_cluster" {
      + arn  = (known after apply)
      + id   = (known after apply)
      + name = "southpark_cluster"

      + setting {
          + name  = (known after apply)
          + value = (known after apply)
        }
    }

  # aws_ecs_service.southpark_service will be created
  + resource "aws_ecs_service" "southpark_service" {
      + cluster                            = (known after apply)
      + deployment_maximum_percent         = 200
      + deployment_minimum_healthy_percent = 100
      + desired_count                      = 3
      + enable_ecs_managed_tags            = false
      + health_check_grace_period_seconds  = 30
      + iam_role                           = (known after apply)
      + id                                 = (known after apply)
      + launch_type                        = "FARGATE"
      + name                               = "southpark_service"
      + platform_version                   = (known after apply)
      + scheduling_strategy                = "REPLICA"
      + task_definition                    = (known after apply)

      + load_balancer {
          + container_name   = "southpark_task"
          + container_port   = 45678
          + target_group_arn = (known after apply)
        }

      + network_configuration {
          + assign_public_ip = true
          + security_groups  = (known after apply)
          + subnets          = (known after apply)
        }

      + placement_strategy {
          + field = (known after apply)
          + type  = (known after apply)
        }
    }

  # aws_ecs_task_definition.southpark_task will be created
  + resource "aws_ecs_task_definition" "southpark_task" {
      + arn                      = (known after apply)
      + container_definitions    = jsonencode(
            [
              + {
                  + cpu          = 128
                  + essential    = true
                  + image        = "416454113568.dkr.ecr.us-east-2.amazonaws.com/sp-db"
                  + memory       = 1024
                  + name         = "southpark_task"
                  + portMappings = [
                      + {
                          + containerPort = 45678
                        },
                    ]
                },
              + {
                  + cpu          = 128
                  + essential    = true
                  + image        = "416454113568.dkr.ecr.us-east-2.amazonaws.com/sp-db"
                  + memory       = 1024
                  + name         = "encoder"
                  + portMappings = [
                      + {
                          + containerPort = 49152
                        },
                    ]
                },
              + {
                  + cpu          = 128
                  + essential    = true
                  + image        = "416454113568.dkr.ecr.us-east-2.amazonaws.com/sp-db"
                  + memory       = 1024
                  + name         = "indexer"
                  + portMappings = [
                      + {
                          + containerPort = 49153
                        },
                    ]
                },
            ]
        )
      + cpu                      = "512"
      + execution_role_arn       = (known after apply)
      + family                   = "southpark_task"
      + id                       = (known after apply)
      + memory                   = "1024"
      + network_mode             = "awsvpc"
      + requires_compatibilities = [
          + "FARGATE",
        ]
      + revision                 = (known after apply)
    }

  # aws_iam_role.ecsExecutionRole will be created
  + resource "aws_iam_role" "ecsExecutionRole" {
      + arn                   = (known after apply)
      + assume_role_policy    = jsonencode(
            {
              + Statement = [
                  + {
                      + Action    = "sts:AssumeRole"
                      + Effect    = "Allow"
                      + Principal = {
                          + Service = "ecs-tasks.amazonaws.com"
                        }
                      + Sid       = ""
                    },
                ]
              + Version   = "2012-10-17"
            }
        )
      + create_date           = (known after apply)
      + force_detach_policies = false
      + id                    = (known after apply)
      + max_session_duration  = 3600
      + name                  = "ecsExecutionRole"
      + path                  = "/"
      + unique_id             = (known after apply)
    }

  # aws_iam_role_policy_attachment.ecsTaskExecutionRole_policy will be created
  + resource "aws_iam_role_policy_attachment" "ecsTaskExecutionRole_policy" {
      + id         = (known after apply)
      + policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
      + role       = "ecsExecutionRole"
    }

  # aws_lb_listener.lsr will be created
  + resource "aws_lb_listener" "lsr" {
      + arn               = (known after apply)
      + id                = (known after apply)
      + load_balancer_arn = (known after apply)
      + port              = 45678
      + protocol          = "HTTP"
      + ssl_policy        = (known after apply)

      + default_action {
          + order            = (known after apply)
          + target_group_arn = (known after apply)
          + type             = "forward"
        }
    }

  # aws_lb_target_group.target_group will be created
  + resource "aws_lb_target_group" "target_group" {
      + arn                                = (known after apply)
      + arn_suffix                         = (known after apply)
      + deregistration_delay               = 90
      + id                                 = (known after apply)
      + lambda_multi_value_headers_enabled = false
      + load_balancing_algorithm_type      = (known after apply)
      + name                               = "target-gp"
      + port                               = 45678
      + protocol                           = "HTTP"
      + proxy_protocol_v2                  = false
      + slow_start                         = 0
      + target_type                        = "ip"
      + vpc_id                             = (known after apply)

      + health_check {
          + enabled             = true
          + healthy_threshold   = 3
          + interval            = 80
          + matcher             = "200,301,302,404"
          + path                = "/"
          + port                = "traffic-port"
          + protocol            = "HTTP"
          + timeout             = 60
          + unhealthy_threshold = 2
        }

      + stickiness {
          + cookie_duration = (known after apply)
          + enabled         = (known after apply)
          + type            = (known after apply)
        }
    }

  # aws_security_group.load_balancer_security_group will be created
  + resource "aws_security_group" "load_balancer_security_group" {
      + arn                    = (known after apply)
      + description            = "control access to the ALB"
      + egress                 = [
          + {
              + cidr_blocks      = [
                  + "0.0.0.0/0",
                ]
              + description      = ""
              + from_port        = 0
              + ipv6_cidr_blocks = []
              + prefix_list_ids  = []
              + protocol         = "-1"
              + security_groups  = []
              + self             = false
              + to_port          = 0
            },
        ]
      + id                     = (known after apply)
      + ingress                = [
          + {
              + cidr_blocks      = [
                  + "0.0.0.0/0",
                ]
              + description      = ""
              + from_port        = 45678
              + ipv6_cidr_blocks = []
              + prefix_list_ids  = []
              + protocol         = "tcp"
              + security_groups  = []
              + self             = false
              + to_port          = 45678
            },
        ]
      + name                   = (known after apply)
      + owner_id               = (known after apply)
      + revoke_rules_on_delete = false
      + vpc_id                 = (known after apply)
    }

  # aws_security_group.service_security_group will be created
  + resource "aws_security_group" "service_security_group" {
      + arn                    = (known after apply)
      + description            = "Allow acces only from the ALB"
      + egress                 = [
          + {
              + cidr_blocks      = [
                  + "0.0.0.0/0",
                ]
              + description      = ""
              + from_port        = 0
              + ipv6_cidr_blocks = []
              + prefix_list_ids  = []
              + protocol         = "-1"
              + security_groups  = []
              + self             = false
              + to_port          = 0
            },
        ]
      + id                     = (known after apply)
      + ingress                = [
          + {
              + cidr_blocks      = []
              + description      = ""
              + from_port        = 0
              + ipv6_cidr_blocks = []
              + prefix_list_ids  = []
              + protocol         = "-1"
              + security_groups  = (known after apply)
              + self             = false
              + to_port          = 0
            },
        ]
      + name                   = (known after apply)
      + owner_id               = (known after apply)
      + revoke_rules_on_delete = false
      + vpc_id                 = (known after apply)
    }

  # null_resource.environment will be created
  + resource "null_resource" "environment" {
      + id = (known after apply)
    }

Plan: 13 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + alb_url = (known after apply)
```
## Creation of resources produces log:

```
Apply complete! Resources: 13 added, 0 changed, 0 destroyed.
```

</details>

You can see the logs on the AWS console under:

CloudWatch -> LogGroups

<p align="center">
  <img src="logs.png" alt="Jina banner" width="90%">
</p>

Click on the desired one and you'll see the details 

<p align="center">
  <img src="logs2.png" alt="Jina banner" width="90%">
</p>