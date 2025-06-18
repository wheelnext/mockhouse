.PHONY: clean test coverage build install lint

# ============================================================================ #
# CLEAN COMMANDS
# ============================================================================ #

clean:  ## remove all json/html
	rm -fr *.json
	rm -fr *.html
	rm -fr *.whl

# ============================================================================ #
# BUILD COMMANDS
# ============================================================================ #

build:  clean
	cd ../../../dummy-projects-flit/sandbox-project/ && \
		make build && \
		cp dist/*.whl ../../mockhouse/pep-xxx-variants/sandbox-project/ && \
		cd -
	variantlib generate-index-json -d .
	mockhouse generate-project-index -d .