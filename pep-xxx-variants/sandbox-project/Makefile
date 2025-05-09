.PHONY: clean test coverage build install lint

# ============================================================================ #
# CLEAN COMMANDS
# ============================================================================ #

clean:  ## remove all json/html
	rm -fr *.json
	rm -fr *.html

clean-all: clean
	rm -fr *.whl

# ============================================================================ #
# BUILD COMMANDS
# ============================================================================ #

build:
	variantlib generate-index-json -d .
	mockhouse generate-project-index -d .
