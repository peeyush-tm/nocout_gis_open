#! /bin/bash

find . -type f -name "*.py" | xargs sed -i 's/[ \t]*$//'
