.PHONY: all

all: build-image

build-image:
	docker build -t cacheflow-build - <Dockerfile.base

serve:
	docker run -ti --rm -v $(shell pwd):/data -w /data/ui -p 8000:8000 cacheflow-build yarn serve --port 8000

build:
	docker run -ti --rm -v $(shell pwd):/data -w /data/ui cacheflow-build yarn build
