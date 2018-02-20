#!/usr/bin/env bash
1;4205;0c
image="/tmp/000_0_LL.png"

usage() {
    echo $0
    echo "Shows (as an normalized image) an image"
    echo "  [-i image to show ($image1)]"
    echo "  [-? help]"
}

echo $0: parsing: $@

while getopts "i:?" opt; do
    case ${opt} in
        i)
            image="${OPTARG}"
            echo "input =" $image
            ;;
        ?)
            usage
            exit 0
            ;;
        \?)
            echo "Invalid option: -${OPTARG}" >&2
            usage
            exit 1
            ;;
        :)
            echo "Option -${OPTARG} requires an argument." >&2
            usage
            exit 1
            ;;
    esac
done

set -x

./ycc2rgb.py -i $image -o /tmp/ycc2rgb.png
display -normalize /tmp/ycc2rgb.png

set +x
