# ------------------------------------------------- #
#                                                   #
#    MAKEFILE                                       #
#    --------                                       #
#                                                   #
#    Makefile commands for template:              #
#                                                   #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
#                                                   #
#        test:  run tests via nosetest.             #
#                                                   #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
#                                                   #
#        package:  packages all components into     #
#        a few Docker images ready for deployment.  #
#                                                   #
# ------------------------------------------------- #
VERSION ?= $(shell python bin/extract_version.py)

all: test package

test:
	bash bin/test.sh;

#
#  Build Docker images.
#
.PHONY: build
build: build-app-image

build-app-image:
	bash bin/build_docker_image.sh $(VERSION);

#
#  Packages all components of the
#  application for deployment.
#
package:
	@echo "Building and packaging Docker image.";
	docker save -o skill-crypto-values-$(VERSION).tar registry.dataproducts.team/skill-crypto-values:$(VERSION);
	gzip skill-crypto-values-$(VERSION).tar;

#
#  Publishes Docker images to repository.
#  Please note that 
#
publish:
	@echo "Publishing Docker image to repository.";
	docker push registry.dataproducts.team/skill-crypto-values:$(VERSION);
