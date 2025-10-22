from plugin.connector.base import ResourceConnector


class RedisConnector(ResourceConnector):
    service_name = "elasticache"
    cloud_service_group = "ElastiCache"
    cloud_service_type = "Redis"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "elasticache"
        self.cloud_service_group = "ElastiCache"
        self.cloud_service_type = "Redis"
        self.rest_service_name = "elasticache"

    def describe_cache_clusters(self):
        paginator = self.client.get_paginator("describe_cache_clusters")
        response_iterator = paginator.paginate(
            ShowCacheNodeInfo=True,
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            },
        )
        return response_iterator

    def describe_replication_groups(self):
        paginator = self.client.get_paginator("describe_replication_groups")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def list_tags_for_resource(self, resource_name):
        response = self.client.list_tags_for_resource(ResourceName=resource_name)
        return response.get("TagList", [])
