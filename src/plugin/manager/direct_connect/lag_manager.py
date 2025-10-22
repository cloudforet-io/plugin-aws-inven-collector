from spaceone.inventory.plugin.collector.lib import *
from ..base import ResourceManager
from ...conf.cloud_service_conf import *

from ...model.direct_connect import LAG


class LAGManager(ResourceManager):
    cloud_service_group = "DirectConnect"
    cloud_service_type = "LAG"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "DirectConnect"
        self.cloud_service_type = "LAG"
        self.metadata_path = "metadata/direct_connect/lag.yaml"

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
        yield from self._collect_lags(options, region)

    def _collect_lags(self, options, region):
        results = self.connector.get_lags()
        for raw in results.get("lags", []):
            try:
                raw.update(
                    {"cloudtrail": self.set_cloudtrail(self.cloud_service_group, raw["lagId"], region)}
                )

                for lag_connection in raw.get("connections", []):
                    bandwidth_size = self.convert_bandwidth_gbps(
                        lag_connection.get("bandwidth", "")
                    )

                    if bandwidth_size:
                        lag_connection.update({"bandwidth_gbps": bandwidth_size})

                lag_vo = LAG(raw, strict=False)
                lag_id = lag_vo.get("lagId", "")
                owner_account = lag_vo.get("ownerAccount", "")
                link = f"https://console.aws.amazon.com/directconnect/v2/home?region={region}#/lags/arn:aws:directconnect:{region}:{owner_account}:{lag_id}"
                reference = self.get_reference(lag_id, link)

                cloud_service = make_cloud_service(
                    name=lag_vo.get("lagName", ""),
                    cloud_service_type=self.cloud_service_type,
                    cloud_service_group=self.cloud_service_group,
                    provider=self.provider,
                    data=lag_vo.to_primitive(),
                    account=options.get("account_id"),
                    reference=reference,
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
