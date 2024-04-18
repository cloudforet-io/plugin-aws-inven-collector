from spaceone.core.manager import BaseManager


class CloudWatchManager(BaseManager):

    def set_cloudwatch_info(self, instance_id, region_name):
        """
        data.cloudwatch: {
            "metrics_info": [
                {
                    "Namespace": "AWS/EC2",
                    "Dimensions": [
                        {
                            "Name": "InstanceId",
                            "Value": "i-xxxxxx"
                        }
                    ]
                },
                {
                    "Namespace": "CWAgent",
                    "Dimensions": [
                        {
                            "Name": "InstanceId",
                            "Value": "i-xxxxxx"
                        }
                    ]
                }
            ]
            "region_name": region_name
        }
        """

        cloudwatch_data = {
            "region_name": region_name if region_name else "us-east-1",
            "metrics_info": self.set_metrics_info(instance_id),
        }

        return cloudwatch_data

    def set_metrics_info(self, instance_id):
        ec2_metric_info = {
            "Namespace": "AWS/EC2",
            "Dimensions": self.set_dimensions(instance_id),
        }
        cwagent_metric_info = {
            "Namespace": "CWAgent",
            "Dimensions": self.set_dimensions(instance_id),
        }
        return [ec2_metric_info, cwagent_metric_info]

    @staticmethod
    def set_dimensions(instance_id):
        dimension = {"Name": "InstanceId", "Value": instance_id}

        return [dimension]
