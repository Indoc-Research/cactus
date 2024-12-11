#!/usr/bin/env bash
set -e

# Helper function to display usage
show_help() {
    echo "Usage: $0 <PYTHON_VERSION> <UNIQUE_ENV_NAME> <KERNEL_DISPLAY_NAME> <PIP_PACKAGES>"
    echo ""
    echo "Arguments:"
    echo "  PYTHON_VERSION       Python version to use for the environment (e.g., 3.9)"
    echo "  UNIQUE_ENV_NAME      Unique name for the environment (e.g., envA)"
    echo "  KERNEL_DISPLAY_NAME  Display name for the Jupyter kernel (e.g., Python (envA))"
    echo "  PIP_PACKAGES         Space-separated Python packages to install via pip (e.g., package1 package2)"
    echo ""
    echo "Example:"
    echo " $0 '3.11' 'uniq-na3-1234' 'kernel with na3' package1 package2"
    exit 0
}

# Check if --help was passed
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    show_help
fi

# Check if required arguments are provided
if [[ $# -lt 4 ]]; then
    echo "Error: Missing arguments."
    echo "Run '$0 --help' for usage instructions."
    exit 1
fi

# VARS
CONDA_BIN="/opt/tljh/user/bin/conda"
PYTHON_VERSION="$1"
UNIQUE_ENV_NAME="$2"
KERNEL_DISPLAY_NAME="$3"
shift 3 # Remove the first three arguments so the remaining ones can be treated as PIP_PACKAGES
PIP_PACKAGES=("$@")

# Create the Python environment with ipykernel
sudo $CONDA_BIN create -n $UNIQUE_ENV_NAME python=$PYTHON_VERSION -y
sudo /opt/tljh/user/bin/conda run -n $UNIQUE_ENV_NAME pip install "${PIP_PACKAGES[@]}"
sudo /opt/tljh/user/bin/conda run -n $UNIQUE_ENV_NAME pip install ipykernel

# Register the kernel with TLJH
sudo /opt/tljh/user/bin/conda run -n $UNIQUE_ENV_NAME python -m ipykernel install \
    --prefix=/opt/tljh/user \
    --name $UNIQUE_ENV_NAME \
    --display-name "$KERNEL_DISPLAY_NAME"

echo "Environments and kernels created successfully!"

echo "Don't forget to restart TLJH if you want to apply changes:"
echo "    sudo systemctl restart jupyterhub"
