#!/bin/bash
# Copyright 2019 WSO2 Inc. (http://wso2.org)
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
# Run Performance Tests for WSO2 API Manager Micro Gateway
# ----------------------------------------------------------------------------

# This script will initiate all the Test scenarios

script_dir=$(dirname "$0")
# Execute common script
. $script_dir/perf-test-common.sh

function initialize() {
    export apim_ssh_host=apim
    export apim_host=$(get_ssh_hostname $apim_ssh_host)
    echo "Downloading tokens to $HOME."
    scp $apim_ssh_host:apim/micro-gw/target/jwt-tokens.csv $HOME/

    if [[ $jmeter_servers -gt 1 ]]; then
        for jmeter_ssh_host in ${jmeter_ssh_hosts[@]}; do
            echo "Copying tokens to $jmeter_ssh_host"
            scp $HOME/jwt-tokens.csv $jmeter_ssh_host:
        done
    fi
}
export -f initialize

declare -A test_scenario0=(
    [name]="microgw-passthrough"
    [display_name]="Micro Gateway - Passthrough"
    [description]="A secured API, which directly invokes the backend through Micro Gateway"
    [jmx]="apim-test.jmx"
    [protocol]="https"
    [path]="/echo/1.0.0"
    [port]="9095"
    [use_backend]=true
    [tokens]="$HOME/jwt-tokens.csv"
    [skip]=false
)

function before_execute_test_scenario() {
    local service_path=${scenario[path]}
    local protocol=${scenario[protocol]}
    local port=${scenario[port]}
    local tokens=${scenario[tokens]}

    jmeter_params+=("host=$apim_host" "port=$port" "path=$service_path")
    jmeter_params+=("payload=$HOME/${msize}B.json" "response_size=${msize}B" "protocol=$protocol"
        "tokens=$tokens")
    echo "Starting APIM Micro-GW service"
    ssh $apim_ssh_host "./apim/micro-gw/micro-gw-start.sh -m $heap"
}

function after_execute_test_scenario() {
    write_server_metrics apim $apim_ssh_host org.wso2.carbon.bootstrap.Bootstrap
    download_file $apim_ssh_host micro-gw-echo-mgw/logs/microgateway.log microgateway.log
    download_file $apim_ssh_host micro-gw-echo-mgw/logs/gc.log microgateway_gc.log
}
test_scenarios
