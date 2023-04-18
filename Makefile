PACKAGE_NAME=sqlUtils
PACKAGE_VERSION=$(shell python -c "import $(PACKAGE_NAME); print($(PACKAGE_NAME).__version__)")

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
publish: build
	twine upload dist/*

