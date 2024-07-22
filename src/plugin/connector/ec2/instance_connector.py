from botocore.config import Config
from spaceone.core.error import ERROR_REQUIRED_PARAMETER

from plugin.conf.cloud_service_conf import *
from plugin.connector.base import ResourceConnector, _LOGGER


class InstanceConnector(ResourceConnector):
    service_name = "ec2"
    cloud_service_group = "EC2"
    cloud_service_type = "Instance"
    include_vpc_default = False

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "ec2"
        self.cloud_service_type = "Instance"
        self.rest_service_name = "ec2"
        self.asg_client = self.session.client(
            "autoscaling", config=Config(retries={"max_attempts": 10})
        )
        self.elbv2_client = self.session.client(
            "elbv2", config=Config(retries={"max_attempts": 10})
        )
        self.ssm_client = self.session.client(
            "ssm", config=Config(retries={"max_attempts": 10})
        )

    def list_regions(self, **query):
        query = self._generate_query(is_paginate=False, **query)
        response = self.client.describe_regions(**query)
        return response["Regions"]

    def list_ec2_instances(self, **query):
        ec2_instances = []
        query = self._generate_query(is_paginate=True, **query)
        query.update(
            {
                "Filters": [
                    {
                        "Name": "instance-state-name",
                        "Values": [
                            "pending",
                            "running",
                            "shutting-down",
                            "stopping",
                            "stopped",
                        ],
                    }
                ]
            }
        )
        paginator = self.client.get_paginator("describe_instances")
        response_iterator = paginator.paginate(**query)
        account_id = ""
        for data in response_iterator:
            for reservation in data.get("Reservations", []):
                if account_id == "":
                    account_id = reservation.get("OwnerId")
                ec2_instances.extend(reservation.get("Instances", []))
        return ec2_instances, account_id

    def list_instance_types(self, **query):
        instance_types = []
        query = self._generate_query(is_paginate=True, **query)
        paginator = self.client.get_paginator("describe_instance_types")
        response_iterator = paginator.paginate(**query)

        for data in response_iterator:
            instance_types.extend(data.get("InstanceTypes", []))

        return instance_types

    def list_instance_attribute(self, instance_id, **query):
        response = self.client.describe_instance_attribute(
            Attribute="disableApiTermination", InstanceId=instance_id, **query
        )

        attribute = response.get("DisableApiTermination", {"Value": False})
        return attribute.get("Value")

    def list_auto_scaling_groups(self, **query):
        auto_scaling_groups = []
        query = self._generate_query(is_paginate=True, **query)
        paginator = self.asg_client.get_paginator("describe_auto_scaling_groups")

        response_iterator = paginator.paginate(**query)

        for data in response_iterator:
            auto_scaling_groups.extend(data.get("AutoScalingGroups", []))

        return auto_scaling_groups

    def list_launch_configurations(self, **query):
        launch_configurations = []
        query = self._generate_query(is_paginate=True, **query)
        paginator = self.asg_client.get_paginator("describe_launch_configurations")
        response_iterator = paginator.paginate(**query)

        for data in response_iterator:
            launch_configurations.extend(data.get("LaunchConfigurations", []))

        return launch_configurations

    def list_launch_templates(self, **query):
        launch_templates = []
        query = self._generate_query(is_paginate=True, **query)
        paginator = self.asg_client.get_paginator("describe_launch_templates")
        response_iterator = paginator.paginate(**query)

        for data in response_iterator:
            launch_templates.extend(data.get("LaunchTemplates", []))

        return launch_templates

    def list_load_balancers(self, **query):
        load_balancers = []
        query = self._generate_query(is_paginate=True, **query)
        paginator = self.elbv2_client.get_paginator("describe_load_balancers")
        response_iterator = paginator.paginate(**query)

        for data in response_iterator:
            load_balancers.extend(data.get("LoadBalancers", []))

        return load_balancers

    def list_target_groups(self, **query):
        target_groups = []
        query = self._generate_query(is_paginate=True, **query)
        paginator = self.elbv2_client.get_paginator("describe_target_groups")
        response_iterator = paginator.paginate(**query)

        for data in response_iterator:
            target_groups.extend(data.get("TargetGroups", []))

        return target_groups

    def list_listeners(self, load_balancer_arn, **query):
        response = self.elbv2_client.describe_listeners(
            LoadBalancerArn=load_balancer_arn, **query
        )
        return response.get("Listeners", [])

    def list_target_health(self, target_group_arn, **query):
        response = self.elbv2_client.describe_target_health(
            TargetGroupArn=target_group_arn, **query
        )
        return response.get("TargetHealthDescriptions", [])

    def list_security_groups(self, **query):
        security_groups = []
        query = self._generate_query(is_paginate=True, **query)
        paginator = self.client.get_paginator("describe_security_groups")
        response_iterator = paginator.paginate(**query)

        for data in response_iterator:
            security_groups.extend(data.get("SecurityGroups", []))

        return security_groups

    def list_subnets(self, **query):
        subnets = []
        query = self._generate_query(is_paginate=True, **query)
        paginator = self.client.get_paginator("describe_subnets")
        response_iterator = paginator.paginate(**query)

        for data in response_iterator:
            subnets.extend(data.get("Subnets", []))

        return subnets

    def list_vpcs(self, **query):
        vpcs = []
        query = self._generate_query(is_paginate=True, **query)
        paginator = self.client.get_paginator("describe_vpcs")
        response_iterator = paginator.paginate(**query)
        for data in response_iterator:
            vpcs.extend(data.get("Vpcs", []))

        return vpcs

    def list_volumes(self, **query):
        volumes = []
        query = self._generate_query(is_paginate=True, **query)
        paginator = self.client.get_paginator("describe_volumes")
        response_iterator = paginator.paginate(**query)

        for data in response_iterator:
            volumes.extend(data.get("Volumes", []))

        return volumes

    def list_images(self, **query):
        query = self._generate_query(is_paginate=False, **query)
        response = self.client.describe_images(**query)
        return response.get("Images", [])

    def list_elastic_ips(self, **query):
        query = self._generate_query(is_paginate=False, **query)
        response = self.client.describe_addresses(**query)
        return response.get("Addresses", [])

    @staticmethod
    def _check_secret_data(secret_data):
        if "aws_access_key_id" not in secret_data:
            raise ERROR_REQUIRED_PARAMETER(key="secret.aws_access_key_id")

        if "aws_secret_access_key" not in secret_data:
            raise ERROR_REQUIRED_PARAMETER(key="secret.aws_secret_access_key")

    @staticmethod
    def _generate_query(is_paginate=False, **query):
        if is_paginate:
            query.update(
                {
                    "PaginationConfig": {
                        "MaxItems": PAGINATOR_MAX_ITEMS,
                        "PageSize": PAGINATOR_PAGE_SIZE,
                    }
                }
            )
        return query

    def describe_instance_information(self, instances, **query) -> dict:
        instance_information = {}

        try:
            for i in range(0, len(instances), 100):
                instances_chunk = instances[i : i + 100]
                query = self._generate_query(is_paginate=True, **query)
                query.update(
                    {
                        "Filters": [
                            {
                                "Key": "InstanceIds",
                                "Values": self._get_instance_ids_from_instance(
                                    instances_chunk
                                ),
                            },
                        ]
                    }
                )
                paginator = self.ssm_client.get_paginator(
                    "describe_instance_information"
                )
                response_iterator = paginator.paginate(**query)

                for data in response_iterator:
                    for instance in data.get("InstanceInformationList", []):
                        instance_information.update(
                            {
                                instance.get("InstanceId"): {
                                    "platform_type": instance.get("PlatformType"),
                                    "platform_name": instance.get("PlatformName"),
                                    "platform_version": instance.get("PlatformVersion"),
                                }
                            }
                        )
        except Exception as e:
            _LOGGER.error(f"[instance_information] {e}")
            instance_information = {}

        return instance_information

    @staticmethod
    def _get_instance_ids_from_instance(instances: list) -> list:
        instance_ids = []
        for instance in instances:
            instance_ids.append(instance.get("InstanceId"))
        return instance_ids
