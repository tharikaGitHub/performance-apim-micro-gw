#!/bin/bash
# Copyright 2017 WSO2 Inc. (http://wso2.org)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# ----------------------------------------------------------------------------
# Setup API Manager
# ----------------------------------------------------------------------------

export PATH=$JMETER_HOME/bin:$PATH

apim_host=$1
netty_host=$2

mkdir -p logs

echoMessage() {
    echo "-----------------------------------------------------------"
    echo "$1"
    echo "-----------------------------------------------------------"
}

waitForEnter() {
    read -p "Press enter to continue"
}

echoMessage "Importing Users"
jmeter.sh -n -t import-users.jmx -Jhost=$apim_host -l logs/import-users.jtl
waitForEnter

echoMessage "Creating Echo API"
jmeter.sh -n -t create-api.jmx -Jhost=$apim_host -Japiname="echo" -Japidesc="Echo API" \
    -Jproduction_url="http://${netty_host}:8688/" -l logs/create-echo-api.jtl
waitForEnter

echoMessage "Creating Mediation API"
jmeter.sh -n -t create-api.jmx -Jhost=$apim_host -Japiname="mediation" -Japidesc="Mediation API" \
    -Jproduction_url="http://${netty_host}:8688/" -Juploadseq="true" -l logs/create-mediation-api.jtl
waitForEnter

echoMessage "Subscribing to Echo API and Generating Tokens"
jmeter.sh -n -t generate-tokens.jmx -Jhost=$apim_host -Japiname="echo" -l logs/echo-generate-tokens.jtl
waitForEnter

echoMessage "Subscribing to Mediation API"
jmeter.sh -n -t generate-tokens.jmx -Jhost=$apim_host -Japiname="mediation" -l logs/mediation-generate-tokens.jtl

