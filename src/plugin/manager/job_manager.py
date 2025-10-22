from plugin.conf.cloud_service_conf import METRIC_SERVICES, GLOBAL_SERVICES, SERVICE_NAME_MAP
from plugin.manager.base import ResourceManager


class JobManager():
    def __init__(self, options: dict, secret_data: dict):
        self.options = options
        self.secret_data = secret_data

    def get_tasks(self):
        tasks = []
        services = self._set_service_filter()
        regions = self._set_region_filter()

        # create task 1: task for collecting only cloud service type metadata
        tasks.extend(self._add_cloud_service_type_tasks(services))

        # create task 2: task for collecting only cloud service region metadata
        tasks.extend(self._add_cloud_service_region_tasks(regions))

        # create task 3: task for collecting only metrics
        tasks.extend(self._add_metric_tasks(services))

        # create task 4: task for collecting only cloud service group metadata
        tasks.extend(self._add_cloud_service_group_tasks(services, regions))

        return {"tasks": tasks}

    def _set_service_filter(self):
        available_services = ResourceManager.get_service_names()

        if service_filter := self.options.get("service_filter"):
            self._validate_service_filter(service_filter, available_services)
            return service_filter
        else:
            return available_services

    @staticmethod
    def _validate_service_filter(service_filter, available_services):
        if not isinstance(service_filter, list):
            raise ValueError(
                f"Services input is supposed to be a list type! Your input is {service_filter}."
            )
        for each_service in service_filter:
            if each_service not in available_services:
                raise ValueError("Not a valid service!")

    def _set_region_filter(self):
        available_regions = ResourceManager.get_region_names(self.secret_data)

        if region_filter := self.options.get("region_filter"):
            self._validate_region_filter(region_filter, available_regions)
            return region_filter
        else:
            return available_regions

    @staticmethod
    def _validate_region_filter(region_filter, available_regions):
        if not isinstance(region_filter, list):
            raise ValueError(
                f"Regions input is supposed to be a list type! Your input is {region_filter}."
            )
        for each_region in region_filter:
            if each_region not in available_regions:
                raise ValueError("Not a valid region!")

    def _add_cloud_service_type_tasks(self, services: list) -> list:
        return [
            self._make_task_wrapper(
                resource_type="inventory.CloudServiceType", services=services
            )
        ]

    def _add_metric_tasks(self, services: list) -> list:
        return [
            self._make_task_wrapper(
                resource_type="inventory.Metric",
                services=services,
            )
        ]

    def _add_cloud_service_region_tasks(self, regions: list) -> list:
        return [self._make_task_wrapper(resource_type="inventory.Region", regions=regions)]

    def _add_cloud_service_group_tasks(self, services: list[str], regions: list[str]) -> list:
        tasks = []
        for service in services:
            service_regions = self._get_service_supported_regions(service, regions)
            
            for region in service_regions:
                tasks.append(
                    self._make_task_wrapper(
                        resource_type="inventory.CloudService",
                        service=service,
                        region=region,
                    )
                )
        return tasks
    
    def _get_service_supported_regions(self, service_name: str, available_regions: list[str]) -> list:
        if service_name in GLOBAL_SERVICES:
            return ["global"]
        
        aws_supported_regions = ResourceManager.get_available_regions(self.secret_data, SERVICE_NAME_MAP.get(service_name))
            
        aws_regions_set = set(aws_supported_regions)
        available_regions_set = set(available_regions)
        intersection = aws_regions_set.intersection(available_regions_set)
            
        return list(intersection)

    @staticmethod
    def _make_task_wrapper(**kwargs) -> dict:
        task_options = {"task_options": {}}
        for key, value in kwargs.items():
            task_options["task_options"][key] = value
        return task_options