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