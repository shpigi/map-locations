#!/bin/bash

# Git wrapper script that requires confirmation for adding new files and pushing
# Usage: ./scripts/git-safe.sh <git-command> [args]

set -e

case "$1" in
    "add")
        # Check if any new files are being added
        new_files=$(git status --porcelain | grep "^??" | cut -c4-)
        if [ -n "$new_files" ]; then
            echo "⚠️  New files detected:"
            echo "$new_files"
            echo ""
            echo "Add these new files to git? (y/N)"
            read -r response
            if [[ ! "$response" =~ ^[Yy]$ ]]; then
                echo "❌ Aborted adding new files"
                exit 1
            fi
        fi
        git add "${@:2}"
        ;;
    "push")
        echo "🚀 About to push changes to remote repository"
        echo "Continue? (y/N)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            echo "❌ Aborted push"
            exit 1
        fi
        git push "${@:2}"
        ;;
    *)
        # For all other git commands, just pass through
        git "$@"
        ;;
esac
