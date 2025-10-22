from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.ecr import Repository, Image


class RepositoryManager(ResourceManager):
    cloud_service_group = "ECR"
    cloud_service_type = "Repository"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "ECR"
        self.cloud_service_type = "Repository"
        self.metadata_path = "metadata/ecr/repository.yaml"

    def create_cloud_service_type(self):
        result = []
        repository_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonECR",
            tags={
                "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-ecr.svg"
            },
            labels=["Container"],
        )
        result.append(repository_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_repositories(options, region)

    def _collect_repositories(self, options, region):
        region_name = region

        for result in self.connector.describe_repositories():
            for repository in result.get('repositories', []):
                try:
                    repository.update({
                        'images': list(self._describe_images(repository)),
                        'cloudtrail': self.set_cloudtrail(self.cloud_service_group,
                                                          repository['repositoryName'], region_name)
                    })

                    repository_vo = Repository(repository, strict=False)


                    repository_name = repository_vo.repository_name
                    link = f"https://{region}.console.aws.amazon.com/ecr/repositories?region={region}#/repository/{repository_name}"
                    resource_id = repository_vo.repository_arn
                    reference = self.get_reference(resource_id, link)

                    cloud_service = make_cloud_service(
                        name=repository_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=repository_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=self.connector.list_tags_for_resource(resource_id),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_ecr_repositories] [{repository.get("RepositoryName")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

    def _describe_images(self, repo):
        for result in self.connector.describe_images():
            for image in result.get('imageDetails', []):
                image.update({
                    # 'image_size_in_megabytes': f'{float(raw["imageSizeInBytes"] / 1000000):.2f}',
                    'image_tags_display': self._generate_image_tags_display(image.get('imageTags', [])),
                    'image_uri': self._generate_image_uri(repo.get("repositoryUri", ''), image.get("imageTags", []))
                })

                res = Image(image, strict=False)
                yield res

    @staticmethod
    def _generate_image_uri(repo_uri, image_tags):
        if image_tags:
            return f'{repo_uri}:{image_tags[0]}'
        else:
            return repo_uri

    @staticmethod
    def _generate_image_tags_display(image_tags):
        if image_tags:
            return image_tags
        else:
            return ['<untagged>']
