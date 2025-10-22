from plugin.connector.base import ResourceConnector


class RepositoryConnector(ResourceConnector):
    service_name = "ecr"
    cloud_service_group = "ECR"
    cloud_service_type = "Repository"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "ecr"
        self.cloud_service_group = "ECR"
        self.cloud_service_type = "Repository"
        self.rest_service_name = "ecr"

    def describe_repositories(self):
        paginator = self.client.get_paginator("describe_repositories")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def describe_images(self, repository_name):
        paginator = self.client.get_paginator("describe_images")
        response_iterator = paginator.paginate(
            repositoryName=repository_name,
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            },
        )
        return response_iterator

    def list_tags_for_resource(self, resource_arn):
        response = self.client.list_tags_for_resource(resourceArn=resource_arn)
        return response.get("tags", [])
