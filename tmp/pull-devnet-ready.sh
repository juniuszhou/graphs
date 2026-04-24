#!/bin/bash
BRANCH_NAME=$(git branch --show-current)

echo "$BRANCH_NAME"

git checkout devnet-ready

git pull

git checkout $BRANCH_NAME
