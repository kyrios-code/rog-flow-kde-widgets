PYTHON ?= python3
WIDGETS := system control gaming
.PHONY: all build test validate clean install uninstall $(addprefix build-,$(WIDGETS)) $(addprefix install-,$(WIDGETS)) $(addprefix uninstall-,$(WIDGETS))
all: build
build:
	$(PYTHON) tools/build.py all
$(addprefix build-,$(WIDGETS)):
	$(PYTHON) tools/build.py $(@:build-%=%)
validate:
	$(PYTHON) tools/validate.py
test: validate
	$(PYTHON) -m unittest discover -s tests -v
install: build
	bash tools/install.sh all
$(addprefix install-,$(WIDGETS)): install-%: build-%
	bash tools/install.sh $*
uninstall:
	bash tools/uninstall.sh all
$(addprefix uninstall-,$(WIDGETS)):
	bash tools/uninstall.sh $(@:uninstall-%=%)
clean:
	$(PYTHON) -c 'import shutil; shutil.rmtree("dist", ignore_errors=True)'
