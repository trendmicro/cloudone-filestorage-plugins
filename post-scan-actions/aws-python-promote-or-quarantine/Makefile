.PHONY: zip

MKDIR := mkdir
ZIP := zip

zip:
	$(MKDIR) -p zip
	$(ZIP) zip/promote-or-quarantine.zip handler.py

create-function: zip
	aws lambda create-function --function-name $(FUNCTION_NAME) \
	--role $(ROLE_ARN) --runtime python3.8 \
	--timeout 30 --memory-size 512 --handler handler.lambda_handler \
	--environment Variables=\{PROMOTEBUCKET=${PROMOTE_BUCKET},QUARANTINEBUCKET=${QUARANTINE_BUCKET}\} \
	--zip-file fileb://zip/promote-or-quarantine.zip
