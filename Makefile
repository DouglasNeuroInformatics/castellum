# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
VIRTUAL_ENV   ?= .venv
SPHINXOPTS    ?=
SPHINXBUILD   ?= $(VIRTUAL_ENV)/bin/sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help: venv
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile venv

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile venv
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

venv:
	@if [ ! -d "$(VIRTUAL_ENV)" ]; \
	then python3 -m venv "$(VIRTUAL_ENV)"; \
	$(VIRTUAL-ENV)/bin/pip3 install sphinx sphinx-rtd-theme; \
	fi
