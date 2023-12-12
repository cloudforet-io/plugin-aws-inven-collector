from ...manager.collector_manager import CollectorManager


class InstanceManager(CollectorManager):
    manager='instance'
    def collect(self, options, secret_data, schema, task_options):
        pass