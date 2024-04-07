#!/usr/bin/env bash
set -eu -o pipefail

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ] ; do SOURCE="$(readlink "$SOURCE")"; done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
PROJECT_DIR="$(dirname $DIR)"

cd $PROJECT_DIR

# trap failed tests
trap 'echo "Tests failed!"' ERR

for test in $(find tests -name test.sh); do
    echo "==> Running: $test"
    $test
    echo "==> Done   : $test"
done