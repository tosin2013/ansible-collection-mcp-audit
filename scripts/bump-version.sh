#!/usr/bin/env bash
# Version bump helper script for ansible-collection-mcp-audit
# Usage: ./scripts/bump-version.sh [major|minor|patch] [--commit] [--tag]

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

GALAXY_FILE="galaxy.yml"
PYPROJECT_FILE="pyproject.toml"

# Function to print colored messages
print_error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
}

print_success() {
    echo -e "${GREEN}SUCCESS: $1${NC}"
}

print_info() {
    echo -e "${YELLOW}INFO: $1${NC}"
}

# Function to get current version from galaxy.yml
get_current_version() {
    grep "^version:" "$GALAXY_FILE" | sed 's/version: //' | tr -d "'" | tr -d '"' | tr -d ' '
}

# Function to bump version
bump_version() {
    local current=$1
    local bump_type=$2

    IFS='.' read -r major minor patch <<< "$current"

    case $bump_type in
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        patch)
            patch=$((patch + 1))
            ;;
        *)
            print_error "Invalid bump type: $bump_type. Use: major, minor, or patch"
            exit 1
            ;;
    esac

    echo "${major}.${minor}.${patch}"
}

# Function to update version in galaxy.yml
update_galaxy_version() {
    local new_version=$1

    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/^version:.*/version: ${new_version}/" "$GALAXY_FILE"
    else
        # Linux
        sed -i "s/^version:.*/version: ${new_version}/" "$GALAXY_FILE"
    fi
}

# Function to update version in pyproject.toml
update_pyproject_version() {
    local new_version=$1

    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/^version = .*/version = \"${new_version}\"/" "$PYPROJECT_FILE"
    else
        # Linux
        sed -i "s/^version = .*/version = \"${new_version}\"/" "$PYPROJECT_FILE"
    fi
}

# Main script
main() {
    # Check if we're in the right directory
    if [[ ! -f "$GALAXY_FILE" ]]; then
        print_error "galaxy.yml not found. Please run this script from the collection root."
        exit 1
    fi

    # Parse arguments
    if [[ $# -lt 1 ]]; then
        print_error "Usage: $0 [major|minor|patch] [--commit] [--tag]"
        echo ""
        echo "Examples:"
        echo "  $0 patch              # Bump patch version (1.0.0 -> 1.0.1)"
        echo "  $0 minor --commit     # Bump minor version and commit"
        echo "  $0 major --commit --tag  # Bump major version, commit and tag"
        exit 1
    fi

    BUMP_TYPE=$1
    DO_COMMIT=false
    DO_TAG=false

    shift
    while [[ $# -gt 0 ]]; do
        case $1 in
            --commit)
                DO_COMMIT=true
                shift
                ;;
            --tag)
                DO_TAG=true
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done

    # Get current version
    CURRENT_VERSION=$(get_current_version)
    print_info "Current version: $CURRENT_VERSION"

    # Calculate new version
    NEW_VERSION=$(bump_version "$CURRENT_VERSION" "$BUMP_TYPE")
    print_info "New version: $NEW_VERSION"

    # Update galaxy.yml
    print_info "Updating $GALAXY_FILE..."
    update_galaxy_version "$NEW_VERSION"

    # Update pyproject.toml
    print_info "Updating $PYPROJECT_FILE..."
    update_pyproject_version "$NEW_VERSION"

    print_success "Version updated to $NEW_VERSION"

    # Commit if requested
    if [[ "$DO_COMMIT" == true ]]; then
        print_info "Creating commit..."
        git add "$GALAXY_FILE" "$PYPROJECT_FILE"
        git commit -m "chore: bump version to $NEW_VERSION"
        print_success "Committed version bump"
    fi

    # Tag if requested
    if [[ "$DO_TAG" == true ]]; then
        TAG_NAME="v$NEW_VERSION"
        print_info "Creating tag $TAG_NAME..."
        git tag -a "$TAG_NAME" -m "Release version $NEW_VERSION"
        print_success "Created tag $TAG_NAME"

        echo ""
        print_info "To push changes and trigger Galaxy publish:"
        echo "  git push origin main --tags"
    elif [[ "$DO_COMMIT" == true ]]; then
        echo ""
        print_info "To push changes:"
        echo "  git push origin main"
        echo ""
        print_info "To also create a tag and trigger Galaxy publish:"
        echo "  git tag v$NEW_VERSION"
        echo "  git push origin main --tags"
    else
        echo ""
        print_info "To commit and tag this version:"
        echo "  git add $GALAXY_FILE $PYPROJECT_FILE"
        echo "  git commit -m 'chore: bump version to $NEW_VERSION'"
        echo "  git tag v$NEW_VERSION"
        echo "  git push origin main --tags"
    fi
}

main "$@"
