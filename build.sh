#!/bin/bash
# Build script for Render

echo "Installing Python dependencies..."
pip install --upgrade pip
cd backend
pip install -r requirements.txt
cd ..

echo "Attempting to build FAISS index..."
cd backend
python build_index.py || echo "FAISS index build failed, will use fallback method"
cd ..

echo "Build complete!"
