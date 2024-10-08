import json
from dataclasses import dataclass

from mypy_boto3_secretsmanager import SecretsManagerClient
from src.environment import Domain
from src.utils.log import Logger

log = Logger(__name__).get_logger()


@dataclass
class WalterSecretsManagerClient:
    """
    WalterAI Secrets Manager

    Secrets:
        - PolygonAPIKey: The API key to access Polygon API for securities data
    """

    POLYGON_API_KEY_SECRET_ID = "PolygonAPIKey"

    client: SecretsManagerClient
    domain: Domain

    polygon_api_key: str = None

    def __post_init__(self) -> None:
        log.debug(
            f"Creating {self.domain.value} SecretsManager client in region '{self.client.meta.region_name}'"
        )

    def get_polygon_api_key(self) -> str:
        # lazily get polygon api key from secrets manager
        if self.polygon_api_key is None:
            self.polygon_api_key = self._get_polygon_api_key()
        return self.polygon_api_key

    def _get_polygon_api_key(self) -> str:
        return json.loads(
            self.client.get_secret_value(
                SecretId=WalterSecretsManagerClient.POLYGON_API_KEY_SECRET_ID
            )["SecretString"]
        )["POLYGON_API_KEY"]
