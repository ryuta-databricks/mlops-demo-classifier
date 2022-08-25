#!/usr/bin/env bash
# Helper script for ensuring no TODOs for files with the specified suffix, within the specified directory
# Usage: ./no-todos.sh directory suffix
TODOS=$(grep -Rn "TODO" "$1" --include "$2")
if [ -n "$TODOS" ]; then
  echo "Found TODOs in the following $2 files under $1. Please resolve them first before proceeding"
  echo "$TODOS"
  exit 1
fi
