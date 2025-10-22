from plugin.connector.base import ResourceConnector


class DiskConnector(ResourceConnector):
    service_name = "lightsail"
    cloud_service_group = "Lightsail"
    cloud_service_type = "Disk"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "lightsail"
        self.cloud_service_group = "Lightsail"
        self.cloud_service_type = "Disk"
        self.rest_service_name = "lightsail"

    def get_disks(self):
        paginator = self.client.get_paginator("get_disks")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def get_disk(self, disk_name):
        response = self.client.get_disk(diskName=disk_name)
        return response.get("disk", {})

    def get_disk_snapshot(self, disk_snapshot_name):
        response = self.client.get_disk_snapshot(diskSnapshotName=disk_snapshot_name)
        return response.get("diskSnapshot", {})
