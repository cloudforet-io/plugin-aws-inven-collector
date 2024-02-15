from .collector_manager import CollectorManager


class CloudServiceManager(CollectorManager):
    # _all_services = ['ACM', 'APIGateway', 'AutoScalingGroup', 'CloudFront', 'CloudTrail', 'DirectConnect', 'DocumentDB',
    #                  'DynamoDB', 'EBS', 'EC2', 'ECR', 'ECS', 'EFS', 'EIP', 'EKS', 'Elasticache', 'ELB', 'IAM',
    #                  'KinesisDataStream', 'KinesisFirehose', 'KMS', 'Lambda', 'Lightsail', 'MSK', 'RDS', 'Redshift',
    #                  'Route53', 'S3', 'SecretsManager', 'SNS', 'SQS', 'VPC']
    # _all_services = {'EC2': EC2Manager}
    # _all_services = {'ACM': acm.ACMManager, 'APIGateway': api_gateway.APIGatewayManager,
    #                  'AutoScalingGroup': auto_scaling.AutoScalingManager, 'CloudFront': cloud_front.CloudFrontManager,
    #                  'CloudTrail': cloud_trail.CloudTrailManager, 'DirectConnect': direct_connect.DirectConnectManager,
    #                  'DocumentDB': document_db.DocumentDBManager, 'DynamoDB': dynamo_db.DynamoDBManager,
    #                  'EBS': ebs.EBSManager, 'EC2': EC2Manager, 'ECR': ecr.ECRManager, 'ECS': ecs.ECSManager,
    #                  'EFS': efs.EFSManager, 'EIP': eip.EIPManager, 'EKS': eks.EKSManager,
    #                  'Elasticache': elasticache.ElastiCacheManager, 'ELB': elb.ELBManager, 'IAM': iam.IAMManager,
    #                  'KinesisDataStream': kinesis_data_stream.KinesisDataStreamManager,
    #                  'KinesisFirehose': kinesis_firehose.KinesisFirehoseManager, 'KMS': kms.KMSManager,
    #                  'Lambda': lambda_.LambdaManager, 'Lightsail': lightsail.LightsailManager, 'MSK': msk.MSKManager,
    #                  'RDS': rds.RDSManager, 'Redshift': redshift.RedshiftManager, 'Route53': route53.Route53Manager,
    #                  'S3': s3.S3Manager, 'SecretsManager': secrets_manager.SecretsManagerManager, 'SNS': sns.SNSManager,
    #                  'SQS': sqs.SQSManager, 'VPC': vpc.VPCManager}

    def collect(self, options, secret_data, schema, task_options):
        """
        this function should return metadata of cloud service types.
        """

        pass

    @classmethod
    def get_managers_by_service(cls, service):
        """
        this function works as a bridge between main.py and each targeted cloud service manager
        """
        service_type_managers = CollectorManager.get_service_type_managers(service)
        return service_type_managers

    @classmethod
    def get_service_names(cls):
        services_name = []
        for sub_cls in cls.__subclasses__():
            services_name.append(sub_cls.cloud_service_group)
        return services_name
