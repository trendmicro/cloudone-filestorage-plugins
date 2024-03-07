.PHONY: zip

MKDIR := mkdir
ZIP := zip

zip:
	$(MKDIR) -p zip
	$(ZIP) zip/scan-send-email.zip handler.py

create-function: zip
	aws lambda create-function --function-name $(FUNCTION_NAME) \
	--role $(ROLE_ARN) --runtime python3.12 \
	--timeout 30 --memory-size 512 --handler handler.lambda_handler \
	--environment Variables=\{SENDER=$(SENDER)>,RECIPIENT=$(RECIPIENT),SUBJECT=$(SUBJECT)\} \
	--zip-file fileb://zip/scan-send-email.zip
