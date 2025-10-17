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

BASE_PACKAGE_DIRS := \
	"plugins/provider_fictional_hw:provider-fictional-hw" \
	"plugins/provider_fictional_tech:provider-fictional-tech"

build_base_packages:
	@for pair in $(BASE_PACKAGE_DIRS); do \
		INPUT_DIR=$$(echo $$pair | cut -d: -f1); \
		OUTPUT_DIR=$$(echo $$pair | cut -d: -f2); \
		echo "Processing $$INPUT_DIR to $$OUTPUT_DIR"; \
		rm -rf "$$OUTPUT_DIR"; \
		mkdir -p "$$OUTPUT_DIR"; \
		cd ../../$$INPUT_DIR/ && \
			make build > /dev/null 2>&1 && \
			cp dist/*.whl ../../mockhouse/pep-xxx-variants/$$OUTPUT_DIR/ && \
			cd - > /dev/null 2>&1; \
		mockhouse generate-project-index -d "$$OUTPUT_DIR" > /dev/null 2>&1; \
	done

VARIANT_PACKAGE_DIRS := \
	example-projects/exampleA-flit:dummy-project-flit \
	example-projects/exampleB-flit:sandbox-project-flit \
	example-projects/example-hatch:dummy-project-hatch

build_variant_packages:
	@for pair in $(VARIANT_PACKAGE_DIRS); do \
		INPUT_DIR=$$(echo $$pair | cut -d: -f1); \
		OUTPUT_DIR=$$(echo $$pair | cut -d: -f2); \
		echo "Processing $$INPUT_DIR to $$OUTPUT_DIR"; \
		rm -rf "$$OUTPUT_DIR"; \
		mkdir -p "$$OUTPUT_DIR"; \
		cd ../../$$INPUT_DIR/ && \
			make build > /dev/null 2>&1 && \
			cp dist/*.whl ../../mockhouse/pep-xxx-variants/$$OUTPUT_DIR/ && \
			cd - > /dev/null 2>&1; \
		variantlib generate-index-json -d "$$OUTPUT_DIR" > /dev/null 2>&1; \
		mockhouse generate-project-index -d "$$OUTPUT_DIR" > /dev/null 2>&1; \
	done


build: clean build_base_packages build_variant_packages ## builds all base and variant packages
	@mockhouse generate-main-index -d .
	@printf "\n[SUCCESS] All packages built successfully - All index pages re-generated.\n"