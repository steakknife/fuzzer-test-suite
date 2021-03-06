#!/usr/bin/env python

import sys
import matplotlib.pyplot as plt
from scipy.stats.mstats import gmean

configs = ['baseline', 'simpler']
config_labels = ['Baseline', 'PartiSan']
config_colors = ['green', 'blue', 'yellow']
config_linestyles = ['--', '-', '-.']
benchmarks = ['boringssl-2016-02-12', 'harfbuzz-1.3.2',
'json-2017-02-12', 'lcms-2017-03-21', 'libarchive-2017-01-04', 'libjpeg-turbo-07-2017',
'libpng-1.2.56', 'openssl-1.1.0c', 'openthread-2018-02-27', 'sqlite-2016-11-14',
'woff2-2016-05-06', 'wpantund-2018-02-27']
types = ['coverage', 'features', 'corpus-units', 'corpus-size', 'exec-s', 'rss']
type_labels = ['coverage', 'features', 'corpus units', 'corpus size', 'exec/s', 'rss']
num_files = 10


def compute_data(cfg, bench):
    file_scheme = cfg + '_' + bench + '_'
    files = [open(file_scheme+str(i)+'.csv') for i in range(num_files)]

    # data types -> series
    data = [[] for _ in types]
    deaths = []
    line_no = 0

    while files:
        finished_files = []
        line_no += 1
        # Collect related values across files
        values = [[] for _ in types]
        for f in files:
            line = f.readline()
            if line:
                line_values = line.split()
                assert len(line_values) == len(types)
                for i in range(len(types)):
                    val = int(line_values[i])
                    assert val > 0 or i == 4    # exec/s might be zero which is a problem for geomean
                    val = max(val, 1)
                    values[i].append(val)
            else:
                deaths.append(line_no)
                finished_files.append(f)

        # Remove exhausted files
        for f in finished_files:
            files.remove(f)
            f.close()

        if files:
            gms = [gmean(val) for val in values]
            for i in range(len(types)):
                data[i].append(gms[i])

    return data, deaths


# bench -> config -> (data types -> series, deaths)
all_data = [[compute_data(cfg, bench) for cfg in configs] for bench in benchmarks]

# Individual graph for every metric/benchmark cobmination
for b in range(len(all_data)):
    for t in range(len(types)):
        plt.figure(figsize=(8, 4.5))  # default: (8, 6)
        plt.ylabel(type_labels[t])
        plt.xlabel('minutes')

        for c in range(len(configs)):
            data, deaths = all_data[b][c]
            series = data[t]
            plt.plot(series, label=config_labels[c], linewidth=1.2, linestyle=config_linestyles[c], color=config_colors[c])
            x_lookup_max = len(series) - 1  # Special case for last data point
            deaths_y = [series[min(x, x_lookup_max)] for x in deaths]
            plt.plot(deaths, deaths_y, linestyle='None', marker='x', color='black', markersize=8, markeredgewidth=0.8)

        plt.legend(loc='lower right', shadow=True)
        file_name = benchmarks[b] + '_' + types[t] + '_gmean.pdf'
        plt.savefig(file_name, bbox_inches='tight')
        plt.close()

# Combined graph: exec/s, features
for b in range(len(all_data)):
    fig, axarr = plt.subplots(2, sharex=True)
    # plt.figure(figsize=(8, 4.5))  # default: (8, 6)
    # fig.suptitle(bench)
    axarr[0].set_title(benchmarks[b])
    # axarr[0].ylabel('exec/s')
    # axarr[0].ylabel('coverage')
    # fig.xlabel('fuzz time in minutes')

    comb_types = [4, 1]  # exec/s, features
    for i, t in enumerate(comb_types):
        for c in range(len(configs)):
            data, deaths = all_data[b][c]
            series = data[t]
            axarr[i].plot(series, label=config_labels[c], linewidth=1.2, linestyle=config_linestyles[c], color=config_colors[c])
            x_lookup_max = len(series) - 1  # Special case for last data point
            deaths_y = [series[min(x, x_lookup_max)] for x in deaths]
            axarr[i].plot(deaths, deaths_y, linestyle='None', marker='x', color='black', markersize=8, markeredgewidth=0.8)

    axarr[1].legend(loc='lower right', shadow=True)
    file_name = benchmarks[b] + '_combined.pdf'
    plt.savefig(file_name, bbox_inches='tight')
    plt.close()

# Special graph for paper
sel_bs = [6, 11]  # which benchmarks?
comb_types = [4, 1]  # exec/s, features
fig, axarr = plt.subplots(2, 2, sharex='col', figsize=(10, 5))
# plt.figure(figsize=(8, 4.5))  # default: (8, 6)
# fig.suptitle(bench)
axarr[0, 0].set_title(benchmarks[sel_bs[0]])
axarr[0, 1].set_title(benchmarks[sel_bs[1]])
for sel_b in range(len(sel_bs)):
    for i, t in enumerate(comb_types):
        thick = 0.0
        for c in range(len(configs)):
            data, deaths = all_data[sel_bs[sel_b]][c]
            series = data[t]
            axarr[i, sel_b].yaxis.set_major_locator(plt.MaxNLocator(4))
            axarr[i, sel_b].plot(series, label=config_labels[c], linewidth=1.3+thick, linestyle=config_linestyles[c], color=config_colors[c])
            thick -= 0.2
            deaths = [x for x in deaths if x <= 8*60]   # Filter out timeouts
            x_lookup_max = len(series) - 1  # Special case for last data point
            deaths_y = [series[min(x, x_lookup_max)] for x in deaths]
            axarr[i, sel_b].plot(deaths, deaths_y, linestyle='None', marker='x', color='black', markersize=8, markeredgewidth=0.8)
        axarr[i, 0].set_ylabel(type_labels[t], fontsize=14)
    ticks = [(x+1)*60 for x in range(8)]
    axarr[1, sel_b].xaxis.set_major_locator(ticker.FixedLocator(ticks))
    axarr[1, sel_b].xaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: '%.0f' % (x/60)))  # convert minutes into hours

# Trim the fat
axarr[0, 0].set_ylim([500, 2500])
axarr[1, 0].set_ylim([1800, 2300])
axarr[0, 1].set_ylim([0, 135])
axarr[1, 1].set_ylim([2000, 15000])

fig.subplots_adjust(hspace=0.08)
# axarr[1].legend(loc='lower right', shadow=True)
plt.legend(bbox_to_anchor=(0.5, 0), loc="upper center", bbox_transform=fig.transFigure, ncol=3, labelspacing=0, handletextpad=0)

# Hack to get a common x-axis label
fig.add_subplot(111, frameon=False)
# hide tick and tick label of the big axes
plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
plt.grid(False)
plt.xlabel("Fuzz time in hours", fontsize=14)

file_name = 'special.pdf'
plt.savefig(file_name, bbox_inches='tight')
plt.close()