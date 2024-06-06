SHELL=/bin/bash

# Variables
subscription = a6feefeb-7f6b-425b-8311-b42ebeaee0d1
subscription_name = B-ID_Sandbox
resource_group = johannes-sandbox
workbook_id = 445acf7a-8ddc-44d5-a07b-67bca9e9cc9f
workbook_name = my-workbook
workbook_file = workbook.json

#
# You can use tab for autocomplete on your terminal
# > make[space][tab]
#

.DEFAULT_GOAL := help
.PHONY: help
help:  ## display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

deploy-workbook:  ## deploy azure monitor workbook to monitor jobs (convert workbook.json to string first)
	SERIALIZED_CONTENT=$$(cat $(workbook_file) | jq -c | jq -R) && \
	az monitor app-insights workbook create --name $(workbook_id) --resource-group $(resource_group) --display-name $(workbook_name) --serialized-data "$$SERIALIZED_CONTENT" --location "westeurope" --kind "shared" --source-id "azure monitor"
