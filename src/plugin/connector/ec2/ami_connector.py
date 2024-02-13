from plugin.connector.base import ResourceConnector


class EC2Connector(ResourceConnector):
    service_name = 'EC2'
    cloud_service_group = 'EC2'
    cloud_service_type = 'AMI'
    include_vpc_default = False

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = 'EC2'
        self.cloud_service_type = 'AMI'
        self.rest_service_name = 'ec2'

    def get_ami_images(self):
        return self.client.describe_images(Owners=['self'])

    def get_ami_image_attributes(self, image):
        return self.client.describe_image_attribute(Attribute='launchPermission',
                                                    ImageId=image['ImageId'])

    def get_auto_scaling_groups(self):
        paginator = self.client.get_paginator('describe_auto_scaling_groups')
        response_iterator = paginator.paginate(
            PaginationConfig={
                'MaxItems': 10000,
                'PageSize': 50,
            }
        )
        return response_iterator

    def _describe_launch_configuration(self):
        res = self.client.describe_launch_configurations()
        return res.get('LaunchConfigurations', [])

    def _describe_policies(self):
        res = self.client.describe_policies()
        return res.get('ScalingPolicies', [])

    def _describe_lifecycle_hooks(self, auto_scaling_group_name):
        res = self.client.describe_lifecycle_hooks(AutoScalingGroupName=auto_scaling_group_name)
        return res.get('LifecycleHooks', [])

    def _describe_notification_configurations(self):
        res = self.client.describe_notification_configurations()
        return res.get('NotificationConfigurations', [])

    def _describe_scheduled_actions(self, auto_scaling_group_name):
        res = self.client.describe_scheduled_actions(AutoScalingGroupName=auto_scaling_group_name)
        return res.get('ScheduledUpdateGroupActions', [])

