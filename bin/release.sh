#!/usr/bin/env bash
set -e

VERSION_FILES=".bumpversion.toml .claude-plugin/plugin.json"

function current_version {
  bump-my-version show current_version
}

function sync_branches {
  echo "👉 Synchronizing branches..."
  git checkout develop
  git pull origin develop
  git checkout main
  git pull origin main
  git checkout develop
  git rebase main
}

function bump_version {
  local version_type=$1
  local before
  before=$(current_version)
  bump-my-version bump "$version_type" --no-commit --no-tag
  local after
  after=$(current_version)
  git add $VERSION_FILES
  git commit -m "🔖 Bump version: ${before} → ${after}"
}

function release {
  local version_type=$1
  bump_version "$version_type"
  local tag="v$(current_version)"

  echo "👉 Creating and pushing tag: $tag"
  git tag -f "$tag"
  git push origin "$tag"

  echo "👉 Resetting main to develop HEAD"
  git checkout main
  git reset --hard develop
  git checkout develop

  echo "👉 Bumping to next minor pre-release on develop..."
  bump_version "minor"
  git push origin develop
  git push origin main

  echo "👉 Creating GitHub release for tag: $tag"
  git checkout main
  gh release create "$tag" --generate-notes
  git checkout develop
}

function release_major {
  echo "🎉 Releasing new major version..."
  sync_branches
  release "major"
}

function release_features {
  echo "🎉 Releasing new minor version (new features)..."
  sync_branches
  release "minor"
}

function release_fixes {
  echo "🎉 Releasing new patch version (only fixes)..."
  sync_branches
  release "patch"
}

case "$1" in
  major)    release_major ;;
  features) release_features ;;
  fixes)    release_fixes ;;
  *)
    echo "Usage: $0 {major|features|fixes}"
    exit 1
    ;;
esac
