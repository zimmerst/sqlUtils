PACKAGE_NAME=sqlUtils
PACKAGE_VERSION=0.1.0

.PHONY: help
help:
	@echo "Usage:"
	@echo "  make build           Build the package"
	@echo "  make clean           Clean the package"
	@echo "  make publish         Publish the package to PyPI"

.PHONY: build
build:
	python setup.py sdist bdist_wheel

.PHONY: clean
clean:
	rm -rf dist build $(PACKAGE_NAME).egg-info

.PHONY: publish
publish:
	twine upload dist/*

