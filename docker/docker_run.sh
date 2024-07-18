#!/bin/bash

usage() {
    echo "Usage: $0 [-d <cpu|gpu>] [-v <version|latest>] [-p <port_mapping>] [-m <volume_mount_path>]"
    echo "  -d  Device type (cpu or gpu)"
    echo "  -v  Version of the Docker image (e.g., latest, 1.0, etc.)"
    echo "  -p  Port mapping (default: 8888:8888,8521:8521)"
    echo "  -m  Volume mount path (default: current directory to /usr/src/swabber)"
    exit 1
}

port_mapping="8888:8888,8521:8521"
volume_mount_path="$(pwd):/usr/src/swabber"

while getopts ":d:v:p:m:h" opt; do
    case $opt in
        d)
            device=$OPTARG
            ;;
        v)
            version=$OPTARG
            ;;
        p)
            port_mapping=$OPTARG
            ;;
        m)
            volume_mount_path=$OPTARG
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

if [ -z "$device" ] || [ -z "$version" ]; then
    usage
fi

if [ "$device" = "cpu" ]; then
    image_name="ranuon98/swabber_cpu:$version"
elif [ "$device" = "gpu" ]; then
    image_name="ranuon98/swabber_gpu:$version"
else
    echo "Invalid device type: $device. Must be 'cpu' or 'gpu'."
    usage
fi

IFS=',' read -r -a port_array <<< "$port_mapping"
port_flags=""
for port in "${port_array[@]}"; do
    port_flags="$port_flags -p $port"
done

if [ "$device" = "cpu" ]; then
    docker run -it $port_flags -v "$volume_mount_path" "$image_name" /bin/bash
else
    docker run -it --gpus all $port_flags -v "$volume_mount_path" "$image_name" /bin/bash
fi

echo "Docker container for image $image_name started successfully."
