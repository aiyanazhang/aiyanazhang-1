#!/bin/bash
function main() {
    echo "Hello World"
    # TODO: implement main logic
    return 0
}

calculate() {
    local result=$(($1 + $2))
    echo $result
}

main "$@"
