from spaceone.inventory.plugin.collector.lib import *
from ..base import ResourceManager
from ...conf.cloud_service_conf import ASSET_URL, INSTANCE_FILTERS


class SecurityGroupManager(ResourceManager):
    cloud_service_group = "EC2"
    cloud_service_type = "SecurityGroup"
    include_vpc_default = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "EC2"
        self.cloud_service_type = "SecurityGroup"
        self.metadata_path = "metadata/ec2/sg.yaml"
        self.include_vpc_default = False

    def create_cloud_service_type(self):
        yield make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonEC2",
            tags={"spaceone:icon": f"{ASSET_URL}/Amazon-VPC_VPN-Gateway_dark-bg.svg"},
            labels=["Compute", "Security"],
        )

    def create_cloud_service(self, region, options, secret_data, schema):
        cloudtrail_resource_type = "AWS::EC2::SecurityGroup"

        # Get default VPC
        default_vpcs = self._get_default_vpc()

        # Get EC2 Instances
        instances = self.list_instances()

        # Get Security Group
        results = self.connector.get_security_groups()
        account_id = self.connector.get_account_id()

        for data in results:
            for raw in data.get("SecurityGroups", []):
                try:
                    if (
                        self.include_vpc_default is False
                        and raw.get("VpcId") in default_vpcs
                    ):
                        continue

                    # Inbound Rules
                    inbound_rules = []
                    for in_rule in raw.get("IpPermissions", []):
                        for _ip_range in in_rule.get("IpRanges", []):
                            inbound_rules.append(
                                self.custom_security_group_rule_info(
                                    in_rule, _ip_range, "ip_ranges"
                                )
                            )

                        for _user_group_pairs in in_rule.get("UserIdGroupPairs", []):
                            inbound_rules.append(
                                self.custom_security_group_rule_info(
                                    in_rule, _user_group_pairs, "user_id_group_pairs"
                                )
                            )

                        for _ip_v6_range in in_rule.get("Ipv6Ranges", []):
                            inbound_rules.append(
                                self.custom_security_group_rule_info(
                                    in_rule, _ip_v6_range, "ipv6_ranges"
                                )
                            )

                    # Outbound Rules
                    outbound_rules = []
                    for out_rule in raw.get("IpPermissionsEgress", []):
                        for _ip_range in out_rule.get("IpRanges", []):
                            outbound_rules.append(
                                self.custom_security_group_rule_info(
                                    out_rule, _ip_range, "ip_ranges"
                                )
                            )

                        for _user_group_pairs in out_rule.get("UserIdGroupPairs", []):
                            outbound_rules.append(
                                self.custom_security_group_rule_info(
                                    out_rule,
                                    _user_group_pairs,
                                    "user_id_group_pairs",
                                )
                            )

                        for _ip_v6_range in out_rule.get("Ipv6Ranges", []):
                            outbound_rules.append(
                                self.custom_security_group_rule_info(
                                    out_rule, _ip_v6_range, "ipv6_ranges"
                                )
                            )

                    raw.update(
                        {
                            "ip_permissions": inbound_rules,
                            "ip_permissions_egress": outbound_rules,
                            "instances": self.get_security_group_map_instances(
                                raw, instances
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                region, cloudtrail_resource_type, raw["GroupId"]
                            ),
                        }
                    )

                    sg_vo = raw
                    cloud_service = make_cloud_service(
                        name=sg_vo.get("GroupName", ""),
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=sg_vo,
                        account=account_id,
                        tags=self.convert_tags_to_dict_type(raw.get("Tags", [])),
                        region_code=region,
                    )
                    yield cloud_service
                    # yield {
                    #     "data": sg_vo,
                    #     "name": sg_vo.group_name,
                    #     "account": self.account_id,
                    #     "tags": self.convert_tags_to_dict_type(raw.get("Tags", [])),
                    # }

                except Exception as e:
                    # resource_id = raw.get("GroupId", "")
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

    def custom_security_group_rule_info(self, raw_rule, remote, remote_type):
        raw_rule.update(
            {
                "protocol_display": self._get_protocol_display(
                    raw_rule.get("IpProtocol")
                ),
                "port_display": self._get_port_display(raw_rule),
                "source_display": self._get_source_display(remote),
                "description_display": self._get_description_display(remote),
                remote_type: remote,
            }
        )

        return raw_rule

    def list_instances(self):
        instances = []
        filter_info = [
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
        results = self.connector.get_filtered_instances(filter_info)
        for data in results:
            for _reservation in data.get("Reservations", []):
                instances.extend(_reservation.get("Instances", []))

        return instances

    def _get_default_vpc(self):
        default_vpcs = []
        vpc_response = self.connector.describe_vpcs()
        for _vpc in vpc_response["Vpcs"]:
            if _vpc.get("IsDefault", False):
                default_vpcs.append(_vpc["VpcId"])

        return default_vpcs

    def get_security_group_map_instances(self, security_group, instances):
        sg_map_instances = []

        for instance in instances:
            for instance_sg in instance.get("SecurityGroups", []):
                if security_group.get("GroupId") == instance_sg.get("GroupId"):
                    instance["instance_name"] = self.get_instance_name_from_tags(
                        instance
                    )
                    needed_instance = {}
                    for key in INSTANCE_FILTERS:
                        if key in instance:
                            needed_instance[key] = instance[key]
                        else:
                            needed_instance[key] = None
                    sg_map_instances.append(needed_instance)

        return [sg_map_instance for sg_map_instance in sg_map_instances]

    @staticmethod
    def _get_protocol_display(raw_protocol):
        if raw_protocol == "-1":
            return "ALL"
        elif raw_protocol == "tcp":
            return "TCP"
        elif raw_protocol == "udp":
            return "UDP"
        elif raw_protocol == "icmp":
            return "ICMP"
        else:
            return raw_protocol

    @staticmethod
    def _get_port_display(raw_rule):
        _protocol = raw_rule.get("IpProtocol")

        if _protocol == "-1":
            return "ALL"
        elif _protocol in ["tcp", "udp"]:
            from_port = raw_rule.get("FromPort")
            to_port = raw_rule.get("ToPort")

            if from_port == 0 and to_port == 65535:
                return "ALL"

            if from_port == to_port:
                return f"{from_port}"

            if from_port is not None and to_port is not None:
                return f"{from_port} - {to_port}"

            return ""
        elif _protocol == "icmp":
            return "ALL"
        else:
            return ""

    @staticmethod
    def _get_source_display(remote):
        if cidr := remote.get("CidrIp"):
            return cidr
        elif group_id := remote.get("GroupId"):
            return group_id
        elif cidrv6 := remote.get("CidrIpv6"):
            return cidrv6

        return ""

    @staticmethod
    def _get_description_display(remote):
        if description := remote.get("Description"):
            return description

        return ""

    @staticmethod
    def get_instance_name_from_tags(instance):
        for _tag in instance.get("Tags", []):
            if _tag.get("Key") == "Name":
                return _tag.get("Value")

        return ""
