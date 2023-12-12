from plugin.connector.collector_connector import CollectorConnector


class EC2Connector(CollectorConnector):
    service_name = 'ec2'
    cloud_service_group = 'EC2'
    include_vpc_default = False

    def __init__(self):
        super().__init__()

    def get_ami_images(self):
        return self.client.describe_images(Owners=['self'])

    def get_ami_image_attributes(self, image):
        return self.client.describe_image_attribute(Attribute='launchPermission',
                                                    ImageId=image['ImageId'])
