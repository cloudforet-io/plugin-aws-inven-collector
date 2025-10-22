from spaceone.inventory.plugin.collector.lib import *
from ..base import ResourceManager
from ...conf.cloud_service_conf import *

from ...model.direct_connect import Connection


class ConnectManager(ResourceManager):
    cloud_service_group = "DirectConnect"
    cloud_service_type = "Connection"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "DirectConnect"
        self.cloud_service_type = "Connection"
        self.metadata_path = "metadata/direct_connect/connection.yaml"

    def create_cloud_service_type(self):
        yield make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AWSDirectConnect",
            tags={"spaceone:icon": f"{ASSET_URL}/AWS-Direct-Connect.svg"},
            labels=["Networking"],
        )

    def create_cloud_service(self, region, options, secret_data, schema):
        yield from self._collect_connections(options, region)

    def _collect_connections(self, options, region):
        results = self.connector.get_connections()
        for raw in results.get("connections", []):
            try:
                bandwidth_size = self.convert_bandwidth_gbps(raw.get("bandwidth", ""))

                if bandwidth_size:
                    raw.update({"bandwidth_gbps": bandwidth_size})

                raw.update(
                    {
                        "cloudtrail": self.set_cloudtrail(
                            self.cloud_service_group, raw["connectionId"], region
                        ),
                        "cloudwatch": self.set_cloudwatch(
                            self.cloud_service_group,
                            raw["connectionId"],
                            region,
                        ),
                    }
                )
                self._update_times(raw)
                connection_vo = Connection(raw, strict=False)
                connection_id = connection_vo.connection_id
                owner_account = connection_vo.owner_account
                link = f"https://console.aws.amazon.com/directconnect/v2/home?region={region}#/connections/arn:aws:directconnect:{region}:{owner_account}:{connection_id}"
                reference = self.get_reference(connection_id, link)

                cloud_service = make_cloud_service(
                    name=connection_vo.get("connectionName", ""),
                    cloud_service_type=self.cloud_service_type,
                    cloud_service_group=self.cloud_service_group,
                    provider=self.provider,
                    data=connection_vo.to_primitive(),
                    account=options.get("account_id"),
                    reference=reference,
                    instance_size=bandwidth_size,
                    instance_type=connection_vo.get("location", ""),
                    tags=self.convert_tags_to_dict_type(
                        raw.get("tags", []), key="key", value="value"
                    ),
                    region_code=region,
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
    def convert_bandwidth_gbps(bandwidth):
        try:
            if "Mbps" in bandwidth:
                bw_mbps = bandwidth.replace("Mbps", "")
                return float(bw_mbps / 1000)
            elif "Gbps" in bandwidth:
                return float(bandwidth.replace("Gpbs", ""))
            else:
                return float(0)
        except Exception as e:
            return float(0)

    def _update_times(self, raw):
        raw.update(
            {
                "loaIssueTime": self.datetime_to_iso8601(raw.get("loaIssueTime", "")),
            }
        )
