MAX_WORKERS = 20
SUPPORTED_FEATURES = ["garbage_collection"]
SUPPORTED_RESOURCE_TYPE = [
    "inventory.CloudService",
    "inventory.Region",
    "inventory.CloudServiceType",
]
SUPPORTED_SCHEDULES = ["hours"]
NUMBER_OF_CONCURRENT = 20
DEFAULT_REGION = "us-east-1"
FILTER_FORMAT = []
BOTO3_HTTPS_VERIFIED = None
DEFAULT_VULNERABLE_PORTS = "22,3306"

ASSET_URL = "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/aws"

PAGINATOR_MAX_ITEMS = 10000
PAGINATOR_PAGE_SIZE = 50

DEFAULT_API_RETRIES = 10

METRIC_SERVICES = [
    "CertificateManager",  # "ACM",
    "CloudFront",
    "CloudTrail",
    "DocumentDB",
    "EC2",
    "ECR",
    "EFS",
    "EKS",
    "ELB",
    "IAM",
    "KMS",
    "Lambda",
    "Route53",
    "S3",
    "TrustedAdvisor",
    "PersonalHealthDashboard",
]

REGION_INFO = {
    "us-east-1": {
        "name": "US East (N. Virginia)",
        "tags": {
            "latitude": "39.028760",
            "longitude": "-77.458263",
            "continent": "north_america",
        },
    },
    "us-east-2": {
        "name": "US East (Ohio)",
        "tags": {
            "latitude": "40.103564",
            "longitude": "-83.200092",
            "continent": "north_america",
        },
    },
    "us-west-1": {
        "name": "US West (N. California)",
        "tags": {
            "latitude": "37.242183",
            "longitude": "-121.783380",
            "continent": "north_america",
        },
    },
    "us-west-2": {
        "name": "US West (Oregon)",
        "tags": {
            "latitude": "45.841046",
            "longitude": "-119.658093",
            "continent": "north_america",
        },
    },
    "af-south-1": {
        "name": "Africa (Cape Town)",
        "tags": {
            "latitude": "-33.932268",
            "longitude": "18.424434",
            "continent": "africa",
        },
    },
    "ap-east-1": {
        "name": "Asia Pacific (Hong Kong)",
        "tags": {
            "latitude": "22.365560",
            "longitude": "114.119420",
            "continent": "asia_pacific",
        },
    },
    "ap-south-1": {
        "name": "Asia Pacific (Mumbai)",
        "tags": {
            "latitude": "19.147428",
            "longitude": "73.013805",
            "continent": "asia_pacific",
        },
    },
    "ap-northeast-3": {
        "name": "Asia Pacific (Osaka-Local)",
        "tags": {
            "latitude": "34.675638",
            "longitude": "135.495706",
            "continent": "asia_pacific",
        },
    },
    "ap-northeast-2": {
        "name": "Asia Pacific (Seoul)",
        "tags": {
            "latitude": "37.528547",
            "longitude": "126.871867",
            "continent": "asia_pacific",
        },
    },
    "ap-southeast-1": {
        "name": "Asia Pacific (Singapore)",
        "tags": {
            "latitude": "1.321259",
            "longitude": "103.695942",
            "continent": "asia_pacific",
        },
    },
    "ap-southeast-2": {
        "name": "Asia Pacific (Sydney)",
        "tags": {
            "latitude": "-33.921423",
            "longitude": "151.188076",
            "continent": "asia_pacific",
        },
    },
    "ap-northeast-1": {
        "name": "Asia Pacific (Tokyo)",
        "tags": {
            "latitude": "35.648411",
            "longitude": "139.792566",
            "continent": "asia_pacific",
        },
    },
    "ca-central-1": {
        "name": "Canada (Central)",
        "tags": {
            "latitude": "43.650803",
            "longitude": "-79.361824",
            "continent": "north_america",
        },
    },
    "cn-north-1": {
        "name": "China (Beijing)",
        "tags": {
            "latitude": "39.919635",
            "longitude": "116.307237",
            "continent": "asia_pacific",
        },
    },
    "cn-northwest-1": {
        "name": "China (Ningxia)",
        "tags": {
            "latitude": "37.354511",
            "longitude": "106.106147",
            "continent": "asia_pacific",
        },
    },
    "eu-central-1": {
        "name": "Europe (Frankfurt)",
        "tags": {
            "latitude": "50.098645",
            "longitude": "8.632262",
            "continent": "europe",
        },
    },
    "eu-west-1": {
        "name": "Europe (Ireland)",
        "tags": {
            "latitude": "53.330893",
            "longitude": "-6.362217",
            "continent": "europe",
        },
    },
    "eu-west-2": {
        "name": "Europe (London)",
        "tags": {
            "latitude": "51.519749",
            "longitude": "-0.087804",
            "continent": "europe",
        },
    },
    "eu-south-1": {
        "name": "Europe (Milan)",
        "tags": {
            "latitude": "45.448648",
            "longitude": "9.147316",
            "continent": "europe",
        },
    },
    "eu-west-3": {
        "name": "Europe (Paris)",
        "tags": {
            "latitude": "48.905302",
            "longitude": "2.369778",
            "continent": "europe",
        },
    },
    "eu-north-1": {
        "name": "Europe (Stockholm)",
        "tags": {
            "latitude": "59.263542",
            "longitude": "18.104861",
            "continent": "europe",
        },
    },
    "me-south-1": {
        "name": "Middle East (Bahrain)",
        "tags": {
            "latitude": "26.240945",
            "longitude": "50.586321",
            "continent": "middle_east",
        },
    },
    "sa-east-1": {
        "name": "South America (São Paulo)",
        "tags": {
            "latitude": "-23.493549",
            "longitude": "-46.809319",
            "continent": "south_america",
        },
    },
    "us-gov-east-1": {
        "name": "AWS GovCloud (US-East)",
        "tags": {"continent": "south_america"},
    },
    "us-gov-west-1": {
        "name": "AWS GovCloud (US)",
        "tags": {"continent": "south_america"},
    },
    "ap-south-2": {
        "name": "Asia Pacific (Mumbai)",
        "tags": {
            "latitude": "17.3850",
            "longitude": "78.4867",
            "continent": "asia_pacific",
        },
    },
    "ap-southeast-4": {
        "name": "Asia Pacific (Melbourne)",
        "tags": {
            "latitude": "-37.8136",
            "longitude": "144.9631",
            "continent": "asia_pacific",
        },
    },
    "ap-southeast-3": {
        "name": "Asia Pacific (Jakarta)",
        "tags": {
            "latitude": "-6.2088",
            "longitude": "106.8272",
            "continent": "asia_pacific",
        },
    },
    "ca-west-1": {
        "name": "Canada West (Calgary)",
        "tags": {
            "latitude": "51.0447",
            "longitude": "114.0719",
            "continent": "north_america",
        },
    },
    "eu-central-2": {
        "name": "Europe (Zurich)",
        "tags": {
            "latitude": "47.3769",
            "longitude": "8.5417",
            "continent": "europe",
        },
    },
    "eu-south-2": {
        "name": "Europe (Spain)",
        "tags": {
            "latitude": "40.4168",
            "longitude": "3.7038",
            "continent": "europe",
        },
    },
    "il-central-1": {
        "name": "Israel (Tel Aviv)",
        "tags": {
            "latitude": "32.0853",
            "longitude": "34.7818",
            "continent": "middle_east",
        },
    },
    "me-central-1": {
        "name": "Middle East (UAE)",
        "tags": {
            "latitude": "25.2769",
            "longitude": "55.2708",
            "continent": "middle_east",
        },
    },
    "ap-southeast-5": {
        "name": "Asia Pacific (Malaysia)",
        "tags": {
            "latitude": "3.1390",
            "longitude": "101.6869",
            "continent": "asia_pacific",
        },
    },
    "mx-central-1": {
        "name": "Mexico (Central)",
        "tags": {
            "latitude": "20.5888",
            "longitude": "-100.3899",
            "continent": "north_america",
        },
    },
    "ap-southeast-6": {
        "name": "Asia Pacific (Thailand)",
        "tags": {
            "latitude": "13.7563",
            "longitude": "100.5018",
            "continent": "asia_pacific",
        },
    },
    "global": {"name": "Global"},
}

INSTANCE_FILTERS = [
    "InstanceId",
    "instance_name",
    "State",
    "SubnetId",
    "VpcId",
    "PrivateIpAddress",
    "PrivateDnsName",
    "PublicIpAddress",
    "PublicDnsName",
    "Architecture",
    "SecurityGroups",
    "Tags",
]

# 글로벌 서비스 목록 (정확한 기준으로 관리)
GLOBAL_SERVICES = {
    "IAM",
    "Route53",
    "CloudFront",
    "S3",
    "ACM",
    "CloudTrail",
    "TrustedAdvisor",
    "PersonalHealthDashboard",
}

SERVICE_NAME_MAP = {
    "ACM": "acm",
    "EC2": "ec2",
    "AutoScaling": "autoscaling",
    "DynamoDB": "dynamodb",
    "DocumentDB": "docdb",
    "DirectConnect": "directconnect",
    "CloudTrail": "cloudtrail",
    "CloudFront": "cloudfront",
    "APIGateway": "apigateway",
    "CertificateManager": "acm",
    "ECR": "ecr",
    "EFS": "efs",
    "EKS": "eks",
    "ELB": "elb",
    "IAM": "iam",
    "KMS": "kms",
    "Lambda": "lambda_model",
    "Route53": "route53",
    "S3": "s3",
    "MSK": "kafka",
    "RDS": "rds",
    "Redshift": "redshift",
    "ElastiCache": "elasticache",
    "SNS": "sns",
    "SQS": "sqs",
    "SecretsManager": "secretsmanager",
    "KinesisDataStream": "kinesis",
    "KinesisFirehose": "firehose",
    "LightSail": "lightsail",
    "VPC": "vpc",
    "EIP": "eip",
    "TrustedAdvisor": "support",
    "PersonalHealthDashboard": "health",
}

CLOUDWATCH_CONFIG = {
    "ACM": {
        "namespace": "AWS/CertificateManager",
        "dimension_name": "CertificateArn",
    },
    "APIGateway": {
        "namespace": "AWS/ApiGateway",
        "dimension_name": "ApiName",
    },
    "CloudFront": {
        "namespace": "AWS/CloudFront",
        "dimension_name": "DistributionId",
    },
    "CloudTrail": {
        "namespace": "CloudTrailMetrics",
        "dimension_name": None,
    },
    "CloudWatch": {
        "namespace": "CloudWatchMetrics",
        "dimension_name": None,
    },
    "DirectConnect": {
        "namespace": "AWS/DX",
        "dimension_name": "ConnectionId",
    },
    "DocumentDB": {
        "namespace": "AWS/DocDB",
        "dimension_name": "DBClusterIdentifier",
    },
    "DynamoDB": {
        "namespace": "AWS/DynamoDB",
        "dimension_name": "TableName",
    },
    "EC2": {
        "namespace": "AWS/EC2",
        "dimension_name": "InstanceId",
    },
    "ECR": {
        "namespace": "AWS/ECR",
        "dimension_name": "RepositoryName",
    },
    "ECS": {
        "namespace": "AWS/ECS",
        "dimension_name": "ClusterName",
    },
    "EFS": {
        "namespace": "AWS/EFS",
        "dimension_name": "FileSystemId",
    },
    "EIP": {
        "namespace": "AWS/EC2",
        "dimension_name": "AllocationId",
    },
    "EKS": {
        "namespace": "AWS/EKS",
        "dimension_name": "ClusterName",
    },
    "ELB": {
        "namespace": "AWS/ELB",
        "dimension_name": "LoadBalancerName",
    },
    "ElastiCache": {
        "namespace": "AWS/ElastiCache",
        "dimension_name": "CacheClusterId",
    },
    "IAM": {
        "namespace": "AWS/IAM",
        "dimension_name": None,
    },
    "KMS": {
        "namespace": "AWS/KMS",
        "dimension_name": "KeyId",
    },
    "Kinesis": {
        "namespace": "AWS/Kinesis",
        "dimension_name": "StreamName",
    },
    "Lambda": {
        "namespace": "AWS/Lambda",
        "dimension_name": "FunctionName",
    },
    "Lightsail": {
        "namespace": "AWS/LightSail",
        "dimension_name": "InstanceName",
    },
    "MSK": {
        "namespace": "AWS/Kafka",
        "dimension_name": "Cluster Name",
    },
    "RDS": {
        "namespace": "AWS/RDS",
        "dimension_name": "DBInstanceIdentifier",
    },
    "Redshift": {
        "namespace": "AWS/Redshift",
        "dimension_name": "ClusterIdentifier",
    },
    "Route53": {
        "namespace": "AWS/Route53",
        "dimension_name": "HostedZoneId",
    },
    "S3": {
        "namespace": "AWS/S3",
        "dimension_name": "BucketName",
    },
    "SNS": {
        "namespace": "AWS/SNS",
        "dimension_name": "TopicName",
    },
    "SQS": {
        "namespace": "AWS/SQS",
        "dimension_name": "QueueName",
    },
    "SecretsManager": {
        "namespace": "AWS/SecretsManager",
        "dimension_name": "SecretName",
    },
    "VPC": {
        "namespace": "AWS/VPC",
        "dimension_name": "VpcId",
    },
    "CustomerGateway": {
        "namespace": "AWS/VPC",
        "dimension_name": "CustomerGatewayId",
    },
    "EgressOnlyInternetGateway": {
        "namespace": "AWS/VPC",
        "dimension_name": "EgressOnlyInternetGatewayId",
    },
    "Endpoint": {
        "namespace": "AWS/VPC",
        "dimension_name": "VpcEndpointId",
    },
    "InternetGateway": {
        "namespace": "AWS/VPC",
        "dimension_name": "InternetGatewayId",
    },
    "NatGateway": {
        "namespace": "AWS/VPC",
        "dimension_name": "NatGatewayId",
    },
    "NetworkAcl": {
        "namespace": "AWS/VPC",
        "dimension_name": "NetworkAclId",
    },
    "PeeringConnection": {
        "namespace": "AWS/VPC",
        "dimension_name": "VpcPeeringConnectionId",
    },
    "RouteTable": {
        "namespace": "AWS/VPC",
        "dimension_name": "RouteTableId",
    },
    "Subnet": {
        "namespace": "AWS/VPC",
        "dimension_name": "SubnetId",
    },
    "TransitGateway": {
        "namespace": "AWS/VPC",
        "dimension_name": "TransitGatewayId",
    },
    "VpnConnection": {
        "namespace": "AWS/VPC",
        "dimension_name": "VpnConnectionId",
    },
    "VpnGateway": {
        "namespace": "AWS/VPC",
        "dimension_name": "VpnGatewayId",
    },
}

CLOUDTRAIL_CONFIG = {
    "ACM": {
        "resource_type": "AWS::CertificateManager::Certificate",
        "lookup_attribute": "ResourceName",
    },
    "APIGateway": {
        "resource_type": "AWS::ApiGateway::RestApi",
        "lookup_attribute": "ResourceName",
    },
    "CloudFront": {
        "resource_type": "AWS::CloudFront::Distribution",
        "lookup_attribute": "ResourceName",
    },
    "CloudTrail": {
        "resource_type": "AWS::CloudTrail::Trail",
        "lookup_attribute": "ResourceName",
    },
    "CloudWatch": {
        "resource_type": "AWS::CloudWatch::Alarm",
        "lookup_attribute": "ResourceName",
    },
    "DirectConnect": {
        "resource_type": "AWS::DirectConnect::Connection",
        "lookup_attribute": "ResourceName",
    },
    "DocumentDB": {
        "resource_type": "AWS::DocDB::DBCluster",
        "lookup_attribute": "ResourceName",
    },
    "DynamoDB": {
        "resource_type": "AWS::DynamoDB::Table",
        "lookup_attribute": "ResourceName",
    },
    "EC2": {
        "resource_type": "AWS::EC2::Instance",
        "lookup_attribute": "ResourceName",
    },
    "ECR": {
        "resource_type": "AWS::ECR::Repository",
        "lookup_attribute": "ResourceName",
    },
    "ECS": {
        "resource_type": "AWS::ECS::Cluster",
        "lookup_attribute": "ResourceName",
    },
    "EFS": {
        "resource_type": "AWS::EFS::FileSystem",
        "lookup_attribute": "ResourceName",
    },
    "EIP": {
        "resource_type": "AWS::EC2::EIP",
        "lookup_attribute": "ResourceName",
    },
    "EKS": {
        "resource_type": "AWS::EKS::Cluster",
        "lookup_attribute": "ResourceName",
    },
    "ELB": {
        "resource_type": "AWS::ElasticLoadBalancing::LoadBalancer",
        "lookup_attribute": "ResourceName",
    },
    "ElastiCache": {
        "resource_type": "AWS::ElastiCache::CacheCluster",
        "lookup_attribute": "ResourceName",
    },
    "IAM": {
        "resource_type": "AWS::IAM::User",
        "lookup_attribute": "ResourceName",
    },
    "KMS": {
        "resource_type": "AWS::KMS::Key",
        "lookup_attribute": "ResourceName",
    },
    "Kinesis": {
        "resource_type": "AWS::Kinesis::Stream",
        "lookup_attribute": "ResourceName",
    },
    "Lambda": {
        "resource_type": "AWS::Lambda::Function",
        "lookup_attribute": "ResourceName",
    },
    "Lightsail": {
        "resource_type": "AWS::Lightsail::Instance",
        "lookup_attribute": "ResourceName",
    },
    "MSK": {
        "resource_type": "AWS::MSK::Cluster",
        "lookup_attribute": "ResourceName",
    },
    "RDS": {
        "resource_type": "AWS::RDS::DBInstance",
        "lookup_attribute": "ResourceName",
    },
    "Redshift": {
        "resource_type": "AWS::Redshift::Cluster",
        "lookup_attribute": "ResourceName",
    },
    "Route53": {
        "resource_type": "AWS::Route53::HostedZone",
        "lookup_attribute": "ResourceName",
    },
    "S3": {
        "resource_type": "AWS::S3::Bucket",
        "lookup_attribute": "ResourceName",
    },
    "SNS": {
        "resource_type": "AWS::SNS::Topic",
        "lookup_attribute": "ResourceName",
    },
    "SQS": {
        "resource_type": "AWS::SQS::Queue",
        "lookup_attribute": "ResourceName",
    },
    "SecretsManager": {
        "resource_type": "AWS::SecretsManager::Secret",
        "lookup_attribute": "ResourceName",
    },
    "VPC": {
        "resource_type": "AWS::EC2::VPC",
        "lookup_attribute": "ResourceName",
    },
    "CustomerGateway": {
        "resource_type": "AWS::EC2::CustomerGateway",
        "lookup_attribute": "ResourceName",
    },
    "EgressOnlyInternetGateway": {
        "resource_type": "AWS::EC2::EgressOnlyInternetGateway",
        "lookup_attribute": "ResourceName",
    },
    "Endpoint": {
        "resource_type": "AWS::EC2::VPCEndpoint",
        "lookup_attribute": "ResourceName",
    },
    "InternetGateway": {
        "resource_type": "AWS::EC2::InternetGateway",
        "lookup_attribute": "ResourceName",
    },
    "NatGateway": {
        "resource_type": "AWS::EC2::NatGateway",
        "lookup_attribute": "ResourceName",
    },
    "NetworkAcl": {
        "resource_type": "AWS::EC2::NetworkAcl",
        "lookup_attribute": "ResourceName",
    },
    "PeeringConnection": {
        "resource_type": "AWS::EC2::VPCPeeringConnection",
        "lookup_attribute": "ResourceName",
    },
    "RouteTable": {
        "resource_type": "AWS::EC2::RouteTable",
        "lookup_attribute": "ResourceName",
    },
    "Subnet": {
        "resource_type": "AWS::EC2::Subnet",
        "lookup_attribute": "ResourceName",
    },
    "TransitGateway": {
        "resource_type": "AWS::EC2::TransitGateway",
        "lookup_attribute": "ResourceName",
    },
    "VpnConnection": {
        "resource_type": "AWS::EC2::VPNConnection",
        "lookup_attribute": "ResourceName",
    },
    "VpnGateway": {
        "resource_type": "AWS::EC2::VPNGateway",
        "lookup_attribute": "ResourceName",
    },
}
