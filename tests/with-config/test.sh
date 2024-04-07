#!/usr/bin/env bash
set -eu -o pipefail

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ] ; do SOURCE="$(readlink "$SOURCE")"; done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
PROJECT_DIR="$(dirname $(dirname $DIR))"
KEEPSECRET="$PROJECT_DIR/keepsecret.py"
cd $DIR

SECRET_KEY="AGE-SECRET-KEY-1XPH2MHHKE8ZSMP9FEXFPAPKYWTJEVJAK0SNE64ZJ0QKYXK4Z7DUSZ6W8AK"

rm -rf *.encrypted

# test encryption
$KEEPSECRET encrypt 

if [ ! -f file1.txt.encrypted ]; then
    echo "file1.txt.encrypted should exist as a result of encryption"
    exit 1
fi

if [ ! -f file2.txt.encrypted ]; then
    echo "file2.txt.encrypted should exist as a result of encryption"
    exit 1
fi

# test decryption
echo $SECRET_KEY | $KEEPSECRET decrypt

