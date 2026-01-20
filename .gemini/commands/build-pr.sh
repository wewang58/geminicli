#!/bin/bash
set -e

# Default settings
# Use hack/utils.sh if available, otherwise default to podman or docker
if [ -f "hack/utils.sh" ]; then
    CONTAINER_ENGINE=$(bash hack/utils.sh get_container_engine)
else
    if command -v podman &> /dev/null; then
        CONTAINER_ENGINE="podman"
    else
        CONTAINER_ENGINE="docker"
    fi
fi

OUT_DIR=${OUT_DIR:-bin}
TAG=${TAG:-latest}

# Helper function for printing
info() {
    echo -e "\033[32m[INFO] $1\033[0m"
}

# Help message
usage() {
    echo "Usage: $0 [options] [components...]"
    echo ""
    echo "Build HyperShift components (CLI, images, operators) from a PR and push to a repository."
    echo ""
    echo "Components:"
    echo "  --cli              Build hypershift CLI"
    echo "  --hcp              Build hcp CLI (product CLI)"
    echo "  --operator         Build hypershift-operator binary"
    echo "  --cpo              Build control-plane-operator binary"
    echo "  --operator-image   Build hypershift-operator container image"
    echo "  --cpo-image        Build control-plane-operator container image"
    echo "  --all              Build everything"
    echo ""
    echo "Options:"
    echo "  --tag <tag>        Set image tag (default: latest)"
    echo "  --push             Push built images to registry"
    echo "  --operator-name <n> Set hypershift-operator image name"
    echo "  --cpo-name <n>      Set control-plane-operator image name"
    echo "  --help             Show this help message"
}

if [ $# -eq 0 ]; then
    usage
    exit 1
fi

BUILD_CLI=false
BUILD_HCP=false
BUILD_OPERATOR=false
BUILD_CPO=false
BUILD_OPERATOR_IMAGE=false
BUILD_CPO_IMAGE=false
PUSH_IMAGES=false
OPERATOR_NAME="hypershift-operator"
CPO_NAME="control-plane-operator"

while [[ $# -gt 0 ]]; do
    case $1 in
        --cli) BUILD_CLI=true; shift ;;
        --hcp) BUILD_HCP=true; shift ;;
        --operator) BUILD_OPERATOR=true; shift ;;
        --cpo) BUILD_CPO=true; shift ;;
        --operator-image) BUILD_OPERATOR_IMAGE=true; shift ;;
        --cpo-image) BUILD_CPO_IMAGE=true; shift ;;
        --push) PUSH_IMAGES=true; shift ;;
        --operator-name) OPERATOR_NAME="$2"; shift 2 ;;
        --cpo-name) CPO_NAME="$2"; shift 2 ;;
        --all)
            BUILD_CLI=true
            BUILD_HCP=true
            BUILD_OPERATOR=true
            BUILD_CPO=true
            BUILD_OPERATOR_IMAGE=true
            BUILD_CPO_IMAGE=true
            shift ;;
        --tag) TAG="$2"; shift 2 ;;
        --help) usage; exit 0 ;;
        *) echo "Unknown option: $1"; usage; exit 1 ;;
    esac
done

if [ "$BUILD_CLI" = true ]; then
    info "Building hypershift CLI..."
    make hypershift OUT_DIR="$OUT_DIR"
fi

if [ "$BUILD_HCP" = true ]; then
    info "Building hcp CLI..."
    make product-cli OUT_DIR="$OUT_DIR"
fi

if [ "$BUILD_OPERATOR" = true ]; then
    info "Building hypershift-operator binary..."
    make hypershift-operator OUT_DIR="$OUT_DIR"
fi

if [ "$BUILD_CPO" = true ]; then
    info "Building control-plane-operator binary..."
    make control-plane-operator OUT_DIR="$OUT_DIR"
fi

if [ "$BUILD_OPERATOR_IMAGE" = true ]; then
    IMAGE_NAME="$OPERATOR_NAME:$TAG"
    info "Building hypershift-operator image ($IMAGE_NAME)..."
    $CONTAINER_ENGINE build -f Containerfile.operator -t "$IMAGE_NAME" .
    if [ "$PUSH_IMAGES" = true ]; then
        info "Pushing hypershift-operator image ($IMAGE_NAME)..."
        $CONTAINER_ENGINE push "$IMAGE_NAME"
    fi
fi

if [ "$BUILD_CPO_IMAGE" = true ]; then
    IMAGE_NAME="$CPO_NAME:$TAG"
    info "Building control-plane-operator image ($IMAGE_NAME)..."
    $CONTAINER_ENGINE build -f Containerfile.control-plane -t "$IMAGE_NAME" .
    if [ "$PUSH_IMAGES" = true ]; then
        info "Pushing control-plane-operator image ($IMAGE_NAME)..."
        $CONTAINER_ENGINE push "$IMAGE_NAME"
    fi
fi

info "Build complete!"
