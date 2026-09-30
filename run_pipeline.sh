#!/bin/bash
set -e
source venv/bin/activate
pip install peft trl accelerate scikit-learn
echo "==================================="
echo "1. GENERATING TEACHER DATASET"
echo "==================================="
python src/data_generation_laya.py
echo "==================================="
echo "2. FINE-TUNING SLM (QWEN 0.5B)"
echo "==================================="
python src/train.py
echo "==================================="
echo "3. RUNNING EVALUATIONS"
echo "==================================="
python src/eval.py
echo "PIPELINE COMPLETE!"
