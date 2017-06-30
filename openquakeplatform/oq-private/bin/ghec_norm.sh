#!/bin/bash
usage () {
    echo "USAGE:"
    echo "$0 <file-in> <file-out>"
    exit $1
}

#
#  MAIN
#

if [ $# -ne 2 ]; then
    usage 1
fi

fin="$1"
fot="$2"
which konwert >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "konwert packace is required, install it and run again"
    exit 1
fi


cat "$fin" | grep -v '^#' | konwert iso15-utf8 | sed 's/\xc2\x96/-/g' > "$fot"

echo "Conversion check: a list of strange characters, currently only [Þ] must be recognized."
echo "[" | tr -d '\n'
cat "$fot" | sed 's/[-'"'"':\/\?"=\[<+() ,\.a-zA-Z0-9 	]//g;s/]//g' | tr -d '\n' ; echo "]"

exit 0