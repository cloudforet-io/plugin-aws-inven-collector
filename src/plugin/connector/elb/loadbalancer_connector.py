from plugin.connector.base import ResourceConnector


class LoadBalancerConnector(ResourceConnector):
    service_name = "elbv2"
    cloud_service_group = "ELB"
    cloud_service_type = "LoadBalancer"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "elbv2"
        self.cloud_service_group = "ELB"
        self.cloud_service_type = "LoadBalancer"
        self.rest_service_name = "elbv2"

    def describe_load_balancers(self):
        paginator = self.client.get_paginator("describe_load_balancers")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def describe_load_balancer_attributes(self, load_balancer_arn):
        response = self.client.describe_load_balancer_attributes(
            LoadBalancerArn=load_balancer_arn
        )
        return response.get("Attributes", [])

    def describe_listeners(self, load_balancer_arn):
        paginator = self.client.get_paginator("describe_listeners")
        response_iterator = paginator.paginate(
            LoadBalancerArn=load_balancer_arn,
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            },
        )
        return response_iterator
