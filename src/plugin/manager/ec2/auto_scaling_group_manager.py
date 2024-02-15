from spaceone.inventory.plugin.collector.lib import make_cloud_service_type

from ..base import ResourceManager, _LOGGER


class AutoScalingGroupManager(ResourceManager):
    cloud_service_group = "EC2"
    cloud_service_type = "AutoScalingGroup"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "EC2"
        self.cloud_service_type = "AutoScalingGroup"
        self.metadata_path = "metadata/ec2/asg.yaml"

    def create_cloud_service_type(self):
        return make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="Cloud Pub/Sub",
            tags={"spaceone:icon": f"{ASSET_URL}/cloud_pubsub.svg"},
            labels=["Application Integration"],
        )

    def create_cloud_service(self, region, options, secret_data, schema):
        self.cloud_service_type = 'AutoScalingGroup'
        cloudwatch_namespace = 'AWS/AutoScaling'
        cloudwatch_dimension_name = 'AutoScalingGroupName'
        cloudtrail_resource_type = 'AWS::AutoScaling::AutoScalingGroup'


        results = self.connector.get_auto_scaling_groups()
        policies = None
        notification_configurations = None

        for data in results:
            for raw in data.get('AutoScalingGroups', []):
                try:
                    if policies is None:
                        policies = self._describe_policies()

                    if notification_configurations is None:
                        notification_configurations = self._describe_notification_configurations()

                    match_lc = self._match_launch_configuration(raw.get('LaunchConfigurationName', ''))
                    match_lt = self._match_launch_template(raw)

                    match_policies = self._match_policies(policies, raw.get('AutoScalingGroupName'))
                    match_noti_confs = self._match_notification_configuration(notification_configurations,
                                                                              raw.get('AutoScalingGroupName'))
                    match_lb_arns = self.get_load_balancer_arns(raw.get('TargetGroupARNs', []))
                    match_lbs = self.get_load_balancer_info(match_lb_arns)

                    raw.update({
                        'launch_configuration': LaunchConfiguration(match_lc, strict=False),
                        'policies': list(map(lambda policy: AutoScalingPolicy(policy, strict=False), match_policies)),
                        'notification_configurations': list(map(lambda noti_conf: NotificationConfiguration(noti_conf,
                                                                                                            strict=False),
                                                                match_noti_confs)),
                        'scheduled_actions': list(map(lambda scheduled_action: ScheduledAction(scheduled_action,
                                                                                               strict=False),
                                                      self._describe_scheduled_actions(raw['AutoScalingGroupName']))),
                        'lifecycle_hooks': list(map(lambda lifecycle_hook: LifecycleHook(lifecycle_hook, strict=False),
                                                    self._describe_lifecycle_hooks(raw['AutoScalingGroupName']))),
                        'autoscaling_tags': list(map(lambda tag: AutoScalingGroupTags(tag, strict=False),
                                                     raw.get('Tags', []))),
                        'instances': self.get_asg_instances(raw.get('Instances', [])),
                        'cloudwatch': self.set_cloudwatch(cloudwatch_namespace, cloudwatch_dimension_name,
                                                          raw['AutoScalingGroupName'], region_name),
                        'cloudtrail': self.set_cloudtrail(region_name, cloudtrail_resource_type,
                                                          raw['AutoScalingGroupName'])
                    })

                    if raw.get('LaunchConfigurationName'):
                        raw.update({
                            'display_launch_configuration_template': raw.get('LaunchConfigurationName')
                        })
                    elif raw.get('MixedInstancesPolicy', {}).get('LaunchTemplate', {}).get(
                            'LaunchTemplateSpecification'):
                        _lt_info = raw.get('MixedInstancesPolicy', {}).get('LaunchTemplate', {}).get(
                            'LaunchTemplateSpecification')
                        raw.update({
                            'display_launch_configuration_template': _lt_info.get('LaunchTemplateName'),
                            'launch_template': match_lt
                        })
                    elif raw.get('LaunchTemplate'):
                        raw.update({
                            'display_launch_configuration_template': raw.get('LaunchTemplate').get(
                                'LaunchTemplateName'),
                            'launch_template': match_lt
                        })

                    else:
                        for instance in raw.get('Instances', []):
                            if instance.get('LaunchTemplate'):
                                raw.update({
                                    'launch_template': match_lt,
                                    'display_launch_configuration_template': instance.get('LaunchTemplate').get(
                                        'LaunchTemplateName')
                                })
                            elif instance.get('LaunchConfigurationName'):
                                raw.update({
                                    'LaunchConfigurationName': instance.get('LaunchConfigurationName'),
                                    'display_launch_configuration_template': instance.get('LaunchConfigurationName')
                                })

                    if raw.get('TargetGroupARNs'):
                        raw.update({
                            'load_balancers': match_lbs,
                            'load_balancer_arns': match_lb_arns
                        })

                    auto_scaling_group_vo = AutoScalingGroup(raw, strict=False)
                    yield {
                        'data': auto_scaling_group_vo,
                        'name': auto_scaling_group_vo.auto_scaling_group_name,
                        'account': self.account_id,
                        'tags': self.convert_tags_to_dict_type(raw.get('Tags', [])),
                        'launched_at': self.datetime_to_iso8601(auto_scaling_group_vo.created_time)
                    }

                except Exception as e:
                    resource_id = raw.get('AutoScalingGroupARN', '')
                    error_resource_response = self.generate_error(region_name, resource_id, e)
                    yield {'data': error_resource_response}


@staticmethod
    def _get_reference(region, image_id):
        return {
            "resource_id": image_id,
            "external_link": f"https://console.aws.amazon.com/ec2/v2/home?region={region}#Images:visibility=public-images;imageId={image_id};sort=name"
        }
