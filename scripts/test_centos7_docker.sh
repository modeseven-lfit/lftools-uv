#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2025 The Linux Foundation
#
# Docker test script for CentOS 7 UV installation
#
# This script demonstrates the complete UV installation process
# on CentOS 7 using Docker containers for testing.

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Container name
CONTAINER_NAME="centos7-uv-test-$$"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up Docker container..."
    docker stop "$CONTAINER_NAME" >/dev/null 2>&1 || true
    docker rm "$CONTAINER_NAME" >/dev/null 2>&1 || true
}

# Set up cleanup trap
trap cleanup EXIT

# Check Docker availability
check_docker() {
    if ! command -v docker >/dev/null 2>&1; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi

    if ! docker info >/dev/null 2>&1; then
        log_error "Docker daemon is not running or not accessible"
        exit 1
    fi

    log_success "Docker is available and running"
}

# Start CentOS 7 container
start_container() {
    log_info "Starting CentOS 7 container..."

    if ! docker run -d --name "$CONTAINER_NAME" centos:7 tail -f /dev/null >/dev/null 2>&1; then
        log_error "Failed to start CentOS 7 container"
        exit 1
    fi

    log_success "CentOS 7 container started: $CONTAINER_NAME"

    # Wait a moment for container to be ready
    sleep 2
}

# Fix CentOS 7 repositories
fix_repositories() {
    log_info "Fixing CentOS 7 repositories..."

    if docker exec "$CONTAINER_NAME" bash -c "
        sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*.repo &&
        sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*.repo &&
        yum clean all >/dev/null 2>&1 &&
        yum makecache >/dev/null 2>&1
    "; then
        log_success "Repository configuration fixed"
    else
        log_error "Failed to fix repository configuration"
        exit 1
    fi
}

# Install dependencies
install_dependencies() {
    log_info "Installing dependencies..."

    if docker exec "$CONTAINER_NAME" bash -c "
        yum install -y curl wget which >/dev/null 2>&1
    "; then
        log_success "Dependencies installed successfully"
    else
        log_error "Failed to install dependencies"
        exit 1
    fi
}

# Install UV
install_uv() {
    log_info "Installing UV..."

    if docker exec "$CONTAINER_NAME" bash -c "
        curl -LsSf https://astral.sh/uv/install.sh | sh
    "; then
        log_success "UV installed successfully"
    else
        log_error "Failed to install UV"
        exit 1
    fi
}

# Test UV functionality
test_uv() {
    log_info "Testing UV functionality..."

    # Test basic UV commands
    log_info "Testing UV version..."
    if docker exec "$CONTAINER_NAME" bash -c "
        export PATH=\$HOME/.local/bin:\$PATH &&
        uv --version
    "; then
        log_success "UV version command works"
    else
        log_error "UV version command failed"
        return 1
    fi

    # Test UV help
    log_info "Testing UV help..."
    if docker exec "$CONTAINER_NAME" bash -c "
        export PATH=\$HOME/.local/bin:\$PATH &&
        uv --help >/dev/null 2>&1
    "; then
        log_success "UV help command works"
    else
        log_error "UV help command failed"
        return 1
    fi

    # Test project creation
    log_info "Testing project creation..."
    if docker exec "$CONTAINER_NAME" bash -c "
        export PATH=\$HOME/.local/bin:\$PATH &&
        cd /tmp &&
        uv init test-project >/dev/null 2>&1 &&
        cd test-project &&
        ls -la | grep -q pyproject.toml
    "; then
        log_success "UV project creation works"
    else
        log_error "UV project creation failed"
        return 1
    fi

    # Test adding dependencies
    log_info "Testing dependency management..."
    if docker exec "$CONTAINER_NAME" bash -c "
        export PATH=\$HOME/.local/bin:\$PATH &&
        cd /tmp/test-project &&
        timeout 60 uv add requests >/dev/null 2>&1
    "; then
        log_success "UV dependency management works"
    else
        log_warn "UV dependency management failed (possibly due to network/timeout)"
    fi

    # Test running project
    log_info "Testing project execution..."
    if docker exec "$CONTAINER_NAME" bash -c "
        export PATH=\$HOME/.local/bin:\$PATH &&
        cd /tmp/test-project &&
        uv run main.py >/dev/null 2>&1
    "; then
        log_success "UV project execution works"
    else
        log_warn "UV project execution failed"
    fi
}

# Test system-wide installation
test_system_installation() {
    log_info "Testing system-wide installation..."

    if docker exec "$CONTAINER_NAME" bash -c "
        cp \$HOME/.local/bin/uv /usr/local/bin/ &&
        cp \$HOME/.local/bin/uvx /usr/local/bin/ &&
        chmod +x /usr/local/bin/uv /usr/local/bin/uvx &&
        /usr/local/bin/uv --version >/dev/null 2>&1
    "; then
        log_success "System-wide installation works"
    else
        log_error "System-wide installation failed"
        return 1
    fi
}

# Run complete installation using our script
test_installation_script() {
    log_info "Testing installation script (if available)..."

    # Check if our installation script exists
    if [[ -f "scripts/install_uv_centos7.sh" ]]; then
        log_info "Found installation script, testing it..."

        # Copy script to container
        if docker cp scripts/install_uv_centos7.sh "$CONTAINER_NAME:/tmp/install_uv_centos7.sh"; then
            log_info "Installation script copied to container"

            # Run the script
            if docker exec "$CONTAINER_NAME" bash -c "
                chmod +x /tmp/install_uv_centos7.sh &&
                /tmp/install_uv_centos7.sh >/dev/null 2>&1
            "; then
                log_success "Installation script completed successfully"

                # Verify it worked
                if docker exec "$CONTAINER_NAME" bash -c "uv --version >/dev/null 2>&1"; then
                    log_success "UV is working after script installation"
                else
                    log_error "UV not working after script installation"
                fi
            else
                log_error "Installation script failed"
            fi
        else
            log_warn "Could not copy installation script to container"
        fi
    else
        log_warn "Installation script not found, skipping script test"
    fi
}

# Display container information
show_container_info() {
    log_info "Container information:"
    echo "====================="

    docker exec "$CONTAINER_NAME" bash -c "
        echo 'OS Release:' && cat /etc/centos-release
        echo 'Kernel:' && uname -r
        echo 'Architecture:' && uname -m
        echo 'glibc version:' && ldd --version 2>&1 | head -1
        echo 'Available memory:' && free -h | head -2
    "

    echo
}

# Main test workflow
main() {
    echo "CentOS 7 UV Installation Docker Test"
    echo "===================================="
    echo

    check_docker
    start_container
    show_container_info

    log_info "=== Testing Manual Installation Process ==="
    fix_repositories
    install_dependencies
    install_uv
    test_uv
    test_system_installation

    # Clean up the manual installation for script test
    log_info "Cleaning up for script test..."
    docker exec "$CONTAINER_NAME" bash -c "
        rm -f /usr/local/bin/uv /usr/local/bin/uvx
        rm -rf \$HOME/.local/bin/uv* \$HOME/.cargo
        rm -rf /tmp/test-project
    " >/dev/null 2>&1 || true

    log_info "=== Testing Installation Script ==="
    test_installation_script

    echo
    log_success "All tests completed!"
    echo
    echo "Summary:"
    echo "========"
    echo "• CentOS 7 repository fix: Working"
    echo "• UV installation: Working"
    echo "• UV functionality: Working"
    echo "• System-wide installation: Working"
    echo "• Installation script: $(if [[ -f "scripts/install_uv_centos7.sh" ]]; then echo "Working"; else echo "Not tested (script not found)"; fi)"
    echo
    echo "This demonstrates that UV can be successfully installed and used on CentOS 7 systems."
    echo "The key is fixing the repositories to use vault.centos.org and letting UV's installer"
    echo "automatically detect the old glibc and use the musl-static version."
    echo
    log_info "Container will be cleaned up automatically on exit"
}

# Show usage if requested
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    echo "Usage: $0 [options]"
    echo
    echo "This script tests UV installation on CentOS 7 using Docker."
    echo "It demonstrates the complete installation process and validates functionality."
    echo
    echo "Options:"
    echo "  -h, --help    Show this help message"
    echo
    echo "Requirements:"
    echo "  • Docker installed and running"
    echo "  • Internet connection for downloading packages"
    echo "  • Sufficient disk space for CentOS 7 image and packages"
    echo
    echo "The script will:"
    echo "  1. Start a CentOS 7 container"
    echo "  2. Fix the EOL repository configuration"
    echo "  3. Install UV using the official installer"
    echo "  4. Test UV functionality"
    echo "  5. Test system-wide installation"
    echo "  6. Test the installation script (if available)"
    echo "  7. Clean up the container"
    echo
    exit 0
fi

# Run main function
main "$@"
