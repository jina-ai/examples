#!/bin/sh
mkdir workspace || true
mkdir workspace/index_workspace || true
python generate_training_data.py
