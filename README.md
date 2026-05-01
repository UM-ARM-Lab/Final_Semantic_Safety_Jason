# Final Semantic Safety Jason

This repository implements a semantic safety prompting pipeline for Vision-Language-Action models, with an OpenVLA integration example.

The goal of this project is to augment OpenVLA-style robot policies with task-conditioned semantic reasoning. Given a bird’s-eye-view image of the environment and a natural-language task description, the pipeline generates a structured semantic map and rewrites the task prompt with additional semantic safety constraints before it is passed to OpenVLA.

## What is Implemented

This project includes:

1. A semantic map generation pipeline
2. A task-conditioned OpenVLA prompt rewriting module
3. A standalone test/demo script
4. An OpenVLA integration file showing where the prompt is modified during evaluation

Main files:

pipeline/semantic_safety_pipeline.py

First we need to set up OpenVLA:

cd ~/Documents
git clone https://github.com/openvla/openvla.git
cd openvla
pip install -e .

Now we need to set up Libero:

cd ~/Documents
git clone https://github.com/Lifelong-Robot-Learning/LIBERO.git
cd LIBERO
pip install -e .

Now we need to set up some python paths, there are some places where it is hard coded here so you may need to change that:
export PYTHONPATH= "your path"

PIP install these dependencies:

openai
requests
numpy
matplotlib
pillow
torch
transformers
tensorflow

set your API KEY here: export OPENAI_API_KEY="your_api_key_here"

your demo outputs should be something like this:
/home/jasonzou/Documents/openvla/experiments/env_images/libero_spatial_temp_task0_birdview.png
/home/jasonzou/Documents/openvla/experiments/env_images/libero_spatial_temp_task0_task.txt

They can be run like this:
cd /home/jasonzou/Documents/Final_Semantic_Safety
python scripts/test_pipeline.py

or

cd ~/Documents/openvla

PYTHONPATH=~/Documents/LIBERO:$PYTHONPATH \
python experiments/robot/libero/run_libero_eval.py \
  --model_family openvla \
  --pretrained_checkpoint openvla/openvla-7b-finetuned-libero-spatial \
  --task_suite_name libero_spatial \
  --center_crop True
