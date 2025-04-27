#!/bin/bash

# 激活conda环境
source $(conda info --base)/etc/profile.d/conda.sh
conda activate MinerU

# 进入项目目录
cd /home/user/yuanjinmin/MinerU/web-ui

# 启动web服务
python app.py 