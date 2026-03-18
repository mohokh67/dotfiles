#!/bin/sh
# Snapshot all installed Homebrew packages + casks to home/.Brewfile
BREWFILE="$(dirname "$0")/../home/.Brewfile"
brew bundle dump --force --file "$BREWFILE"
echo "Brewfile updated: $BREWFILE"
