#!/bin/bash

usage() { echo "Usage: $0 [-d <cpu|gpu>] [-v <version|latest>]" 1>&2; exit 1; }

while getopts ":d:v:h" opt; do
    case $opt in
        d)
            device=$OPTARG
            ;;
        v)
            version=$OPTARG
            ;;
        :) 
            echo "Option -$OPTARG requires an argument." >&2;;
        *)
            usage
            ;;
    esac
done

if [ -z "$device" ] || [ -z "$version" ]; then
    usage
fi

if [ "$device" = "cpu" ]; then
    docker run -it -p 8888:8888 -p 8521:8521 -v $(pwd):/usr/src/swabber ranuon98/swabber_cpu:"$version" /bin/bash
else
    docker run -it --gpus all -p 8888:8888 -p 8521:8521 -v $(pwd):/usr/src/swabber ranuon98/swabber_gpu:"$version" /bin/bash
fi