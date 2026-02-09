#!/bin/bash
# Local Linux testing script for EasyClaude

set -e

echo "=== EasyClaude Linux Test Runner ==="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

# Test sections
run_unit_tests() {
    echo -e "${BLUE}Running unit tests...${NC}"
    pytest tests/platform/test_linux.py -v --cov=app/platform/linux --cov-report=term-missing
}

run_integration_tests() {
    echo -e "${BLUE}Running integration tests...${NC}"
    pytest tests/platform/test_linux_integration.py -v
}

run_mock_tests() {
    echo -e "${BLUE}Running mock desktop tests...${NC}"
    pytest tests/platform/test_linux_desktop.py -v
}

run_all_linux_tests() {
    echo -e "${BLUE}Running all Linux tests...${NC}"
    pytest tests/ -v -k "linux or Linux" --cov=app/platform/linux --cov-report=term-missing
}

run_all_tests() {
    echo -e "${BLUE}Running complete test suite...${NC}"
    pytest tests/ -v --cov=app --cov-report=term-missing
}

check_dependencies() {
    echo -e "${YELLOW}Checking dependencies...${NC}"

    deps=("gnome-terminal" "konsole" "xfce4-terminal" "xterm")
    missing=()

    for dep in "${deps[@]}"; do
        if command -v "$dep" &> /dev/null; then
            echo -e "  ${GREEN}✓${NC} $dep"
        else
            echo -e "  ${RED}✗${NC} $dep (not found)"
            missing+=("$dep")
        fi
    done

    # Check Python
    if command -v python3 &> /dev/null; then
        python_version=$(python3 --version 2>&1 | awk '{print $2}')
        echo -e "  ${GREEN}✓${NC} python3 $python_version"
    else
        echo -e "  ${RED}✗${NC} python3 (not found)"
        missing+=("python3")
    fi

    # Check pytest
    if python3 -m pytest --version &> /dev/null; then
        pytest_version=$(python3 -m pytest --version 2>&1 | head -n1)
        echo -e "  ${GREEN}✓${NC} $pytest_version"
    else
        echo -e "  ${RED}✗${NC} pytest (not found)"
        missing+=("pytest")
    fi

    if [ ${#missing[@]} -gt 0 ]; then
        echo ""
        echo -e "${RED}Missing dependencies: ${missing[*]}${NC}"
        echo "Install with:"
        if [ "$(uname -s)" == "Linux" ]; then
            echo "  sudo apt-get install ${missing[*]}"
            echo "  pip3 install pytest pytest-cov pytest-mock"
        fi
        return 1
    fi

    echo ""
    return 0
}

run_lint() {
    echo -e "${BLUE}Running lint checks...${NC}"

    echo -e "${YELLOW}flake8...${NC}"
    if command -v flake8 &> /dev/null; then
        flake8 app/platform/linux.py --max-line-length=100 || true
    else
        echo "  flake8 not installed, skipping"
    fi

    echo -e "${YELLOW}pylint...${NC}"
    if command -v pylint &> /dev/null; then
        pylint app/platform/linux.py --exit-zero || true
    else
        echo "  pylint not installed, skipping"
    fi

    echo -e "${YELLOW}mypy...${NC}"
    if command -v mypy &> /dev/null; then
        mypy app/platform/linux.py --ignore-missing-imports || true
    else
        echo "  mypy not installed, skipping"
    fi
}

run_coverage_report() {
    echo -e "${BLUE}Generating coverage report...${NC}"
    pytest tests/platform/test_linux.py --cov=app/platform/linux --cov-report=html --cov-report=term
    echo "HTML report: htmlcov/index.html"
}

test_with_xvfb() {
    echo -e "${BLUE}Running tests with Xvfb (virtual display)...${NC}"

    # Start Xvfb
    Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
    XVFB_PID=$!
    export DISPLAY=:99

    # Give Xvfb time to start
    sleep 1

    # Run tests
    pytest tests/platform/test_linux_desktop.py -v

    # Cleanup
    kill $XVFB_PID 2>/dev/null || true
}

show_help() {
    cat << EOF
Usage: $0 [COMMAND] [OPTIONS]

Commands:
  unit           Run Linux unit tests only
  integration    Run Linux integration tests only
  mock           Run Linux mock tests only
  linux          Run all Linux-specific tests
  all            Run complete test suite
  check          Check dependencies
  lint           Run lint checks
  coverage       Generate coverage report
  xvfb           Run tests with Xvfb (virtual display)
  help           Show this help message

Options:
  -v, --verbose  Verbose output
  -q, --quiet    Quiet output

Examples:
  $0 unit                    # Run unit tests only
  $0 check                  # Check dependencies before testing
  $0 all --verbose          # Run all tests with verbose output
  $0 xvfb                   # Run GUI tests with virtual display

EOF
}

# Parse arguments
COMMAND="${1:-all}"
shift || true

case "$COMMAND" in
    unit)
        run_unit_tests
        ;;
    integration)
        run_integration_tests
        ;;
    mock)
        run_mock_tests
        ;;
    linux)
        run_all_linux_tests
        ;;
    all)
        check_dependencies
        run_all_tests
        ;;
    check)
        check_dependencies
        ;;
    lint)
        run_lint
        ;;
    coverage)
        run_coverage_report
        ;;
    xvfb)
        test_with_xvfb
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Test run complete!${NC}"
