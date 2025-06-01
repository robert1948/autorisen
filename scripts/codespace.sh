#!/usr/bin/env bash

# Name of your Codespace for Autorisen
CODESPACE_NAME="robert1948-autorisen"  # Replace with your actual Codespace name

# Check the first argument: start or stop
case "$1" in
  start)
    echo "Starting Codespace: $CODESPACE_NAME"
    gh codespace start --codespace "$CODESPACE_NAME"
    ;;
  stop)
    echo "Stopping Codespace: $CODESPACE_NAME"
    gh codespace stop --codespace "$CODESPACE_NAME"
    ;;
  status)
    echo "Current Codespaces:"
    gh codespace list
    ;;
  *)
    echo "Usage: $0 {start|stop|status}"
    exit 1
    ;;
esac
