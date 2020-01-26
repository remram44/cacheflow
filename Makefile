.PHONY: all build-image serve serve-local build build-local

all: build-image

build-image:
	docker build -t cacheflow-build - <Dockerfile.base

serve:
	docker run -ti --rm -v $(shell pwd):/data -w /data/ui -p 8000:8000 cacheflow-build yarn serve --port 8000

serve-local:
	cd ui && yarn serve --port 8000

build:
	docker run -ti --rm -v $(shell pwd):/data -w /data/ui cacheflow-build yarn build
	rm -rf cacheflow/web/ui
	mkdir cacheflow/web/ui
	mkdir cacheflow/web/ui/static
	cp ui/dist/index.html cacheflow/web/ui/
	cp -r ui/dist/* cacheflow/web/ui/static/

build-local:
	cd ui && yarn build
	rm -rf cacheflow/web/ui
	mkdir cacheflow/web/ui
	mkdir cacheflow/web/ui/static
	cp ui/dist/index.html cacheflow/web/ui/
	cp -r ui/dist/* cacheflow/web/ui/static/
