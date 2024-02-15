from plugin.connector.base import ResourceConnector


class AMIConnector(ResourceConnector):
    service_name = "ec2"
    cloud_service_group = "EC2"
    cloud_service_type = "AMI"
    include_vpc_default = False

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "ec2"
        self.cloud_service_type = "AMI"
        self.rest_service_name = "ec2"

    def get_ami_images(self):
        return self.client.describe_images(Owners=["self"])

    def get_ami_image_attributes(self, image):
        return self.client.describe_image_attribute(
            Attribute="launchPermission", ImageId=image["ImageId"]
        )
