#!/bin/bash

export GOOGLE_APPLICATION_CREDENTIALS="D:\JHU\courses\20fall\cloud security\qingshan-cloud-security-513ba52b1c96.json"
export GAE_ENV="localdev"

# windows env command
# $env:GOOGLE_APPLICATION_CREDENTIALS="D:\JHU\courses\20fall\cloud security\qingshan-cloud-security-513ba52b1c96.json"

python main.py
