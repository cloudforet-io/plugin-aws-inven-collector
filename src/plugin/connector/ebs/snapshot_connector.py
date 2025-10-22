from plugin.connector.base import ResourceConnector


class SnapshotConnector(ResourceConnector):
    service_name = "ec2"
    cloud_service_group = "EC2"
    cloud_service_type = "Snapshot"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "ec2"
        self.cloud_service_group = "EC2"
        self.cloud_service_type = "Snapshot"
        self.rest_service_name = "ec2"

    def get_snapshots(self, owner_ids):
        paginator = self.client.get_paginator("describe_snapshots")
        response_iterator = paginator.paginate(
            OwnerIds=owner_ids,
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            },
        )
        return response_iterator
