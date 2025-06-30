#!/bin/bash

# Kong Auth Service Documentation Builder
# This script builds and tests the Sphinx documentation

set -e  # Exit on any error

echo "🔨 Building Kong Auth Service Documentation"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "docs/source/conf.py" ]; then
    print_error "This script must be run from the project root directory"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

# Check if pip is available
if ! command -v pip &> /dev/null; then
    print_error "pip is required but not installed"
    exit 1
fi

print_status "Checking prerequisites..."

# Navigate to docs directory
cd docs

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    print_status "Installing documentation dependencies..."
    pip install -r requirements.txt
    print_success "Dependencies installed"
else
    print_warning "No requirements.txt found, skipping dependency installation"
fi

# Clean previous builds
print_status "Cleaning previous builds..."
make clean 2>/dev/null || true
print_success "Clean complete"

# Build HTML documentation
print_status "Building HTML documentation..."
if make html; then
    print_success "HTML documentation built successfully"
else
    print_error "Failed to build HTML documentation"
    exit 1
fi

# Check if build was successful
if [ ! -d "build/html" ]; then
    print_error "HTML build directory not found"
    exit 1
fi

# Count built pages
PAGE_COUNT=$(find build/html -name "*.html" | wc -l)
print_success "Built $PAGE_COUNT HTML pages"

# Check for common issues
print_status "Running documentation checks..."

# Check for broken links (if linkcheck is available)
if command -v sphinx-build &> /dev/null; then
    print_status "Checking for broken links..."
    if make linkcheck > /dev/null 2>&1; then
        print_success "Link check completed"
    else
        print_warning "Link check failed or found issues"
    fi
fi

# Check for spelling errors (if spelling is available)
if command -v sphinx-build &> /dev/null; then
    print_status "Checking spelling..."
    if make spelling > /dev/null 2>&1; then
        print_success "Spelling check completed"
    else
        print_warning "Spelling check failed or found issues"
    fi
fi

# Summary
echo ""
echo "🎉 Documentation Build Summary"
echo "============================="
print_success "Documentation built successfully!"
echo ""
echo "📁 Build location: docs/build/html/"
echo "📄 Pages built: $PAGE_COUNT"
echo ""
echo "🚀 To view the documentation:"
echo "   cd docs/build/html"
echo "   python3 -m http.server 8080"
echo "   Then open http://localhost:8080 in your browser"
echo ""
echo "🔧 Available make commands:"
echo "   make html      - Build HTML documentation"
echo "   make clean     - Clean build directory"
echo "   make serve     - Build and serve documentation"
echo "   make check     - Check for broken links"
echo "   make spelling  - Check spelling"
echo ""

# Optional: Start server
if [ "$1" = "--serve" ]; then
    print_status "Starting documentation server..."
    cd build/html
    print_success "Documentation available at http://localhost:8080"
    print_status "Press Ctrl+C to stop the server"
    python3 -m http.server 8080
fi

print_success "Documentation build completed successfully!" 