from plugin.connector.base import ResourceConnector


class ClusterConnector(ResourceConnector):
    service_name = "docdb"
    cloud_service_group = "DocumentDB"
    cloud_service_type = "Cluster"
    include_vpc_default = False

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "docdb"
        self.cloud_service_type = "Cluster"
        self.cloud_service_group = "DocumentDB"
        self.rest_service_name = "docdb"

    def get_db_clusters(self):
        paginator = self.client.get_paginator("describe_db_clusters")
        response_iterator = paginator.paginate(
            Filters=[{"Name": "engine", "Values": ["docdb"]}],
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            },
        )
        return response_iterator

    def get_db_cluster_parameter_groups(self):
        return self.client.describe_db_cluster_parameter_groups()

    def get_db_subnet_groups(self):
        paginator = self.client.get_paginator("describe_db_subnet_groups")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def describe_db_instances(self):
        paginator = self.client.get_paginator("describe_db_instances")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def describe_db_cluster_snapshots(self):
        return self.client.describe_db_cluster_snapshots()

    def list_tags_for_resource(self, resource_name):
        return self.client.list_tags_for_resource(ResourceName=resource_name)

    def describe_db_cluster_parameters(self, pg_name):
        return self.client.describe_db_cluster_parameters(
            DBClusterParameterGroupName=pg_name
        )
