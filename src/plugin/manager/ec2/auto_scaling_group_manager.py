import time

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)
from ..base import ResourceManager, _LOGGER
from ...conf.cloud_service_conf import ASSET_URL


class AutoScalingGroupManager(ResourceManager):
    cloud_service_group = "EC2"
    cloud_service_type = "AutoScalingGroup"
    _launch_configurations = None
    _launch_templates = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "EC2"
        self.cloud_service_type = "AutoScalingGroup"
        self.metadata_path = "metadata/ec2/asg.yaml"
        self._launch_configurations = []
        self._launch_templates = []

    def create_cloud_service_type(self):
        metadata_name = "LaunchConfiguration"
        lf_metadata_path = "metadata/ec2/lf.yaml"
        cloud_service_type_results = []
        lf_cst_result = self._create_additional_cloud_service_type(
            metadata_name, lf_metadata_path
        )
        cloud_service_type_results.append(lf_cst_result)

        metadata_name = "LaunchTemplate"
        lt_metadata_path = "metadata/ec2/lt.yaml"
        lt_cst_result = self._create_additional_cloud_service_type(
            metadata_name, lt_metadata_path
        )
        cloud_service_type_results.append(lt_cst_result)

        asg_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonEC2",
            tags={"spaceone:icon": f"{ASSET_URL}/Amazon-EC2-Auto-Scaling.svg"},
            labels=["Compute"],
        )
        cloud_service_type_results.append(asg_cst_result)
        return cloud_service_type_results

    def create_cloud_service(self, region, options, secret_data, schema):
        self.cloud_service_type = "AutoScalingGroup"
        cloudwatch_namespace = "AWS/AutoScaling"
        cloudwatch_dimension_name = "AutoScalingGroupName"
        cloudtrail_resource_type = "AWS::AutoScaling::AutoScalingGroup"

        pre_collect_list = [
            self._create_launch_configurations,
            self._create_launch_templates,
        ]
        for pre_collect in pre_collect_list:
            yield from pre_collect(region)
        results = self.connector.get_auto_scaling_groups()
        self.connector.set_account_id()
        account_id = self.connector.get_account_id()
        policies = None
        notification_configurations = None

        for data in results:
            for raw in data.get("AutoScalingGroups", []):
                try:
                    if policies is None:
                        policies = self.connector.describe_policies()

                    if notification_configurations is None:
                        notification_configurations = (
                            self.connector.describe_notification_configurations()
                        )

                    match_lc = self._match_launch_configuration(
                        raw.get("LaunchConfigurationName", "")
                    )
                    match_lt = self._match_launch_template(raw)

                    match_policies = self._match_policies(
                        policies, raw.get("AutoScalingGroupName")
                    )
                    match_noti_confs = self._match_notification_configuration(
                        notification_configurations, raw.get("AutoScalingGroupName")
                    )
                    match_lb_arns = self.get_load_balancer_arns(
                        raw.get("TargetGroupARNs", [])
                    )
                    match_lbs = self.get_load_balancer_info(match_lb_arns)

                    raw.update(
                        {
                            "launch_configuration": match_lc,
                            "policies": list(
                                map(lambda policy: policy, match_policies)
                            ),
                            "notification_configurations": list(
                                map(lambda noti_conf: noti_conf, match_noti_confs)
                            ),
                            "scheduled_actions": list(
                                map(
                                    lambda scheduled_action: scheduled_action,
                                    self.connector.describe_scheduled_actions(
                                        raw["AutoScalingGroupName"]
                                    ),
                                )
                            ),
                            "lifecycle_hooks": list(
                                map(
                                    lambda lifecycle_hook: lifecycle_hook,
                                    self.connector.describe_lifecycle_hooks(
                                        raw["AutoScalingGroupName"]
                                    ),
                                )
                            ),
                            "autoscaling_tags": list(
                                map(lambda tag: tag, raw.get("Tags", []))
                            ),
                            "instances": self.get_asg_instances(
                                raw.get("Instances", [])
                            ),
                            "cloudwatch": self.set_cloudwatch(
                                cloudwatch_namespace,
                                cloudwatch_dimension_name,
                                raw["AutoScalingGroupName"],
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                region,
                                cloudtrail_resource_type,
                                raw["AutoScalingGroupName"],
                            ),
                        }
                    )

                    if raw.get("LaunchConfigurationName"):
                        raw.update(
                            {
                                "display_launch_configuration_template": raw.get(
                                    "LaunchConfigurationName"
                                )
                            }
                        )
                    elif (
                        raw.get("MixedInstancesPolicy", {})
                        .get("LaunchTemplate", {})
                        .get("LaunchTemplateSpecification")
                    ):
                        _lt_info = (
                            raw.get("MixedInstancesPolicy", {})
                            .get("LaunchTemplate", {})
                            .get("LaunchTemplateSpecification")
                        )
                        raw.update(
                            {
                                "display_launch_configuration_template": _lt_info.get(
                                    "LaunchTemplateName"
                                ),
                                "launch_template": match_lt,
                            }
                        )
                    elif raw.get("LaunchTemplate"):
                        raw.update(
                            {
                                "display_launch_configuration_template": raw.get(
                                    "LaunchTemplate"
                                ).get("LaunchTemplateName"),
                                "launch_template": match_lt,
                            }
                        )

                    else:
                        for instance in raw.get("Instances", []):
                            if instance.get("LaunchTemplate"):
                                raw.update(
                                    {
                                        "launch_template": match_lt,
                                        "display_launch_configuration_template": instance.get(
                                            "LaunchTemplate"
                                        ).get(
                                            "LaunchTemplateName"
                                        ),
                                    }
                                )
                            elif instance.get("LaunchConfigurationName"):
                                raw.update(
                                    {
                                        "LaunchConfigurationName": instance.get(
                                            "LaunchConfigurationName"
                                        ),
                                        "display_launch_configuration_template": instance.get(
                                            "LaunchConfigurationName"
                                        ),
                                    }
                                )

                    if raw.get("TargetGroupARNs"):
                        raw.update(
                            {
                                "load_balancers": match_lbs,
                                "load_balancer_arns": match_lb_arns,
                            }
                        )

                    # Converting datetime type attributes to ISO8601 format needed to meet protobuf format
                    self._update_times(raw)

                    auto_scaling_group_vo = raw

                    resource_id = auto_scaling_group_vo.get("AutoScalingGroupARN", "")
                    auto_scaling_group_name = auto_scaling_group_vo.get(
                        "AutoScalingGroupName", ""
                    )
                    link = f"https://console.aws.amazon.com/ec2/autoscaling/home?region={region}#AutoScalingGroups:id={auto_scaling_group_name}"
                    reference = self.get_reference(resource_id, link)

                    cloud_service = make_cloud_service(
                        name=auto_scaling_group_vo.get("AutoScalingGroupName", ""),
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=auto_scaling_group_vo,
                        account=account_id,
                        tags=self.convert_tags_to_dict_type(raw.get("Tags", [])),
                        region_code=region,
                        reference=reference,
                    )
                    yield cloud_service
                    # yield {
                    #     'data': auto_scaling_group_vo,
                    #     'name': auto_scaling_group_vo.auto_scaling_group_name,
                    #     'account': self.account_id,
                    #     'tags': self.convert_tags_to_dict_type(raw.get('Tags', [])),
                    #     'launched_at': self.datetime_to_iso8601(auto_scaling_group_vo.created_time)
                    # }

                except Exception as e:
                    # resource_id = raw.get('AutoScalingGroupARN', '')
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

    def get_asg_instances(self, instances):
        # ec2_client = self.session.client('ec2', verify=BOTO3_HTTPS_VERIFIED)
        max_count = 20
        instances_from_ec2 = []
        split_instances = [
            instances[i : i + max_count] for i in range(0, len(instances), max_count)
        ]

        for instances in split_instances:
            try:
                instance_ids = [
                    _instance.get("InstanceId")
                    for _instance in instances
                    if _instance.get("InstanceId")
                ]
                # response = ec2_client.describe_instances(InstanceIds=instance_ids)
                response = self.connector.describe_instances(instance_ids)

                for reservation in response.get("Reservations", []):
                    instances_from_ec2.extend(reservation.get("Instances", []))
            except Exception as e:
                _LOGGER.debug(f"[autoscaling] instance not found: {instance_ids}")

        for instance in instances:
            for instance_from_ec2 in instances_from_ec2:
                if instance_from_ec2.get("InstanceId") == instance.get("InstanceId"):
                    instance.update(
                        {
                            "lifecycle": instance_from_ec2.get(
                                "InstanceLifecycle", "scheduled"
                            )
                        }
                    )
                    break

        return instances

    def get_load_balancer_arns(self, target_group_arns):
        # elb_client = self.session.client('elbv2', verify=BOTO3_HTTPS_VERIFIED)
        lb_arns = []
        max_count = 20

        split_tgs_arns = [
            target_group_arns[i : i + max_count]
            for i in range(0, len(target_group_arns), max_count)
        ]

        for tg_arns in split_tgs_arns:
            try:
                # response = elb_client.describe_target_groups(TargetGroupArns=tg_arns)
                response = self.connector.describe_target_groups(tg_arns)
                for target_group in response.get("TargetGroups", []):
                    lb_arns.extend(target_group.get("LoadBalancerArns", []))
            except Exception as e:
                _LOGGER.debug(f"[autoscaling] target group not found: {tg_arns}")

        return lb_arns

    def get_load_balancer_info(self, lb_arns):
        # elb_client = self.session.client('elbv2', verify=BOTO3_HTTPS_VERIFIED)
        max_count = 20

        split_lb_arns = [
            lb_arns[i : i + max_count] for i in range(0, len(lb_arns), max_count)
        ]

        load_balancer_data_list = []

        for lb_arns in split_lb_arns:
            try:
                # lbs = elb_client.describe_load_balancers(LoadBalancerArns=lb_arns).get('LoadBalancers', [])
                lbs = self.connector.describe_load_balancers(lb_arns).get(
                    "LoadBalancers", []
                )
                for lb in lbs:
                    lb_arn = lb.get("LoadBalancerArn", "")
                    # listeners = elb_client.describe_listeners(LoadBalancerArn=lb_arn).get('Listeners', [])
                    listeners = self.connector.describe_listeners(lb_arn).get(
                        "Listeners", []
                    )
                    lb.update({"listeners": listeners})
                    load_balancer_data_list.append(self.get_load_balancer_data(lb))

                    # avoid to API Rate limitation.
                    time.sleep(0.5)

            except Exception as e:
                _LOGGER.debug(f"[autoscaling] ELB not found: {lb_arns}")

        return load_balancer_data_list

    @staticmethod
    def get_load_balancer_data(match_load_balancer):
        return {
            "endpoint": match_load_balancer.get("DNSName", ""),
            "type": match_load_balancer.get("Type"),
            "scheme": match_load_balancer.get("Scheme"),
            "name": match_load_balancer.get("LoadBalancerName", ""),
            "protocol": [
                listener.get("Protocol")
                for listener in match_load_balancer.get("listeners", [])
                if listener.get("Protocol")
            ],
            "port": [
                listener.get("Port")
                for listener in match_load_balancer.get("listeners", [])
                if listener.get("Port")
            ],
            "tags": {"arn": match_load_balancer.get("LoadBalancerArn", "")},
        }

    def _match_launch_configuration(self, lc):
        return next(
            (
                launch_configuration
                for launch_configuration in self._launch_configurations
                if launch_configuration.launch_configuration_name == lc
            ),
            "",
        )

    def _match_launch_template(self, raw):
        lt_dict = {}

        if raw.get("LaunchTemplate"):
            lt_dict = raw.get("LaunchTemplate")
        elif (
            raw.get("MixedInstancesPolicy", {})
            .get("LaunchTemplate", {})
            .get("LaunchTemplateSpecification")
        ):
            lt_dict = (
                raw.get("MixedInstancesPolicy", {})
                .get("LaunchTemplate", {})
                .get("LaunchTemplateSpecification")
            )
        else:
            for instance in raw.get("Instances", []):
                if instance.get("LaunchTemplate"):
                    lt_dict = instance.get("LaunchTemplate")

        return next(
            (
                launch_template
                for launch_template in self._launch_templates
                if launch_template.get("LaunchTemplateId")
                == lt_dict.get("LaunchTemplateId")
            ),
            None,
        )

    @staticmethod
    def _match_policies(policies, asg_name):
        match_policies = []

        for _policy in policies:
            if _policy["AutoScalingGroupName"] == asg_name:
                match_policies.append(_policy)

        return match_policies

    @staticmethod
    def _match_notification_configuration(notification_configurations, asg_name):
        match_noti_confs = []

        for _noti_conf in notification_configurations:
            if _noti_conf["AutoScalingGroupName"] == asg_name:
                match_noti_confs.append(_noti_conf)

        return match_noti_confs

    def _match_launch_template_version(self, lt):
        lt_versions = self.connector.describe_launch_template_versions(lt)
        res = lt_versions.get("LaunchTemplateVersions", [])[0]
        return res

    @staticmethod
    def _match_launch_template_data(lt_ver):
        res = lt_ver.get("LaunchTemplateData", [])
        return res

    # @staticmethod
    # def _match_lifecycle_hook(lifecycle_hooks, asg_name):
    #     match_lifecycle_kooks = []
    #
    #     for _lifecycle_hook in lifecycle_hooks:
    #         if _lifecycle_hook['AutoScalingGroupName'] == asg_name:
    #             match_lifecycle_kooks.append(_lifecycle_hook)
    #
    #     return match_lifecycle_kooks
    def _create_launch_configurations(self, region):
        cloud_service_type = "LaunchConfiguration"
        cloudtrail_resource_type = "AWS::AutoScaling::LaunchConfiguration"

        response = self.connector.get_launch_configurations()
        self.connector.set_account_id()
        account_id = self.connector.get_account_id()
        result_list = []
        for data in response:
            for raw in data.get("LaunchConfigurations", []):
                try:
                    raw.update(
                        {
                            "cloudtrail": self.set_cloudtrail(
                                region,
                                cloudtrail_resource_type,
                                raw["LaunchConfigurationName"],
                            )
                        }
                    )

                    launch_configuration_vo = raw
                    self._launch_configurations.append(launch_configuration_vo)

                    resource_id = launch_configuration_vo.get(
                        "LaunchConfigurationARN", ""
                    )
                    launch_configuration_name = launch_configuration_vo.get(
                        "LaunchConfigurationName", ""
                    )
                    link = f"https://console.aws.amazon.com/ec2/autoscaling/home?region={region}#LaunchConfigurations:id={launch_configuration_name}"
                    reference = self.get_reference(resource_id, link)

                    cloud_service = make_cloud_service(
                        name=launch_configuration_vo.get("LaunchConfigurationName", ""),
                        cloud_service_type=cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=launch_configuration_vo,
                        account=account_id,
                        region_code=region,
                        reference=reference,
                    )
                    result_list.append(cloud_service)
                    # yield {
                    #     'data': launch_configuration_vo,
                    #     'name': launch_configuration_vo.launch_configuration_name,
                    #     'account': account_id,
                    #     'launched_at': self.datetime_to_iso8601(launch_configuration_vo.created_time)
                    # }

                except Exception as e:
                    # resource_id = raw.get('LaunchConfigurationARN', '')
                    error_response = make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=cloud_service_type,
                        region_name=region,
                    )
                    result_list.append(error_response)

        return result_list

    def _create_launch_templates(self, region):
        cloud_service_type = "LaunchTemplate"
        cloudtrail_resource_type = "AWS::AutoScaling::LaunchTemplate"

        response = self.connector.get_launch_templates()
        self.connector.set_account_id()
        account_id = self.connector.get_account_id()
        result_list = []
        for data in response:
            for raw in data.get("LaunchTemplates", []):
                try:
                    match_lt_version = self._match_launch_template_version(
                        raw.get("LaunchTemplateId")
                    )
                    match_lt_data = self._match_launch_template_data(match_lt_version)

                    raw.update(
                        {
                            "version": match_lt_version.get("VersionNumber"),
                            "version_description": match_lt_version.get(
                                "VersionDescription"
                            ),
                            "ami_id": match_lt_data.get("ImageId", ""),
                            "default_version": match_lt_version.get("DefaultVersion"),
                            "launch_template_data": match_lt_data,
                            "arn": self.generate_arn(
                                service="ec2",
                                region="",
                                account_id="",
                                resource_type="launch_template",
                                resource_id=raw["LaunchTemplateId"]
                                + "/v"
                                + str(match_lt_version.get("VersionNumber")),
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                region,
                                cloudtrail_resource_type,
                                raw["LaunchTemplateName"],
                            ),
                        }
                    )

                    launch_template_vo = raw

                    self._update_lt_times(launch_template_vo)
                    self._launch_templates.append(launch_template_vo)

                    resource_id = launch_template_vo.get("arn", "")
                    launch_template_id = launch_template_vo.get("LaunchTemplateId", "")
                    link = f"https://console.aws.amazon.com/ec2autoscaling/home?region={region}#/details?id={launch_template_id}"
                    reference = self.get_reference(resource_id, link)

                    cloud_service = make_cloud_service(
                        name=launch_template_vo.get("LaunchTemplateName", ""),
                        cloud_service_type=cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=launch_template_vo,
                        account=account_id,
                        tags=self.convert_tags_to_dict_type(raw.get("Tags", [])),
                        region_code=region,
                        reference=reference,
                    )
                    result_list.append(cloud_service)
                    # yield {
                    #     'data': launch_template_vo,
                    #     'name': launch_template_vo.launch_template_name,
                    #     'account': self.account_id,
                    #     'tags': self.convert_tags_to_dict_type(raw.get('Tags', [])),
                    #     'launched_at': self.datetime_to_iso8601(launch_template_vo.create_time)
                    # }

                except Exception as e:
                    # resource_id = raw.get('LaunchConfigurationARN', '')
                    error_response = make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=cloud_service_type,
                        region_name=region,
                    )
                    result_list.append(error_response)

        return result_list

    def _create_additional_cloud_service_type(self, name, metadata_path):
        return make_cloud_service_type(
            name=name,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonEC2",
            tags={"spaceone:icon": f"{ASSET_URL}/Amazon-EC2-Auto-Scaling.svg"},
            labels=["Compute"],
        )

    def _update_times(self, autoscaling_info: dict) -> None:
        autoscaling_info.update(
            {
                "CreatedTime": self.datetime_to_iso8601(
                    autoscaling_info.get("CreatedTime")
                ),
            }
        )
        launch_configuration = autoscaling_info.get("launch_configuration", {})
        if launch_configuration:
            launch_configuration.update(
                {
                    "CreatedTime": self.datetime_to_iso8601(
                        launch_configuration.get("CreatedTime")
                    )
                }
            )
        scheduled_actions = autoscaling_info.get("scheduled_actions", [])
        for schedule_action in scheduled_actions:
            schedule_action.update(
                {
                    "Time": self.datetime_to_iso8601(schedule_action.get("Time")),
                    "StartTime": self.datetime_to_iso8601(
                        schedule_action.get("StartTime")
                    ),
                    "EndTime": self.datetime_to_iso8601(schedule_action.get("EndTime")),
                }
            )
        launch_template = autoscaling_info.get("launch_template", {})
        if launch_template:
            print(launch_template.get("CreateTime"))
            print("EXISTS?")
            launch_template.update(
                {
                    "CreateTime": self.datetime_to_iso8601(
                        launch_template.get("CreateTime")
                    )
                }
            )

    def _update_lt_times(self, lt_info: dict) -> None:
        lt_info.update(
            {"CreateTime": self.datetime_to_iso8601(lt_info.get("CreateTime"))}
        )
