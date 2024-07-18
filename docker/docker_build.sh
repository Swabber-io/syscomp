#!/bin/bash

usage() {
    echo "Usage: $0 [-o <win|mac>] [-d <cpu|gpu>] [-v <version|latest>]"
    echo "  -o  Operating system (win or mac)"
    echo "  -d  Device type (cpu or gpu)"
    echo "  -v  Version of the Docker image (e.g., latest, 1.0, etc.)"
    exit 1
}

load_env() {
    if [ -f .env ]; then
        export $(cat .env | grep -v '#' | awk '/=/ {print $1}')
    else
        echo ".env file not found."
        exit 1
    fi
}

while getopts ":o:d:v:h" opt; do
    case $opt in
        o)
            os=${OPTARG}
            ;;
        d)
            device=${OPTARG}
            ;;
        v)
            version=${OPTARG}
            ;;
        h)
            usage
            ;;
        :)
            echo "Option -$OPTARG requires an argument." >&2
            usage
            ;;
        *)
            usage
            ;;
    esac
done

if [ -z "$os" ] || [ -z "$device" ] || [ -z "$version" ]; then
    usage
fi

if [ "$os" = "mac" ]; then
    platform="--platform linux/amd64"
elif [ "$os" = "win" ]; then
    platform=""
else
    echo "Invalid OS type: $os. Must be 'win' or 'mac'."
    usage
fi

if [ "$device" = "cpu" ]; then
    dockerfile="docker/Dockerfile.CPU"
    image_name="ranuon98/swabber_cpu:$version"
elif [ "$device" = "gpu" ]; then
    dockerfile="docker/Dockerfile.GPU"
    image_name="ranuon98/swabber_gpu:$version"
else
    echo "Invalid device type: $device. Must be 'cpu' or 'gpu'."
    usage
fi

load_env

docker build $platform -t $image_name -f $dockerfile \
    --build-arg DB_USER=$DB_USER \
    --build-arg DB_PASSWORD=$DB_PASSWORD \
    --build-arg DB_HOST=$DB_HOST \
    --build-arg DB_PORT=$DB_PORT \
    --build-arg DB_NAME=$DB_NAME .

echo "Docker image $image_name built successfully."
