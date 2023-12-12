from .instance_manager import InstanceManager
from .volume_manager import VolumeManager
from .ami_manager import AMIManager
from .auto_scaling_group_manager import AutoScalingGroupManager
from .eip_manager import EIPManager
from .launch_configuration_manager import LaunchConfigurationManager
from .launch_template_manager import LaunchTemplateManager
from .security_group_manager import SecurityGroupManager
from .snapshot_manager import SnapshotManager
from ..collector_manager import CollectorManager
from ...connector.ec2.connector import EC2Connector


class EC2Manager(CollectorManager):
    service = 'ec2'
    # _all_managers = {
    #     InstanceManager: 'instance', VolumeManager: 'volume', AMIManager: 'ami',
    #     AutoScalingGroupManager: 'auto_scaling_group', EIPManager: 'eip',
    #     LaunchConfigurationManager: 'launch_configuration', LaunchTemplateManager: 'launch_template',
    #     SecurityGroupManager: 'security_group', SnapshotManager: 'snapshot'}

    def collect(self, options, secret_data, schema, task_options):
        '''
        TODO: find out a better way to iterate through all managers without making manual list of managers.
        '''
        self.connector = EC2Connector()
        region = task_options.get('region')
        resources = []
        self.create_session(secret_data, region)

        # managers = self.get_all_managers()
        managers = EC2Manager.get_all_managers_in_service()
        # for manager in self._all_managers:
        for manager in managers:
            if self._all_managers[manager] == 'ami':
                resources.extend(
                    self.collect_resources(manager, self._all_managers[manager], options, secret_data, schema,
                                           task_options))
        return resources

    def collect_resources(self, manager, service_type_name, options, secret_data, schema, task_options):
        print('AM I HERE?')
        resources = []
        additional_data = ['name', 'type', 'size', 'launched_at']
        region = task_options.get('region')
        try:
            mgr = manager(self.session)
            for collected_dict in mgr.collect(options, secret_data, schema, task_options):
                data = collected_dict['data']
                if getattr(data, 'resource_type', None) and data.resource_type == 'inventory.ErrorResource':
                    # Error Resource
                    resources.append(data)
                else:
                    # Cloud Service Resource
                    if getattr(data, 'set_cloudwatch', None):
                        data.cloudwatch = data.set_cloudwatch(region)

                    resource_dict = {
                        'data': data,
                        'account': collected_dict.get('account'),
                        'instance_size': float(collected_dict.get('instance_size', 0)),
                        'instance_type': collected_dict.get('instance_type', ''),
                        'launched_at': str(collected_dict.get('launched_at', '')),
                        'tags': collected_dict.get('tags', {}),
                        'region_code': region,
                        'reference': data.reference(region)
                    }

                    for add_field in additional_data:
                        if add_field in collected_dict:
                            resource_dict.update({add_field: collected_dict[add_field]})
                    resources.append({'resource': resource_dict})
        except Exception as e:
            resource_id = ''
            error_resource_response = self.generate_error("ec2", region, resource_id, "EC2", service_type_name, e)
            resources.append(error_resource_response)

        return resources

    @classmethod
    def get_all_managers_in_service(cls):
        return cls.__subclasses__()
