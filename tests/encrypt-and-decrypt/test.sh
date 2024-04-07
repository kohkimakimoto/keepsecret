#!/usr/bin/env bash
set -eu -o pipefail

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ] ; do SOURCE="$(readlink "$SOURCE")"; done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
PROJECT_DIR="$(dirname $(dirname $DIR))"
KEEPSECRET="$PROJECT_DIR/keepsecret.py"
cd $DIR

rm -rf *.encrypted

# test encryption
$KEEPSECRET encrypt -f -r "age12lgj8l7dt3tyfy7c09mr4ukn52qda9ds3n3ceqgxmkceaq9yv38surr65a" -- file1.txt file2.txt

if [ ! -f file1.txt.encrypted ]; then
    echo "file1.txt.encrypted should exist as a result of encryption"
    exit 1
fi

if [ ! -f file2.txt.encrypted ]; then
    echo "file2.txt.encrypted should exist as a result of encryption"
    exit 1
fi

# test decryption
echo "AGE-SECRET-KEY-1XPH2MHHKE8ZSMP9FEXFPAPKYWTJEVJAK0SNE64ZJ0QKYXK4Z7DUSZ6W8AK" | $KEEPSECRET decrypt -f -- file1.txt.encrypted file2.txt.encrypted

