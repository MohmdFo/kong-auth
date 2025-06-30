# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Custom targets for easier documentation management
html:
	@echo "Building HTML documentation..."
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "HTML documentation built in $(BUILDDIR)/html/"

clean:
	@echo "Cleaning documentation build..."
	@rm -rf $(BUILDDIR)/*
	@echo "Clean complete!"

serve:
	@echo "Starting documentation server..."
	@cd $(BUILDDIR)/html && python -m http.server 8080
	@echo "Documentation available at http://localhost:8080"

install:
	@echo "Installing Sphinx dependencies..."
	@pip install -r requirements.txt
	@echo "Dependencies installed!"

build-all: clean html
	@echo "Documentation built successfully!"

# Development helpers
dev:
	@echo "Starting development server with auto-reload..."
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "Documentation built. Starting server..."
	@cd $(BUILDDIR)/html && python -m http.server 8080

check:
	@echo "Checking documentation for errors..."
	@$(SPHINXBUILD) -M linkcheck "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "Link check complete!"

spelling:
	@echo "Checking spelling..."
	@$(SPHINXBUILD) -M spelling "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "Spelling check complete!" 