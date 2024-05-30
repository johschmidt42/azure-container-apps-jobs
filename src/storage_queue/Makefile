SHELL=/bin/bash

# Variables
package_name = storage_queue
container_registry = johannes
image_name = johannes.azurecr.io/johannes-container-apps-jobs
image_tag = storage-queue
subscription = a6feefeb-7f6b-425b-8311-b42ebeaee0d1
subscription_name = B-ID_Sandbox
resource_group = johannes-sandbox
environment = johannes-container-apps-environment
storage_account_name = johannesstorageacc
queue_name = mysecondqueue
uami = /subscriptions/a6feefeb-7f6b-425b-8311-b42ebeaee0d1/resourceGroups/johannes-sandbox/providers/Microsoft.ManagedIdentity/userAssignedIdentities/container-jobs
uami_client_id = 60923ba8-c748-4a0c-9ab2-313d3b3ac414

#
# You can use tab for autocomplete on your terminal
# > make[space][tab]
#

.DEFAULT_GOAL := help
.PHONY: help
help:  ## display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

build-release:  ## build docker image (release)
	@cd ../; docker build --file ./$(package_name)/Dockerfile --target release --platform linux/amd64 --tag $(image_name):$(image_tag) .

build-dev:  ## build docker image (dev)
	@cd ../; docker build --file ./$(package_name)/Dockerfile --target dev --platform linux/amd64 --tag $(image_name):$(image_tag) .

run:  ## run docker image (dev) with mounted azure credentials
	@docker run --platform linux/amd64 -it --rm -v ~/.azure:/root/.azure $(image_name):$(image_tag)

run-bash:  ## run docker image (dev) with bash
	@docker run --platform linux/amd64 -it --rm -v ~/.azure:/root/.azure $(image_name):$(image_tag) /bin/bash

push:  ## push docker image to container registry
	@az acr login --name $(container_registry)
	@docker push $(image_name):$(image_tag)

write-message-queue:  ## writes a message to the queue
	@PYTHONPATH="../shared/src" python src/$(package_name)/storage_queue_write.py

process-message-queue: ## process a message from the queue
	@PYTHONPATH="../shared/src" python src/$(package_name)/storage_queue_process.py

##@ Deploy

set-subscription:
	@az account set --subscription $(subscription)

deploy-container-job:
	@QUEUE_CONNECTION_STRING=$$(az storage account show-connection-string -g $(resource_group) --name $(storage_account_name) --query connectionString --output tsv) && \
	az containerapp job create \
    --name "$(image_tag)" \
    --subscription "$(subscription)" \
    --resource-group "$(resource_group)" \
    --environment "$(environment)" \
    --trigger-type "Event" \
    --replica-timeout "1800" \
    --min-executions "0" \
    --max-executions "1" \
    --polling-interval "60" \
    --scale-rule-name "$(image_tag)" \
    --scale-rule-type "azure-queue" \
    --scale-rule-metadata "accountName=$(storage_account_name)" "queueName=$(queue_name)" "queueLength=1" \
    --scale-rule-auth "connection=connection-string-secret" \
    --image "$(image_name):$(image_tag)" \
    --cpu "0.5" \
    --memory "1Gi" \
    --secrets "connection-string-secret=$$QUEUE_CONNECTION_STRING" \
    --env-vars "AZURE_STORAGE_QUEUE_NAME=$(queue_name)" "AZURE_STORAGE_CONNECTION_STRING=secretref:connection-string-secret" "AZURE_CLIENT_ID=$(uami_client_id)" \
    --mi-user-assigned "$(uami)" \
    --registry-identity "$(uami)" \
    --registry-server "$(container_registry).azurecr.io" \

delete-container-job:
	@az containerapp job delete --name "$(image_tag)" --subscription "$(subscription)" --resource-group "$(resource_group)" --yes
