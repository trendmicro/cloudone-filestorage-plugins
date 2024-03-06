.PHONY: zip

MKDIR := mkdir
ZIP := zip

zip:
	$(MKDIR) -p zip
	$(ZIP) zip/slack-notification.zip handler.py

create-function: zip
	aws lambda create-function --function-name $(FUNCTION_NAME) \
	--role $(ROLE_ARN) --runtime python3.12 \
	--timeout 30 --memory-size 512 --handler handler.lambda_handler \
	--environment Variables=\{SLACK_URL=${SLACKURL},SLACK_CHANNEL=${SLACKCHANNEL},SLACK_USERNAME=${SLACKUSERNAME}\} \
	--zip-file fileb://zip/slack-notification.zip
