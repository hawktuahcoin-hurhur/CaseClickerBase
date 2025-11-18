#!/bin/bash

echo "Starting Global Coalition Arms Dealer Game..."
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Starting server..."
python app.py
