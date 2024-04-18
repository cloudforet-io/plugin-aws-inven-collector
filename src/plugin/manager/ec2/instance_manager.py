from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ..ec2_server import *


class InstanceManager(ResourceManager):
    cloud_service_group = "EC2"
    cloud_service_type = "Instance"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "EC2"
        self.cloud_service_type = "Instance"
        self.metadata_path = "metadata/ec2/instance.yaml"

    def create_cloud_service_type(self):
        yield make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonEC2",
            tags={
                "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-ec2.svg"
            },
            labels=["Compute", "Server"],
        )

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        # meta_manager: MetadataManager = MetadataManager()
        region_name = region
        cloudtrail_resource_type = "AWS::EC2::Instance"

        instance_filter = {}
        # Instance list and account ID

        # if "instance_ids" in params and len(params["instance_ids"]) > 0:
        #     instance_filter.update(
        #         {"Filters": [{"Name": "instance-id", "Values": params["instance_ids"]}]}
        #     )

        instances, account_id = self.connector.list_ec2_instances(**instance_filter)

        # _LOGGER.debug(
        #     f'[list_instances] [{params["region_name"]}] INSTANCE COUNT : {len(instances)}'
        # )

        if instances:
            ins_manager = EC2InstanceManager(self.connector, region)
            asg_manager = AutoScalingGroupManager(self.connector)
            elb_manager = LoadBalancerManager(self.connector)
            disk_manager = DiskManager(self.connector)
            nic_manager = NICManager(self.connector)
            vpc_manager = VPCManager(self.connector)
            sg_manager = SecurityGroupManager(self.connector)
            cw_manager = CloudWatchManager()

            # Instance Type
            itypes = self.connector.list_instance_types()

            # Image
            images = self.connector.list_images(ImageIds=self.get_image_ids(instances))

            # Auto Scaling group list
            auto_scaling_groups = self.connector.list_auto_scaling_groups()
            launch_configurations = self.connector.list_launch_configurations()

            # LB list
            load_balancers = self.connector.list_load_balancers()
            elb_manager.set_listeners_into_load_balancers(load_balancers)

            target_groups = self.connector.list_target_groups()

            for target_group in target_groups:
                target_healths = self.connector.list_target_health(
                    target_group.get("TargetGroupArn")
                )
                target_group["target_healths"] = target_healths

            # VPC
            vpcs = self.connector.list_vpcs()
            subnets = self.connector.list_subnets()

            # Volume
            volumes = self.connector.list_volumes()

            # IP
            eips = self.connector.list_elastic_ips()

            # Security Group
            sgs = self.connector.list_security_groups()

            for instance in instances:
                try:
                    instance_id = instance.get("InstanceId")
                    instance_ip = instance.get("PrivateIpAddress")

                    server_data = ins_manager.get_server_info(instance, itypes, images)
                    auto_scaling_group_vo = asg_manager.get_auto_scaling_info(
                        instance_id, auto_scaling_groups, launch_configurations
                    )

                    load_balancer_vos = elb_manager.get_load_balancer_info(
                        load_balancers, target_groups, instance_id, instance_ip
                    )

                    disk_vos = disk_manager.get_disk_info(
                        self.get_volume_ids(instance), volumes
                    )
                    vpc_vo, subnet_vo = vpc_manager.get_vpc_info(
                        instance.get("VpcId"),
                        instance.get("SubnetId"),
                        vpcs,
                        subnets,
                        region_name,
                    )

                    nic_vos = nic_manager.get_nic_info(
                        instance.get("NetworkInterfaces"), subnet_vo
                    )

                    sg_ids = [
                        security_group.get("GroupId")
                        for security_group in instance.get("SecurityGroups", [])
                        if security_group.get("GroupId") is not None
                    ]
                    sg_rules_vos = sg_manager.get_security_group_info(sg_ids, sgs)

                    if disk_vos:
                        server_data["data"]["aws"]["root_volume_type"] = (
                            disk_vos[0].get("tags", {}).get("volume_type")
                        )

                    server_data.update(
                        {
                            "region_code": region_name,
                            "instance_type": server_data["data"]["compute"][
                                "instance_type"
                            ],
                            "tags": self.convert_tags(instance.get("Tags", [])),
                        }
                    )

                    server_data["data"].update(
                        {
                            "primary_ip_address": instance_ip,
                            "nics": nic_vos,
                            "disks": disk_vos,
                            "load_balancer": load_balancer_vos,
                            "security_group": sg_rules_vos,
                            "vpc": vpc_vo,
                            "subnet": subnet_vo,
                        }
                    )

                    if auto_scaling_group_vo:
                        server_data["data"].update(
                            {"auto_scaling_group": auto_scaling_group_vo}
                        )

                    # IP addr : ip_addresses = nics.ip_addresses + data.public_ip_address
                    server_data.update(
                        {"ip_addresses": self.merge_ip_addresses(server_data)}
                    )

                    server_data["data"]["cloudwatch"] = cw_manager.set_cloudwatch_info(
                        instance_id, region_name
                    )
                    server_data["data"]["cloudtrail"] = self.set_cloudtrail(
                        region_name, cloudtrail_resource_type, instance_id
                    )
                    server_data["data"]["compute"]["account"] = account_id
                    server_data["account"] = account_id

                    link = f"https://{region}.console.aws.amazon.com/ec2/v2/home?region={region}#Instances:instanceId={server_data['data']['compute']['instance_id']}"
                    resource_id = server_data["data"]["compute"]["instance_id"]
                    reference = self.get_reference(resource_id, link)

                    cloud_service = make_cloud_service(
                        name=server_data.get("name", ""),
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=server_data["data"],
                        account=account_id,
                        reference=reference,
                        instance_type=server_data.get("instance_type", ""),
                        instance_size=float(server_data.get("instance_size", 0)),
                        tags=server_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_instances] [{instance.get("InstanceId")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

    def convert_tags(self, tags):
        dict_tags = {}

        for _tag in tags:
            dict_tags[_tag.get("Key")] = _tag.get("Value")

        return dict_tags

    # @staticmethod
    # def list_cloud_service_types():
    #     meta_manager: MetadataManager = MetadataManager()
    #
    #     cloud_service_type = {
    #         "_metadata": meta_manager.get_cloud_service_type_metadata(),
    #         "tags": {
    #             "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-ec2.svg",
    #         },
    #     }
    #     return [CloudServiceType(cloud_service_type, strict=False)]

    @staticmethod
    def get_volume_ids(instance):
        block_device_mappings = instance.get("BlockDeviceMappings", [])
        return [
            block_device_mapping["Ebs"]["VolumeId"]
            for block_device_mapping in block_device_mappings
            if block_device_mapping.get("Ebs") is not None
        ]

    @staticmethod
    def get_image_ids(instances):
        image_ids = [
            instance.get("ImageId")
            for instance in instances
            if instance.get("ImageId") is not None
        ]
        return list(set(image_ids))

    @staticmethod
    def get_device_for_cloudwatch(disks):
        try:
            for _disk in disks:
                _device = _disk.device
                _device_name = _device.split("/")[-1]
                if _device_name:
                    return f"{_device_name}1"
            return None
        except Exception as e:
            return None

    @staticmethod
    def merge_ip_addresses(server_data):
        nics = server_data.get("data", {}).get("nics", [])

        nic_ip_addresses = []
        for nic in nics:
            nic_ip_addresses.extend(nic.get("ip_addresses", []))

        merge_ip_address = nic_ip_addresses

        return list(set(merge_ip_address))
