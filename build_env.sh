#!/bin/bash
echo $0: Creating virtual environment
virtualenv --prompt="<myenv>" ./env

mkdir ./logs
mkdir ./logs/term
mkdir ./archiv
mkdir ./pids
mkdir ./db
mkdir ./tmp
mkdir ./tmp/excel

cp gunicorn.conf.py_distr gunicorn.conf.py
cp api/configs/general.py_distr api/configs/general.py
cp api/configs/payment.py_distr api/configs/payment.py
cp api/configs/smsru.py_distr api/configs/smsru.py
cp api/configs/soc_config.py_distr api/configs/soc_config.py

echo $0: Installing dependencies
source ./env/bin/activate
export PIP_REQUIRE_VIRTUALENV=true
./env/bin/pip install --requirement=./requirements.txt --log=./logs/build_pip_packages.log

echo $0: Making virtual environment relocatable
virtualenv --relocatable ./env

echo $0: Creating virtual environment finished.