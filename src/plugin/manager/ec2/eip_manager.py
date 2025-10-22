from ..base import ResourceManager
from spaceone.inventory.plugin.collector.lib import *

from ...conf.cloud_service_conf import ASSET_URL


class EIPManager(ResourceManager):
    cloud_service_group = "EC2"
    cloud_service_type = "EIP"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "EC2"
        self.cloud_service_type = "EIP"
        self.metadata_path = "metadata/ec2/eip.yaml"

    def create_cloud_service_type(self):
        result = []
        eip_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=False,
            is_major=True,
            service_code="AmazonEC2",
            tags={
                "spaceone:icon": f"{ASSET_URL}/Amazon-EC2_Elastic-IP-Address_light-bg.svg"
            },
            labels=["Networking", "Compute"],
        )
        result.append(eip_cst_result)
        return result

    def create_cloud_service(self, region, options, secret_data, schema):
        yield from self._collect_eips(options, region)

    def _collect_eips(self, options, region):
        results = self.connector.get_addresses()
        account_id = options.get("account_id", "")
        self.connector.load_account_id(account_id)
        nat_gateways = None
        network_interfaces = None
        eips = results.get("Addresses", [])

        if len(eips) > 0:
            nat_gateways = self.connector.describe_nat_gateways().get("NatGateways", [])
            network_interfaces = self.connector.describe_network_interfaces(
                [
                    eip.get("NetworkInterfaceId")
                    for eip in eips
                    if eip.get("NetworkInterfaceId")
                ]
            ).get("NetworkInterfaces", [])

        for _ip in eips:
            try:
                public_ip = _ip.get("PublicIp")

                if public_ip is not None:
                    if nat_gw_id := self._match_nat_gw(public_ip, nat_gateways):
                        _ip["nat_gateway_id"] = nat_gw_id

                    if public_dns := self._match_network_interface_public_dns(
                        public_ip, network_interfaces
                    ):
                        _ip["public_dns"] = public_dns

                _ip.update(
                    {
                        "allocation_status": (
                            "In-use" if _ip.get("AllocationId") else "Unused"
                        ),
                        "name": self._get_name_from_tags(_ip.get("Tags", [])),
                        "cloudtrail": self.set_cloudtrail(
                            self.cloud_service_group, _ip["AllocationId"], region
                        ),
                    }
                )

                eip_vo = _ip

                allocation_id = eip_vo.get("AllocationId", "")
                link = f"https://console.aws.amazon.com/ec2/v2/home?region={region}#ElasticIpDetails:AllocationId={allocation_id}"
                reference = self.get_reference(allocation_id, link)

                cloud_service = make_cloud_service(
                    name=eip_vo.get("name", ""),
                    cloud_service_type=self.cloud_service_type,
                    cloud_service_group=self.cloud_service_group,
                    provider=self.provider,
                    data=eip_vo,
                    account=options.get("account_id"),
                    tags=self.convert_tags_to_dict_type(_ip.get("Tags", [])),
                    region_code=region,
                    reference=reference,
                )
                yield cloud_service
                # yield {
                #     'data': eip_vo,
                #     'name': eip_vo.name,
                #     'account': self.account_id,
                #     'tags': self.convert_tags_to_dict_type(_ip.get('Tags', []))
                # }

            except Exception as e:
                # resource_id = _ip.get('PublicIp', '')
                yield make_error_response(
                    error=e,
                    provider=self.provider,
                    cloud_service_group=self.cloud_service_group,
                    cloud_service_type=self.cloud_service_type,
                    region_name=region,
                )

    @staticmethod
    def _match_network_interface_public_dns(ip, network_interfaces):
        for nif in network_interfaces:
            if association := nif.get("Association"):
                if ip == association.get("PublicIp"):
                    return association.get("PublicDnsName", None)

        return None

    @staticmethod
    def _match_nat_gw(ip, nat_gateways):
        for nat_gw in nat_gateways:
            nat_gw_address = nat_gw.get("NatGatewayAddresses", [{}])[0]
            if ip == nat_gw_address.get("PublicIp"):
                return nat_gw.get("NatGatewayId")

        return None

    @staticmethod
    def _get_name_from_tags(tags):
        for tag in tags:
            if "Name" in tag.get("Key"):
                return tag.get("Value")
        return ""
