import os

import boto3

from src.ai.client import WalterBedrockClient
from src.ai.context.generator import ContextGenerator
from src.ai.meta.models import MetaLlama38B
from src.aws.cloudwatch.client import WalterCloudWatchClient
from src.aws.dynamodb.client import WalterDDBClient
from src.aws.s3.client import WalterS3Client
from src.aws.secretsmanager.client import WalterSecretsManagerClient
from src.aws.ses.client import WalterSESClient
from src.aws.sqs.client import WalterSQSClient
from src.database.client import WalterDB
from src.environment import get_domain
from src.jinja.client import TemplateEngine
from src.newsletters.client import NewslettersBucket
from src.stocks.client import WalterStocksAPI
from src.stocks.polygon.client import PolygonClient
from src.templates.client import TemplatesBucket
from src.utils.log import Logger

log = Logger(__name__).get_logger()

log.debug("Initializing clients...")

#########################
# ENVIRONMENT VARIABLES #
#########################

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
"""(str): The AWS region the WalterAIBackend service is deployed."""

DOMAIN = get_domain(os.getenv("DOMAIN", "DEVELOPMENT"))
"""(str): The domain of the WalterAIBackend service environment."""

########################
# WALTER BOTO3 CLIENTS #
########################

bedrock = WalterBedrockClient(
    bedrock=boto3.client("bedrock", region_name=AWS_REGION),
    bedrock_runtime=boto3.client("bedrock-runtime", region_name=AWS_REGION),
)
cloudwatch = WalterCloudWatchClient(
    client=boto3.client("cloudwatch", region_name=AWS_REGION), domain=DOMAIN
)
ses = WalterSESClient(client=boto3.client("ses", region_name=AWS_REGION), domain=DOMAIN)
sqs = WalterSQSClient(client=boto3.client("sqs", region_name=AWS_REGION), domain=DOMAIN)

##############
# S3 BUCKETS #
##############

s3 = WalterS3Client(client=boto3.client("s3", region_name=AWS_REGION), domain=DOMAIN)
templates_bucket = TemplatesBucket(s3, DOMAIN)
newsletters_bucket = NewslettersBucket(s3, DOMAIN)

##########################
# WALTER DATABASE CLIENT #
##########################

walter_db = WalterDB(
    ddb=WalterDDBClient(client=boto3.client("dynamodb", region_name=AWS_REGION)),
    domain=DOMAIN,
)

#####################
# WALTER STOCKS API #
#####################

walter_stocks_api = WalterStocksAPI(
    client=PolygonClient(
        api_key=WalterSecretsManagerClient(
            client=boto3.client("secretsmanager", region_name=AWS_REGION), domain=DOMAIN
        ).get_polygon_api_key()
    )
)


#########################
# JINJA TEMPLATE ENGINE #
#########################

template_engine = TemplateEngine(
    templates_bucket=templates_bucket,
    newsletters_bucket=newsletters_bucket,
    domain=DOMAIN,
)

##############
# LLM MODELS #
##############

meta_llama3 = MetaLlama38B(model=bedrock)

#####################
# CONTEXT GENERATOR #
#####################

context_generator = ContextGenerator()
