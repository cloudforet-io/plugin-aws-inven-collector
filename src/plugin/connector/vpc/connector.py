from plugin.connector.collector_connector import CollectorConnector


class VPCConnector(CollectorConnector):
    service_name = 'vpc'
    cloud_service_group = 'VPC'
    include_vpc_default = False

    def __init__(self):
        super().__init__()

