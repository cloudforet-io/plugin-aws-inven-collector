from plugin.connector.base import ResourceConnector


class DatabaseConnector(ResourceConnector):
    service_name = "lightsail"
    cloud_service_group = "Lightsail"
    cloud_service_type = "Database"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "lightsail"
        self.cloud_service_group = "Lightsail"
        self.cloud_service_type = "Database"
        self.rest_service_name = "lightsail"

    def get_relational_databases(self):
        paginator = self.client.get_paginator("get_relational_databases")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def get_relational_database(self, relational_database_name):
        response = self.client.get_relational_database(
            relationalDatabaseName=relational_database_name
        )
        return response.get("relationalDatabase", {})

    def get_relational_database_parameters(self, relational_database_name):
        response = self.client.get_relational_database_parameters(
            relationalDatabaseName=relational_database_name
        )
        return response.get("parameters", [])
