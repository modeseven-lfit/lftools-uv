#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2025 The Linux Foundation
#
# Validate UV installation on CentOS 7 systems
#
# This script performs comprehensive validation of UV installation
# to ensure it's working correctly on CentOS 7 systems.

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results tracking
TESTS_PASSED=0
TESTS_FAILED=0
FAILED_TESTS=()

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

log_test_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((TESTS_PASSED++))
}

log_test_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((TESTS_FAILED++))
    FAILED_TESTS+=("$1")
}

# Check if this is CentOS 7
check_centos7() {
    log_info "Checking CentOS 7 compatibility..."

    if [[ ! -f /etc/centos-release ]]; then
        log_test_fail "Not running on CentOS"
        return 1
    fi

    local version
    version=$(cat /etc/centos-release | grep -oE '[0-9]+' | head -1)
    if [[ "$version" != "7" ]]; then
        log_test_fail "Not running on CentOS 7 (detected version: $version)"
        return 1
    fi

    log_test_pass "Running on CentOS 7"
    return 0
}

# Test UV binary availability
test_uv_binary() {
    log_info "Testing UV binary availability..."

    if command -v uv >/dev/null 2>&1; then
        log_test_pass "UV binary found in PATH"

        # Check if it's executable
        if [[ -x "$(command -v uv)" ]]; then
            log_test_pass "UV binary is executable"
        else
            log_test_fail "UV binary is not executable"
            return 1
        fi
    else
        log_test_fail "UV binary not found in PATH"
        return 1
    fi

    return 0
}

# Test UV version
test_uv_version() {
    log_info "Testing UV version command..."

    local version_output
    if version_output=$(uv --version 2>&1); then
        log_test_pass "UV version command works: $version_output"

        # Check if version follows expected format
        if [[ "$version_output" =~ ^uv\ [0-9]+\.[0-9]+\.[0-9]+ ]]; then
            log_test_pass "UV version format is correct"
        else
            log_test_fail "UV version format is unexpected: $version_output"
            return 1
        fi
    else
        log_test_fail "UV version command failed: $version_output"
        return 1
    fi

    return 0
}

# Test UV help command
test_uv_help() {
    log_info "Testing UV help command..."

    if uv --help >/dev/null 2>&1; then
        log_test_pass "UV help command works"
    else
        log_test_fail "UV help command failed"
        return 1
    fi

    return 0
}

# Test UV subcommands
test_uv_subcommands() {
    log_info "Testing UV subcommands..."

    local subcommands=("pip" "venv" "python" "tool" "run")

    for cmd in "${subcommands[@]}"; do
        if uv "$cmd" --help >/dev/null 2>&1; then
            log_test_pass "UV $cmd subcommand works"
        else
            log_test_fail "UV $cmd subcommand failed"
        fi
    done
}

# Test Python version management
test_python_management() {
    log_info "Testing UV Python version management..."

    # Test python list command
    if uv python list >/dev/null 2>&1; then
        log_test_pass "UV python list command works"
    else
        log_test_fail "UV python list command failed"
    fi

    # Test python install (if internet available)
    if ping -c 1 google.com >/dev/null 2>&1; then
        log_info "Internet connection available, testing Python installation..."

        # Try to install a Python version (this might take a while)
        if timeout 300 uv python install 3.11 >/dev/null 2>&1; then
            log_test_pass "UV can install Python versions"
        else
            log_test_fail "UV Python installation failed or timed out"
        fi
    else
        log_warn "No internet connection - skipping Python installation test"
    fi
}

# Test project creation and management
test_project_creation() {
    log_info "Testing UV project creation..."

    local test_dir="/tmp/uv-validation-test-$$"

    # Create test directory
    mkdir -p "$test_dir"
    cd "$test_dir"

    # Test project initialization
    if uv init test-project >/dev/null 2>&1; then
        log_test_pass "UV project initialization works"

        cd test-project

        # Check if project files were created
        if [[ -f "pyproject.toml" && -f "main.py" ]]; then
            log_test_pass "UV created expected project files"
        else
            log_test_fail "UV did not create expected project files"
        fi

        # Test adding dependencies (if internet available)
        if ping -c 1 google.com >/dev/null 2>&1; then
            log_info "Testing dependency management..."

            if timeout 60 uv add requests >/dev/null 2>&1; then
                log_test_pass "UV can add dependencies"

                # Test running the project
                if uv run main.py >/dev/null 2>&1; then
                    log_test_pass "UV can run project scripts"
                else
                    log_test_fail "UV cannot run project scripts"
                fi
            else
                log_test_fail "UV cannot add dependencies (timeout or error)"
            fi
        else
            log_warn "No internet connection - skipping dependency tests"
        fi

    else
        log_test_fail "UV project initialization failed"
    fi

    # Clean up test directory
    cd /
    rm -rf "$test_dir"
}

# Test pip compatibility
test_pip_compatibility() {
    log_info "Testing UV pip compatibility..."

    # Test pip help
    if uv pip --help >/dev/null 2>&1; then
        log_test_pass "UV pip interface works"
    else
        log_test_fail "UV pip interface failed"
        return 1
    fi

    # Test pip list (should work even without packages)
    if uv pip list >/dev/null 2>&1; then
        log_test_pass "UV pip list command works"
    else
        log_test_fail "UV pip list command failed"
    fi

    return 0
}

# Test uvx functionality
test_uvx() {
    log_info "Testing uvx functionality..."

    if command -v uvx >/dev/null 2>&1; then
        log_test_pass "uvx binary found"

        if uvx --help >/dev/null 2>&1; then
            log_test_pass "uvx help command works"
        else
            log_test_fail "uvx help command failed"
        fi
    else
        log_test_fail "uvx binary not found"
    fi
}

# Test system integration
test_system_integration() {
    log_info "Testing system integration..."

    # Check if UV is in system PATH
    local uv_path
    uv_path=$(which uv 2>/dev/null || echo "")

    if [[ "$uv_path" =~ ^/usr/local/bin/ ]]; then
        log_test_pass "UV is installed in system location (/usr/local/bin)"
    elif [[ "$uv_path" =~ /.local/bin/ ]]; then
        log_warn "UV is installed in user location ($uv_path) - consider system-wide installation"
    else
        log_test_fail "UV path is unexpected: $uv_path"
    fi

    # Check profile script
    if [[ -f /etc/profile.d/uv.sh ]]; then
        log_test_pass "System-wide UV profile script exists"
    else
        log_warn "System-wide UV profile script not found - UV may not be available in new shells"
    fi
}

# Test glibc compatibility
test_glibc_compatibility() {
    log_info "Testing glibc compatibility..."

    local glibc_version
    glibc_version=$(ldd --version 2>&1 | head -1 | grep -oE '[0-9]+\.[0-9]+' | head -1)

    log_info "Detected glibc version: $glibc_version"

    # CentOS 7 typically has glibc 2.17
    if [[ "$glibc_version" =~ ^2\.17 ]]; then
        log_test_pass "Running with expected CentOS 7 glibc version"

        # Check if UV binary is statically linked (musl version)
        local uv_binary
        uv_binary=$(which uv)

        if file "$uv_binary" | grep -q "statically linked"; then
            log_test_pass "UV binary is statically linked (good for old glibc)"
        else
            log_warn "UV binary may not be statically linked - could cause issues"
        fi
    else
        log_warn "Unexpected glibc version: $glibc_version"
    fi
}

# Generate test report
generate_report() {
    echo
    echo "======================================"
    echo "UV CentOS 7 Validation Report"
    echo "======================================"
    echo "Date: $(date)"
    echo "System: $(cat /etc/centos-release 2>/dev/null || echo 'Unknown')"
    echo "UV Version: $(uv --version 2>/dev/null || echo 'Not available')"
    echo "UV Location: $(which uv 2>/dev/null || echo 'Not found')"
    echo
    echo "Test Results:"
    echo "============="
    echo "Tests Passed: $TESTS_PASSED"
    echo "Tests Failed: $TESTS_FAILED"
    echo "Total Tests: $((TESTS_PASSED + TESTS_FAILED))"

    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}Overall Status: ALL TESTS PASSED${NC}"
        echo "UV is fully functional on this CentOS 7 system."
    else
        echo -e "${RED}Overall Status: SOME TESTS FAILED${NC}"
        echo
        echo "Failed Tests:"
        for test in "${FAILED_TESTS[@]}"; do
            echo "  • $test"
        done
        echo
        echo "Please review the failed tests above and address any issues."
    fi

    echo
    echo "Recommendations:"
    echo "================"

    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo "• UV installation is working correctly"
        echo "• Consider documenting this configuration for other systems"
        echo "• Plan for migration from CentOS 7 to a supported distribution"
    else
        echo "• Review and fix failed tests before using UV in production"
        echo "• Consider reinstalling UV if multiple tests failed"
        echo "• Check internet connectivity if network-dependent tests failed"
    fi

    echo "• Regularly test UV functionality after system updates"
    echo "• Monitor for UV updates and test them in non-production first"
    echo "• Maintain backups of working UV installations"
}

# Main function
main() {
    echo "UV CentOS 7 Validation Script"
    echo "============================="
    echo

    # Run all tests
    check_centos7 || true
    test_uv_binary || true
    test_uv_version || true
    test_uv_help || true
    test_uv_subcommands || true
    test_python_management || true
    test_project_creation || true
    test_pip_compatibility || true
    test_uvx || true
    test_system_integration || true
    test_glibc_compatibility || true

    # Generate final report
    generate_report

    # Exit with appropriate code
    if [[ $TESTS_FAILED -eq 0 ]]; then
        exit 0
    else
        exit 1
    fi
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
