SHELL=/bin/bash

container_registry = johannes
image_name = johannes.azurecr.io/johannes-container-apps-jobs
image_tag = latest


#
# You can use tab for autocomplete on your terminal
# > make[space][tab]
#

.DEFAULT_GOAL := help
.PHONY: help
help:  ## display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

build-release:  ## build docker image (release)
	@docker build --file Dockerfile --target release --platform linux/amd64 --tag $(image_name):$(image_tag) .

build-dev:  ## build docker image (dev)
	@docker build --file Dockerfile --target dev --platform linux/amd64 --tag $(image_name):$(image_tag) .

run:  ## run docker image (dev) with mounted azure credentials
	@docker run --platform linux/amd64 -it --rm -v ~/.azure:/root/.azure $(image_name):$(image_tag)

push:  ## push docker image to container registry
	@az acr login --name $(container_registry)
	@docker push $(image_name):$(image_tag)

write-message-storage-queue:  ## writes a message to the storage queue
	@python storage_queue_write.py

write-message-servicebus-queue:  ## writes a message to the service bus queue
	@python service_bus_write.py
