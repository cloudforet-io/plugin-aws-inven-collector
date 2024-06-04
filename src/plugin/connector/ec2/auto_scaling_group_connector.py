from plugin.conf.cloud_service_conf import BOTO3_HTTPS_VERIFIED
from plugin.connector.base import ResourceConnector


class AutoScalingGroupConnector(ResourceConnector):
    service_name = "autoscaling"
    cloud_service_group = "EC2"
    cloud_service_type = "AutoScalingGroup"
    include_vpc_default = False

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "autoscaling"
        self.cloud_service_type = "AutoScalingGroup"
        self.rest_service_name = "autoscaling"

    def get_auto_scaling_groups(self):
        paginator = self.client.get_paginator("describe_auto_scaling_groups")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def get_launch_templates(self):
        lt_client = self.session.client("ec2", verify=BOTO3_HTTPS_VERIFIED)
        paginator = lt_client.get_paginator("describe_launch_templates")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def get_launch_configurations(self):
        paginator = self.client.get_paginator("describe_launch_configurations")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def describe_launch_template_versions(self, lt):
        lt_client = self.session.client("ec2", verify=BOTO3_HTTPS_VERIFIED)
        lt_versions = lt_client.describe_launch_template_versions(LaunchTemplateId=lt)
        return lt_versions

    def describe_instances(self, instance_ids):
        ec2_client = self.session.client("ec2", verify=BOTO3_HTTPS_VERIFIED)
        res = ec2_client.describe_instances(InstanceIds=instance_ids)
        return res

    def describe_target_groups(self, tg_arns):
        elb_client = self.session.client("elbv2", verify=BOTO3_HTTPS_VERIFIED)
        res = elb_client.describe_target_groups(TargetGroupArns=tg_arns)
        return res

    def describe_load_balancers(self, lb_arns):
        elb_client = self.session.client("elbv2", verify=BOTO3_HTTPS_VERIFIED)
        res = elb_client.describe_load_balancers(LoadBalancerArns=lb_arns).get(
            "LoadBalancers", []
        )
        return res

    def describe_listeners(self, lb_arn):
        elb_client = self.session.client("elbv2", verify=BOTO3_HTTPS_VERIFIED)
        res = elb_client.describe_listeners(lb_arn).get("Listeners", [])
        return res

    def describe_launch_configuration(self):
        res = self.client.describe_launch_configurations()
        return res.get("LaunchConfigurations", [])

    def describe_policies(self):
        res = self.client.describe_policies()
        return res.get("ScalingPolicies", [])

    def describe_lifecycle_hooks(self, auto_scaling_group_name):
        res = self.client.describe_lifecycle_hooks(
            AutoScalingGroupName=auto_scaling_group_name
        )
        return res.get("LifecycleHooks", [])

    def describe_notification_configurations(self):
        res = self.client.describe_notification_configurations()
        return res.get("NotificationConfigurations", [])

    def describe_scheduled_actions(self, auto_scaling_group_name):
        res = self.client.describe_scheduled_actions(
            AutoScalingGroupName=auto_scaling_group_name
        )
        return res.get("ScheduledUpdateGroupActions", [])
