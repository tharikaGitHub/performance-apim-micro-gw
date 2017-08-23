#!/usr/bin/env python3.6
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
# Create charts from the summary.csv file
# ----------------------------------------------------------------------------
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

sns.set_style("darkgrid")

df = pd.read_csv('summary.csv')
# Filter errors
df=df.loc[df['Error Count'] < 100]
unique_sleep_times=df['Sleep Time (ms)'].unique()
unique_message_sizes=df['Message Size (Bytes)'].unique()

def save_line_chart(chart, column, sleep_time, title):
    print("Creating " + chart + " chart for " + str(sleep_time) + "ms backend delay")
    fig, ax = plt.subplots()
    fig.set_size_inches(8, 6)
    # # Make sure all charts have the same max limit and there is enough space for legend
    # max_limit=(int(df[column].max() / 1000) + 2) * 1000
    sns_plot = sns.pointplot(x="Concurrent Users", y=column, hue="Message Size (Bytes)", data=df.loc[df['Sleep Time (ms)'] == sleep_time], ci=None, dodge=True)
    plt.suptitle(title)
    # sns_plot.set_ylim(0, max_limit)
    plt.legend(loc=2, frameon=True, title="Message Size in Bytes")
    plt.savefig(chart + "_" + str(sleep_time) + "ms.png")
    plt.clf()
    plt.close(fig)

def save_multi_columns_categorical_charts(chart, sleep_time, columns, y, hue, title):
    print("Creating " + chart + " charts for " + str(sleep_time) + "ms backend delay")
    fig, ax = plt.subplots()
    fig.set_size_inches(8, 6)
    df_results = df.loc[df['Sleep Time (ms)'] == sleep_time]
    all_columns=['Message Size (Bytes)','Concurrent Users']
    all_columns.extend(columns)
    df_results=df_results[all_columns]
    df_results = df_results.set_index(['Message Size (Bytes)', 'Concurrent Users']).stack().reset_index().rename(columns={'level_2': hue, 0: y})
    sns_plot = sns.factorplot(x="Concurrent Users", y=y,
        hue=hue, col="Message Size (Bytes)",
        data=df_results, kind="point",
        size=6, aspect=1, col_wrap=2 ,legend=False);
    plt.suptitle(title)
    plt.legend(frameon=True)
    plt.savefig(chart + "_" + str(sleep_time) + "ms.png")
    plt.clf()
    plt.close(fig)

def save_gc_categorical_charts(chart, sleep_time, title):
    print("Creating " + chart + " charts for " + str(sleep_time) + "ms backend delay")
    fig, ax = plt.subplots()
    fig.set_size_inches(8, 6)
    df_results = df.loc[df['Sleep Time (ms)'] == sleep_time]
    df_results=df_results[['Message Size (Bytes)','Concurrent Users','API Manager GC Throughput (%)']]
    factorgrid = sns.factorplot(x="Concurrent Users", y="API Manager GC Throughput (%)",
        col="Message Size (Bytes)",
        data=df_results, kind="point",
        size=6, aspect=1, col_wrap=2 ,legend=False);
    factorgrid.set(ylim=(50, 100))
    plt.suptitle(title)
    plt.savefig(chart + "_" + str(sleep_time) + "ms.png")
    plt.clf()
    plt.close(fig)

def save_bar_chart(message_size, sleep_time, title):
    print("Creating response time summmary chart for " + str(message_size) + "B message size with " + str(sleep_time) + "ms backend delay")
    fig, ax = plt.subplots()
    fig.set_size_inches(8, 6)
    df_results = df.loc[(df['Message Size (Bytes)'] == message_size) & (df['Sleep Time (ms)'] == sleep_time)]
    df_results=df_results[['Message Size (Bytes)','Concurrent Users','Min (ms)','90th Percentile (ms)','95th Percentile (ms)','99th Percentile (ms)','Max (ms)']]
    df_results = df_results.set_index(['Message Size (Bytes)', 'Concurrent Users']).stack().reset_index().rename(columns={'level_2': 'Summary', 0: 'Response Time'})
    sns_plot = sns.barplot(x='Concurrent Users', y='Response Time', hue='Summary', data=df_results, ci=None)
    plt.suptitle(title)
    plt.legend(loc=2, frameon=True, title="Response Time Summary")
    plt.savefig("response_time_summary_" + str(message_size) + "B_" + str(sleep_time) + "ms.png")
    plt.clf()
    plt.close(fig)

for sleep_time in unique_sleep_times:
    save_line_chart("thrpt", "Throughput", sleep_time, "Throughput (Requests/sec) vs Concurrent Users for " + str(sleep_time) + "ms backend delay")
    save_line_chart("avgt", "Average (ms)", sleep_time, "Average Response Time (ms) vs Concurrent Users for " + str(sleep_time) + "ms backend delay")
    save_multi_columns_categorical_charts("loadavg", sleep_time, ['API Manager Load Average - Last 1 minute','API Manager Load Average - Last 5 minutes','API Manager Load Average - Last 15 minutes'],
        "Load Average", "API Manager", "Load Average with " + str(sleep_time) + "ms backend delay");
    save_multi_columns_categorical_charts("network", sleep_time, ['Received (KB/sec)', 'Sent (KB/sec)'],
        "Network Throughput (KB/sec)", "Network", "Network Throughput with " + str(sleep_time) + "ms backend delay");
    save_gc_categorical_charts("gc", sleep_time, "GC Throughput with " + str(sleep_time) + "ms backend delay")
    for message_size in unique_message_sizes:
        save_bar_chart(message_size, sleep_time, "Response Time Summary for " + str(message_size) + "B message size with " + str(sleep_time) + "ms backend delay")

print("Done")