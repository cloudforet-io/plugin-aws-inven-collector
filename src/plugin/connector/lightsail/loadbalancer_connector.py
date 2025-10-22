from plugin.connector.base import ResourceConnector


class LoadBalancerConnector(ResourceConnector):
    service_name = "lightsail"
    cloud_service_group = "Lightsail"
    cloud_service_type = "LoadBalancer"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "lightsail"
        self.cloud_service_group = "Lightsail"
        self.cloud_service_type = "LoadBalancer"
        self.rest_service_name = "lightsail"

    def get_load_balancers(self):
        paginator = self.client.get_paginator("get_load_balancers")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def get_load_balancer(self, load_balancer_name):
        response = self.client.get_load_balancer(loadBalancerName=load_balancer_name)
        return response.get("loadBalancer", {})

    def get_load_balancer_metric_data(
        self, load_balancer_name, metric_name, start_time, end_time
    ):
        response = self.client.get_load_balancer_metric_data(
            loadBalancerName=load_balancer_name,
            metricName=metric_name,
            startTime=start_time,
            endTime=end_time,
        )
        return response.get("metricData", [])
