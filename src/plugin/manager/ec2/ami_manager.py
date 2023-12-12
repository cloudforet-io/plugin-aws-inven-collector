from ...manager.collector_manager import CollectorManager, _LOGGER
from ..ec2 import EC2Manager


class AMIManager(EC2Manager):
    service_type = 'AMI'

    def collect(self, options, secret_data, schema, task_options):
        service = task_options.get('service')
        region = task_options.get('region')
        self.cloud_service_type = 'AMI'
        cloudtrail_resource_type = 'AWS::EC2::Ami'

        results = self.connector.get_ami_images()
        account_id = self.connector.get_account_id()

        for image in results.get('Images', []):
            try:
                try:
                    permission_info = self.connector.get_ami_image_attributes(image)

                    if permission_info:
                        image.update({
                            'launch_permissions': [_permission for _permission in
                                                   permission_info.get('LaunchPermissions', [])]
                        })

                except Exception as e:
                    _LOGGER.debug(f"[ami][request_ami_data] SKIP: {e}")

                image.update({
                    'cloudtrail': self.set_cloudtrail(region, cloudtrail_resource_type, image['ImageId'])
                })

                image_vo = image
                yield {
                    'data': image_vo,
                    'name': image_vo.get('Name', ''),
                    'instance_type': image_vo.get('ImageType', ''),
                    'account': account_id,
                    'tags': self.convert_tags_to_dict_type(image.get('Tags', []))
                }

            except Exception as e:
                resource_id = image.get('ImageId', '')
                error_resource_response = self.generate_error(service, region, resource_id, service,
                                                              self.cloud_service_type, e)
                yield {'data': error_resource_response}
