#!/bin/sh
# Install all packages from ~/.Brewfile (requires dotfiles to be stowed first)
# Usage: sh install.sh [/path/to/Brewfile]
if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew not found. Install from https://brew.sh first."
  exit 1
fi
FILE="${1:-$HOME/.Brewfile}"
if [ ! -f "$FILE" ]; then
  echo "$FILE not found. Run stow first: stow -d ~/dev/dotfiles -t ~ home"
  exit 1
fi
brew bundle install --file="$FILE"
