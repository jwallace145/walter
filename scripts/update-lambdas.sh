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