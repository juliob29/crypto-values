#!/bin/bash
#
#  Builds Docker image of the
#  `skill-crypto-values` program.
#
VERSION=$1
docker build --tag registry.dataproducts.team/skill-crypto-values:$VERSION \
             --tag registry.dataproducts.team/skill-crypto-values:latest \
             .