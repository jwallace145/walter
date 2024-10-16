### Walter

[![codecov](https://codecov.io/gh/jwallace145/walter/graph/badge.svg?token=OKI43GAC28)](https://codecov.io/gh/jwallace145/walter)

[`Walter`](`https://walterai.io`) is an artificially intelligent bot that creates and sends customized newsletters to subscribers at 7:00am sharp about the markets they're following. `WalterAI` gathers market data from various APIs for each user and their interested stocks and feeds the data into [Bedrock](https://aws.amazon.com/bedrock/) to get AI insights from the LLM [Meta Llama 3](https://ai.meta.com/blog/meta-llama-3/). This allows `WalterAI` to create tailored newsletters for each subscriber including information only about the markets relevant to the user's portfolio.

`WalterAIBackend` is the backend service that maintains the database of subscribers and their interested stocks as well as the service responsible for creating and sending the customized newsletters. `WalterAIBackend` is powered completely by [AWS](https://aws.amazon.com/) and runs on [Lambda](https://aws.amazon.com/lambda/). 

### Table of Contents

* [Walter](#walter)
* [Table of Contents](#table-of-contents)
* [Architecture](#architecture)
* [Templates](#templates)
* [Scripts](#scripts)
  * [CloudFormation](#cloudformation)
  * [Lambda](#lambda)
  * [S3](#s3)
  * [SQS](#sqs)
* [Contributions](#contributions)
* [Links](#links)

### API

Export the `WALTER_API_ENDPOINT` for the intended environment and run the following curl commands to interact with Walter!

For APIs that require authentication, first authenticate the user using the `AuthUser` API and then export the returned JSON web token as `TOKEN` to be included in authenticated requests.
#### Create User

```bash
export EMAIL="walter@gmail.com" \
&& export USERNAME="walter" \
&& export PASSWORD="walter" \
&& curl -X POST "${WALTER_API_ENDPOINT}/users" \
 -H "Content-Type: application/json" \
 -d "{\"email\": \"${EMAIL}\", \"username\": \"${USERNAME}\", \"password\": \"${PASSWORD}\"}" | jq
```

#### Authenticate User

```bash
export EMAIL="walter@gmail.com" \
&& export PASSWORD="walter" \
&& curl -X POST "${WALTER_API_ENDPOINT}/auth" \
 -H "Content-Type: application/json" \
 -d "{\"email\": \"${EMAIL}\", \"password\": \"${PASSWORD}\"}" | jq
```

#### Add Stock

```bash
export EMAIL="walter@gmail.com" \
&& export STOCK="META" \
&& export QUANTITY=100.0 \
&& curl -X POST "${WALTER_API_ENDPOINT}/stocks" \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer ${TOKEN}" \
 -d "{\"email\": \"${EMAIL}\", \"stock\": \"${STOCK}\", \"quantity\": \"${QUANTITY}\"}" | jq
```

#### Get Stocks For User

```bash
export EMAIL="walter@gmail.com" \
&& curl -X POST "${WALTER_API_ENDPOINT}/users/stocks" \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer ${TOKEN}" \
 -d "{\"email\": \"${EMAIL}\"}" | jq
```

#### Send Newsletter

```bash
export EMAIL="walter@gmail.com" \
&& curl -X POST "${WALTER_API_ENDPOINT}/newsletters" \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer ${TOKEN}" \
 -d "{\"email\": \"${EMAIL}\"}" | jq
```

### Architecture

![WalterAIBackend](https://github.com/user-attachments/assets/d8441a55-84d6-41de-9199-7c70e7b034fc)

### Templates

`WalterAIBackend` uses email templates stored in S3 to create the emails to send to subscribers. Each email template is written in HTML and uses [Jinja](https://jinja.palletsprojects.com/en/3.1.x/api/) to parameterize the inputs. `WalterAIBackend` pulls the email templates from S3 and renders the template given the `templatespec.yml` and the `template.jinja` file. The `templatespec.yml` is the specification file that tells Walter the name of the parameters as well as the Bedrock prompts to use to get the parameter value. An example of a `templatespec.yml` file is given below:

```yaml
version: 0.0

TemplateSpec:
  Parameters:
    - Key: Introduction # template includes a key "Introduction"
      Prompt: | # Bedrock prompt for "Introduction" 
        Introduce yourself as Walter, a friendly AI financial newsletter bot
      MaxGenLength: 100
    - Key: DailyJoke # template includes a key "DailyJoke"
      Prompt: | # Bedrock prompt for "DailyJoke"
        Tell a joke!
      MaxGenLength: 50
```

After getting the answers to the prompts given in the `templatespec.yml` file, Walter renders the template with 
[Jinja](https://jinja.palletsprojects.com/en/3.1.x/api/) and then sends the custom newsletter to the subscriber!

### Scripts

#### CloudFormation

Use the following commands to create/update/delete the [CloudFormation](https://aws.amazon.com/cloudformation/) stacks responsible for `WalterAIBackend` infrastructure by domain.

```bash
# create development stack
aws cloudformation create-stack \
  --stack-name="WalterBackend-dev" \
  --template-body="file://infra/infra.yml" \
  --parameters="ParameterKey=AppEnvironment,ParameterValue=dev" \
  --capabilities="CAPABILITY_NAMED_IAM"

# update development stack
aws cloudformation update-stack \
  --stack-name="WalterBackend-dev" \
  --template-body="file://infra/infra.yml" \
  --parameters="ParameterKey=AppEnvironment,ParameterValue=dev" \
  --capabilities="CAPABILITY_NAMED_IAM"

# delete development stack
aws cloudformation delete-stack \
  --stack-name="WalterBackend-Dev"
```

#### Lambda

Use the following command to dump the required Python dependencies listed in the `Pipfile` to a directory to zip and upload to AWS as a [Lambda Layer](https://docs.aws.amazon.com/lambda/latest/dg/chapter-layers.html).

A new Lambda Layer is required to be created and uploaded to AWS anytime a new runtime dependency is added to Walter. To ensure the deployed Lambda utilizes the new Lambda Layer, the corresponding CloudFormation stacks need to be updated to increment the Lambda Layer utilized by `WalterAPI` and `WalterBackend`. 

```bash
mkdir python \
&& pipenv requirements > requirements.txt \
&& pip3 install -r requirements.txt --platform manylinux2014_aarch64 --target ./python --only-binary=:all: --upgrade \
&& zip -r python.zip python \
&& aws lambda publish-layer-version \
  --layer-name WalterAILambdaLayer \
  --zip-file fileb://python.zip \
  --compatible-runtimes python3.11 \
  --compatible-architectures "arm64" \
&& rm -rf python* \
&& rm -rf requirements.txt
```

Use the following command to update the Walter backend code for `WalterAPI` and `WalterBackend` from the latest artifacts in S3.

```bash
echo Updating WalterAPI Auth source code with artifact from S3 \
&& aws lambda update-function-code --function-name WalterAPI-Auth-dev --s3-bucket walter-backend-src --s3-key walter-backend.zip \
&& echo Updating WalterAPI CreateUser source code with artifact from S3 \
&& aws lambda update-function-code --function-name WalterAPI-CreateUser-dev --s3-bucket walter-backend-src --s3-key walter-backend.zip \
&& echo Updating WalterAPI AddStock source code with artifact from S3 \
&& aws lambda update-function-code --function-name WalterAPI-AddStock-dev --s3-bucket walter-backend-src --s3-key walter-backend.zip \
&& echo Updating WalterAPI GetStocksForUser source code with artifact from S3 \
&& aws lambda update-function-code --function-name WalterAPI-GetStocksForUser-dev --s3-bucket walter-backend-src --s3-key walter-backend.zip \
&& echo Updating WalterAPI SendNewsletter source code with artifact from S3 \
&& aws lambda update-function-code --function-name WalterAPI-SendNewsletter-dev --s3-bucket walter-backend-src --s3-key walter-backend.zip \
&& echo Updating WalterNewsletters source code with artifact from S3 \
&& aws lambda update-function-code --function-name WalterNewsletters-dev --s3-bucket walter-backend-src --s3-key walter-backend.zip \
&& echo Updating WalterBackend source code with artifact from S3 \
&& aws lambda update-function-code --function-name WalterBackend-dev --s3-bucket walter-backend-src --s3-key walter-backend.zip
```

Use the following command to publish new versions for the Walter Lambda functions.

```bash
echo Publishing new WalterAPI Auth Lambda version \
&& aws lambda publish-version --function-name WalterAPI-Auth-dev \
&& echo Publishing new WalterAPI CreateUser Lambda version \
&& aws lambda publish-version --function-name WalterAPI-CreateUser-dev \
&& echo Publishing new WalterAPI AddStock Lambda version \
&& aws lambda publish-version --function-name WalterAPI-AddStock-dev \
&& echo Publishing new WalterAPI GetStocksForUser Lambda version \
&& aws lambda publish-version --function-name WalterAPI-GetStocksForUser-dev \
&& echo Publishing new WalterAPI SendNewsletter Lambda version \
&& aws lambda publish-version --function-name WalterAPI-SendNewsletter-dev \
&& echo Publishing new WalterNewsletters Lambda version \
&& aws lambda publish-version --function-name WalterNewsletters-dev \
&& echo Publishing new WalterBackend Lambda version \
&& aws lambda publish-version --function-name WalterBackend-dev
```

### S3

Use the following command to update the source code of Walter backend.

```bash
echo "Updating Walter backend source code" \
&& mkdir walter-backend \
&& cp -r src walter-backend \
&& cp config.yml walter-backend \
&& cp api.py walter-backend \
&& cp newsletters.py walter-backend \
&& cp walter.py walter-backend \
&& cd walter-backend \
&& zip -r ../walter-backend.zip . \
&& cd .. \
&& echo "Publishing Walter backend source to S3" \
&& aws s3 cp walter-backend.zip s3://walter-backend-src/walter-backend.zip \
&& rm -rf walter-backend \
&& rm -rf walter-backend.zip
```
The CloudFormation stack responsible for creating the `WalterAPI` and `WalterBackend` Lambdas pulls the source  code
from S3 and the above command zips the required source code files in this repository into a package to upload to S3. 

#### SQS

Use the following command to publish a message to the Newsletters Queue to invoke Walter to generate and send an email to the given user.

```bash
aws sqs send-message \
  --queue-url="https://sqs.${AWS_REGION}.amazonaws.com/${AWS_ACCOUNT_ID}/NewsletterQueue-${DOMAIN}" \
  --message-body '{"email": "walteraifinancialadvisor@gmail.com", "dry_run": "false"}'
```

### Contributions

* [Black: The uncompromising code formatter](https://black.readthedocs.io/en/stable/)
* [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
* [Pre-Commit](https://github.com/pre-commit/pre-commit)
* [Codecov](https://about.codecov.io/)


### Links

* [Polygon IO Python Client](https://github.com/polygon-io/client-python)
* [Pre-Commit](https://github.com/pre-commit/pre-commit)
