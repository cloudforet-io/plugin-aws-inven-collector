from ..base import ResourceManager
from spaceone.core.manager import BaseManager


class EC2InstanceManager(BaseManager):

    def __init__(self, ec2_connector, region, **kwargs):
        super().__init__(**kwargs)
        self.ec2_connector = ec2_connector
        self.region = region

    def get_server_info(self, instance, itypes, images, instance_information):
        """
        server_data = {
            "name": ""
            "ip_addresses": [],
            "account": "",
            "type": "",
            "launched_at": "datetime",
            "data":  {
                "primary_ip_address": "",
                "os": {
                    "os_distro": "",
                    "os_arch": "",
                    "os_type": "LINUX" | "WINDOWS",
                    "details": "",
                },
                "aws": {
                    "ami_id" : "",
                    "ebs_optimized": "",
                    "termination_protection": "true" | "false",
                    "iam_instance_profile": {
                        "id": "",
                        "arn": ""
                    },
                    "lifecycle": "spot" | "scheduled",
                    "tags": {},
                },
                "hardware": {
                    "core": 0,
                    "memory": 0
                },
                "compute": {
                    "keypair": "",
                    "availability_zone": "",
                    "instance_state": "",
                    "instance_type": "",
                    "launched_at": "datetime",
                    "instance_id": "",
                    "instance_name": "",
                    "security_groups": [
                        {
                            "id": "",
                            "name": "",
                            "display": ""
                        },
                        ...
                    ],
                    "image": "",
                    "account": "",
                    "tags": {
                        "arn": ""
                    }
                },
            }
        }
        """

        match_image = self.match_image(instance.get("ImageId"), images)

        server_dic = self.get_server_dic(instance)
        # Add OS detail data.
        instance_id = instance.get("InstanceId")

        os_data = self.get_os_data(
            match_image,
            self.get_os_type(instance),
            self.get_os_details(instance),
            instance_information.get(instance_id, {}),
        )
        aws_data = self.get_aws_data(instance)
        hardware_data = self.get_hardware_data(instance, itypes)
        compute_data = self.get_compute_data(instance, match_image)

        # Converting datetime type attributes to ISO8601 format needed to meet protobuf format
        self._update_times([aws_data, compute_data])

        server_dic.update(
            {
                "type": compute_data.get("instance_type"),
                "launched_at": compute_data.get("launched_at"),
                "data": {
                    "os": os_data,
                    "aws": aws_data,
                    "hardware": hardware_data,
                    "compute": compute_data,
                },
            }
        )

        return server_dic

    def get_server_dic(self, instance):
        server_data = {
            "name": self.generate_name(instance),
            "region_code": self.region,
        }
        return server_data

    def get_os_data(self, image, os_type, os_details, instance_information):
        os_data = {
            "os_distro": self.get_os_distro(image.get("Name", ""), os_type),
            "os_arch": image.get("Architecture", ""),
            "os_type": os_type,
        }

        if platform_name := instance_information.get("platform_name"):
            if platform_version := instance_information.get("platform_version"):
                f"{platform_name} {platform_version}"
            else:
                os_data["details"] = platform_name
        else:
            os_data["details"] = os_details
        return os_data

    def get_aws_data(self, instance):
        aws_data = {
            "ami_id": instance.get("ImageId"),
            "ami_launch_index": instance.get("AmiLaunchIndex"),
            "kernel_id": instance.get("KernelId"),
            "monitoring_state": instance.get("Monitoring", {}).get("State", ""),
            "ebs_optimized": instance.get("EbsOptimized"),
            "ena_support": instance.get("EnaSupport"),
            "hypervisor": instance.get("Hypervisor"),
            "placement": instance.get("Placement"),
            "iam_instance_profile": instance.get("IamInstanceProfile"),
            "termination_protection": self.get_termination_protection(
                instance.get("InstanceId")
            ),
            "lifecycle": instance.get("InstanceLifecycle", "scheduled"),
            "auto_recovery": instance.get("MaintenanceOptions", {}).get("AutoRecovery"),
            "boot_mode": instance.get("BootMode"),
            "current_instance_boost": instance.get("CurrentInstanceBootMode"),
            "tpm_support": instance.get("TpmSupport"),
            "platform_details": instance.get("PlatformDetails"),
            "usage_operation": instance.get("UsageOperation"),
            "usage_operation_update_time": instance.get("UsageOperationUpdateTime"),
            "enclave_options": instance.get("EnclaveOptions", {}).get("Enabled"),
            "hibernation_options": instance.get("HibernationOptions", {}).get(
                "Configured"
            ),
            "state_transition_reason": instance.get("StateTransitionReason"),
            "source_desk_check": instance.get("SourceDestCheck"),
            "sriov_net_support": instance.get("SriovNetSupport"),
            "elastic_gpu_associations": instance.get("ElasticGpuAssociations"),
            "elastic_inference_accelerator_associations": instance.get(
                "ElasticInferenceAcceleratorAssociations"
            ),
            "capacity_reservation_id": instance.get("CapacityReservationId"),
            "capacity_reservation_specification": instance.get(
                "CapacityReservationSpecification"
            ),
        }

        return aws_data

    def get_hardware_data(self, instance, itypes):
        hardware_data = {}
        itype = self.match_instance_type(instance.get("InstanceType"), itypes)

        if itype is not None:
            hardware_data = {
                "core": itype.get("VCpuInfo", {}).get("DefaultVCpus", 0),
                "memory": round(
                    float((itype.get("MemoryInfo", {}).get("SizeInMiB", 0)) / 1024), 2
                ),  # 2.0
            }

        return hardware_data

    def get_compute_data(self, instance, image):
        compute_data = {
            # 'eip': self.match_eips_from_instance_id(instance.get('InstanceId'), eips),
            "keypair": instance.get("KeyName", ""),
            "az": instance.get("Placement", {}).get("AvailabilityZone", ""),
            "instance_state": instance.get("State", {}).get("Name").upper(),
            "instance_type": instance.get("InstanceType", ""),
            "launched_at": instance.get("LaunchTime"),
            "instance_id": instance.get("InstanceId"),
            "instance_name": self.generate_name(instance),
            "security_groups": self._get_security_groups(instance),
            "image": image.get("Name", ""),
        }

        return compute_data

    @staticmethod
    def _get_security_groups(instance):
        sg_list = []
        for sg in instance.get("SecurityGroups", []):
            if sg.get("GroupName") is not None:
                sg_name = sg.get("GroupName")
                sg_id = sg.get("GroupId")
                sg_dict = dict(
                    name=sg_name, id=sg_id, display=sg_name + " (" + sg_id + ")"
                )
                sg_list.append(sg_dict)

        return sg_list

    @staticmethod
    def _get_tags_only_string_values(instance):
        tags = {}
        for k, v in instance.get("tags", {}).items():
            if isinstance(v, str):
                tags.update({k: v})
        return tags

    def get_termination_protection(self, instance_id):
        return self.ec2_connector.list_instance_attribute(instance_id)

    def get_os_distro(self, image_name, os_type):
        if image_name == "":
            return os_type.lower()
        else:
            return self.extract_os_distro(image_name, os_type)

    @staticmethod
    def match_image(image_id, images):
        for image in images:
            if image.get("ImageId") == image_id:
                return image
        return {}

    @staticmethod
    def match_eips_from_instance_id(instance_id, eips):
        return [
            eip.get("PublicIp")
            for eip in eips
            if instance_id == eip.get("InstanceId", "")
        ]

    @staticmethod
    def match_instance_type(instance_type, itypes):
        for itype in itypes:
            if itype.get("InstanceType") == instance_type:
                return itype
        return None

    @staticmethod
    def generate_name(resource):
        for resource_tag in resource.get("Tags", []):
            if resource_tag["Key"] == "Name":
                return resource_tag["Value"]
        return ""

    @staticmethod
    def get_os_type(instance):
        return instance.get("Platform", "LINUX").upper()

    @staticmethod
    def get_os_details(instance):
        return instance.get("PlatformDetails", "Linux/UNIX")

    @staticmethod
    def extract_os_distro(image_name, os_type):
        if os_type == "LINUX":
            os_map = {
                "suse": "suse",
                "rhel": "redhat",
                "cetnos": "centos",
                "fedora": "fedora",
                "ubuntu": "ubuntu",
                "debian": "debia",
                "amazon": "amazonlinux",
                "amzn": "amazonlinux",
            }

            image_name.lower()
            for key in os_map:
                if key in image_name:
                    return os_map[key]
            return "linux"

        elif os_type == "WINDOWS":
            os_distro_string = None
            image_splits = image_name.split("-")
            version_cmps = ["2016", "2019", "2012"]

            for version_cmp in version_cmps:
                if version_cmp in image_splits:
                    os_distro_string = f"win{version_cmp}"
            if os_distro_string is not None and "R2_RTM" in image_splits:
                os_distro_string = f"{os_distro_string}r2"
            if os_distro_string is None:
                os_distro_string = "windows"
            return os_distro_string

    def _update_times(self, data_list):
        aws_data, compute_data = data_list
        aws_data.update(
            {
                "usage_operation_update_time": ResourceManager.datetime_to_iso8601(
                    aws_data.get("usage_operation_update_time")
                )
            }
        )
        elastic_gpu_associations = aws_data.get("ElasticGpuAssociations", [])
        for elastic_gpu in elastic_gpu_associations:
            elastic_gpu.update(
                {
                    "ElasticGpuAssociationTime": ResourceManager.datetime_to_iso8601(
                        elastic_gpu.get("ElasticGpuAssociationTime")
                    )
                }
            )
        elastic_inference_accelerator_associations = aws_data.get(
            "ElasticInferenceAcceleratorAssociations", []
        )
        for elastic_inference_accelerator in elastic_inference_accelerator_associations:
            elastic_inference_accelerator.update(
                {
                    "ElasticInferenceAcceleratorAssociationTime": ResourceManager.datetime_to_iso8601(
                        elastic_inference_accelerator.get(
                            "ElasticInferenceAcceleratorAssociationTime"
                        )
                    )
                }
            )

        compute_data.update(
            {
                "launched_at": ResourceManager.datetime_to_iso8601(
                    compute_data.get("launched_at")
                )
            }
        )
