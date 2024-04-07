#!/usr/bin/env bash
set -eu -o pipefail

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ] ; do SOURCE="$(readlink "$SOURCE")"; done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
PROJECT_DIR="$(dirname $(dirname $DIR))"
KEEPSECRET="$PROJECT_DIR/keepsecret.py"
cd $DIR

# production secret key
SECRET_KEY=

rm -rf *.encrypted

# test encryption
$KEEPSECRET encrypt -s development
if [ ! -f file1.txt.encrypted ]; then
    echo "file1.txt.encrypted should exist as a result of encryption"
    exit 1
fi

if [ ! -f file2.txt.encrypted ]; then
    echo "file2.txt.encrypted should exist as a result of encryption"
    exit 1
fi

$KEEPSECRET encrypt -s production
if [ ! -f file3.txt.encrypted ]; then
    echo "file3.txt.encrypted should exist as a result of encryption"
    exit 1
fi

if [ ! -f file4.txt.encrypted ]; then
    echo "file4.txt.encrypted should exist as a result of encryption"
    exit 1
fi


# test decryption
echo "AGE-SECRET-KEY-1XPH2MHHKE8ZSMP9FEXFPAPKYWTJEVJAK0SNE64ZJ0QKYXK4Z7DUSZ6W8AK" | $KEEPSECRET decrypt -s development
# it should decrypt the development section files with production secret key
echo "AGE-SECRET-KEY-1J90PAZEMLGMDGZPZJFFPSM93KP6VAYR3TALJTKLGH5RVAGH5JERQKPH7QD" | $KEEPSECRET decrypt -s development
echo "AGE-SECRET-KEY-1J90PAZEMLGMDGZPZJFFPSM93KP6VAYR3TALJTKLGH5RVAGH5JERQKPH7QD" | $KEEPSECRET decrypt -s production

