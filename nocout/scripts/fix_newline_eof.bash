#! /bin/bash

find -type f -name "*.py" -exec sh -c '[ -n "$(sed -n "\$p" $1)" ] && echo "$1"' _ {} \; | xargs sed -i -e '$a\'
