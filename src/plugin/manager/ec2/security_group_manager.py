import copy
from spaceone.inventory.plugin.collector.lib import *
from ..base import ResourceManager
from ...conf.cloud_service_conf import (
    ASSET_URL,
    INSTANCE_FILTERS,
    DEFAULT_VULNERABLE_PORTS,
)
from plugin.error.custom import ERROR_VULNERABLE_PORTS


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
        self.sg_rules_for_this_group = []

    def create_cloud_service_type(self):
        result = []
        sg_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=False,
            is_major=False,
            service_code="AmazonEC2",
            tags={"spaceone:icon": f"{ASSET_URL}/Amazon-VPC_VPN-Gateway_dark-bg.svg"},
            labels=["Compute", "Security"],
        )
        result.append(sg_cst_result)
        return result

    def create_cloud_service(self, region, options, secret_data, schema):
        cloudtrail_resource_type = "AWS::EC2::SecurityGroup"

        # If Port Filter Option Exist
        vulnerable_ports = options.get("vulnerable_ports")

        # Get default VPC
        default_vpcs = self._get_default_vpc()

        # Get EC2 Instances
        instances = self.list_instances()

        # Get Security Group
        results = self.connector.get_security_groups()
        account_id = options.get("account_id", "")
        self.connector.load_account_id(account_id)

        # Get Security Group Rules Detail
        sg_rules_detail = self.connector.get_security_group_rules()

        sg_rules_map = {}
        for data in sg_rules_detail:
            for rule in data.get("SecurityGroupRules", []):
                group_id = rule.get("GroupId")
                if group_id not in sg_rules_map:
                    sg_rules_map[group_id] = []
                sg_rules_map[group_id].append(rule)

        for data in results:
            for raw in data.get("SecurityGroups", []):
                try:
                    group_id = raw.get("GroupId", "")
                    self.sg_rules_for_this_group = sg_rules_map.get(group_id, [])

                    if (
                        self.include_vpc_default is False
                        and raw.get("VpcId") in default_vpcs
                    ):
                        continue

                    # Inbound Rules
                    inbound_rules = []
                    for in_rule in raw.get("IpPermissions", []):
                        in_rule_copy = copy.deepcopy(in_rule)

                        for _ip_range in in_rule.get("IpRanges", []):
                            inbound_rules.append(
                                self._custom_security_group_inbound_rule_info(
                                    raw_rule=in_rule_copy,
                                    remote=_ip_range,
                                    remote_type="ip_ranges",
                                    is_egress=False,
                                    vulnerable_ports=vulnerable_ports,
                                )
                            )

                        for _user_group_pair in in_rule.get("UserIdGroupPairs", []):
                            inbound_rules.append(
                                self._custom_security_group_inbound_rule_info(
                                    raw_rule=in_rule_copy,
                                    remote=_user_group_pair,
                                    remote_type="user_id_group_pairs",
                                    is_egress=False,
                                    vulnerable_ports=vulnerable_ports,
                                )
                            )

                        for _ip_v6_range in in_rule.get("Ipv6Ranges", []):
                            inbound_rules.append(
                                self._custom_security_group_inbound_rule_info(
                                    raw_rule=in_rule_copy,
                                    remote=_ip_v6_range,
                                    remote_type="ipv6_ranges",
                                    is_egress=False,
                                    vulnerable_ports=vulnerable_ports,
                                )
                            )

                        for prefix_list_id in in_rule.get("PrefixListIds", []):
                            inbound_rules.append(
                                self._custom_security_group_inbound_rule_info(
                                    raw_rule=in_rule_copy,
                                    remote=prefix_list_id,
                                    remote_type="prefix_list_ids",
                                    is_egress=False,
                                    vulnerable_ports=vulnerable_ports,
                                )
                            )

                    # Outbound Rules
                    outbound_rules = []
                    for out_rule in raw.get("IpPermissionsEgress", []):
                        out_rule_copy = copy.deepcopy(out_rule)

                        for _ip_range in out_rule.get("IpRanges", []):
                            outbound_rules.append(
                                self._custom_security_group_inbound_rule_info(
                                    raw_rule=out_rule_copy,
                                    remote=_ip_range,
                                    remote_type="ip_ranges",
                                    is_egress=True,
                                )
                            )

                        for _user_group_pairs in out_rule.get("UserIdGroupPairs", []):
                            outbound_rules.append(
                                self._custom_security_group_inbound_rule_info(
                                    raw_rule=out_rule_copy,
                                    remote=_user_group_pairs,
                                    remote_type="user_id_group_pairs",
                                    is_egress=True,
                                )
                            )

                        for _ip_v6_range in out_rule.get("Ipv6Ranges", []):
                            outbound_rules.append(
                                self._custom_security_group_inbound_rule_info(
                                    raw_rule=out_rule_copy,
                                    remote=_ip_v6_range,
                                    remote_type="ipv6_ranges",
                                    is_egress=True,
                                )
                            )

                        for prefix_list_id in out_rule.get("PrefixListIds", []):
                            outbound_rules.append(
                                self._custom_security_group_inbound_rule_info(
                                    raw_rule=out_rule_copy,
                                    remote=prefix_list_id,
                                    remote_type="prefix_list_ids",
                                    is_egress=True,
                                )
                            )

                    match_instances = self.get_security_group_map_instances(
                        raw, instances
                    )

                    raw.update(
                        {
                            "ip_permissions": inbound_rules,
                            "ip_permissions_egress": outbound_rules,
                            "instances": match_instances,
                            "cloudtrail": self.set_cloudtrail(
                                region, cloudtrail_resource_type, raw["GroupId"]
                            ),
                            "stats": {"instances_count": len(match_instances)},
                        }
                    )
                    sg_vo = raw

                    link = f"https://console.aws.amazon.com/ec2/v2/home?region={region}#SecurityGroups:group-id={group_id}"
                    reference = self.get_reference(group_id, link)

                    cloud_service = make_cloud_service(
                        name=sg_vo.get("GroupName", ""),
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=sg_vo,
                        account=account_id,
                        tags=self.convert_tags_to_dict_type(raw.get("Tags", [])),
                        region_code=region,
                        reference=reference,
                    )
                    yield cloud_service
                except Exception as e:
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

    @staticmethod
    def _get_matched_security_group_rule_id(
        raw_rule, sg_rules_detail, remote, remote_type, is_egress
    ):
        raw_protocol = raw_rule.get("IpProtocol")
        raw_from_port = raw_rule.get("FromPort")
        raw_to_port = raw_rule.get("ToPort")

        for sg_rule in sg_rules_detail:
            if sg_rule.get("IsEgress") != is_egress:
                continue

            if sg_rule.get("IpProtocol") != raw_protocol:
                continue

            if raw_from_port:
                sg_from_port = sg_rule.get("FromPort")
                if raw_from_port is not None and sg_from_port is not None:
                    if raw_from_port != sg_from_port:
                        continue

            if raw_to_port:
                sg_to_port = sg_rule.get("ToPort")
                if raw_to_port is not None and sg_to_port is not None:
                    if raw_to_port != sg_to_port:
                        continue

            if remote_type == "ip_ranges":
                if sg_rule.get("CidrIpv4") != remote.get("CidrIp"):
                    continue
            elif remote_type == "ipv6_ranges":
                if sg_rule.get("CidrIpv6") != remote.get("CidrIpv6"):
                    continue
            elif remote_type == "prefix_list_ids":
                if sg_rule.get("PrefixListId") != remote.get("PrefixListId"):
                    continue
            elif remote_type == "user_id_group_pairs":
                referenced_group = sg_rule.get("ReferencedGroupInfo", {})
                if referenced_group.get("GroupId") != remote.get("GroupId"):
                    continue

            return sg_rule.get("SecurityGroupRuleId")

        return None

    def _custom_security_group_inbound_rule_info(
        self, raw_rule, remote, remote_type, is_egress, vulnerable_ports=None
    ):
        rule_id = self._get_matched_security_group_rule_id(
            raw_rule=raw_rule,
            sg_rules_detail=self.sg_rules_for_this_group,
            remote=remote,
            remote_type=remote_type,
            is_egress=is_egress,
        )

        raw_rule = self._custom_security_group_rule_info(raw_rule, remote, remote_type)

        protocol_display = raw_rule.get("protocol_display")

        if vulnerable_ports:
            ports = self._get_vulnerable_ports(
                protocol_display, raw_rule, vulnerable_ports
            )

            raw_rule.update(
                {
                    "rule_id": rule_id,
                    "vulnerable_ports": ports,
                    "detected_vulnerable_ports": True if ports else False,
                }
            )

        return raw_rule

    def _custom_security_group_rule_info(self, raw_rule, remote, remote_type):
        protocol_display = self._get_protocol_display(raw_rule.get("IpProtocol"))
        raw_rule.update(
            {
                "protocol_display": protocol_display,
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
        elif prefix_list_id := remote.get("PrefixListId"):
            return prefix_list_id

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

    @staticmethod
    def _get_vulnerable_ports(
        protocol_display: str, raw_rule: dict, vulnerable_ports: str
    ):
        try:
            ports = []

            to_port = raw_rule.get("ToPort")
            from_port = raw_rule.get("FromPort")

            if protocol_display != "ALL" and (to_port is None or from_port is None):
                return None

            for port in vulnerable_ports.split(","):
                target_port = int(port)

                if protocol_display == "ALL":
                    ports.append(port)
                elif from_port <= target_port <= to_port:
                    ports.append(port)

            return ",".join(ports)
        except ValueError:
            raise ERROR_VULNERABLE_PORTS(vulnerable_ports)
