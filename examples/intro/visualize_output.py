#!/usr/bin/env python

"""
Visualize output of intro demo.
"""

import concurrent.futures

import numpy as np
import matplotlib as mpl
mpl.use('agg')

import neurokernel.LPU.utils.visualizer as vis
import networkx as nx

nx.readwrite.gexf.GEXF.convert_bool = {'false':False, 'False':False,
                                        'true':True, 'True':True}

def run(out_name):
    V = vis.visualizer()

    # Assumes that generic_lpu_0_input.h5 and generic_lpu_1_input.h5
    # contain the same data:
    V.add_LPU('./data/generic_lpu_0_input.h5', LPU='Sensory')
    V.add_plot({'type': 'waveform', 'ids': [[0]]}, 'input_Sensory')

    for i in [0, 1]:
        G = nx.read_gexf('./data/generic_lpu_%s.gexf.gz' % i)
        neu_pub = sorted([int(n) for n, d in G.nodes_iter(True) \
                          if d['public'] == True])

        V.add_LPU('generic_lpu_%s_%s_output_spike.h5' % (i, out_name),
                  './data/generic_lpu_%s.gexf.gz' % i,
                  'Generic LPU %s' % i)
        V.add_plot({'type': 'raster',
                    'ids': {0: neu_pub},
                    #'yticks': range(1, 1+len(neu_out)),
                    #'yticklabels': range(len(neu_out))
                    },
                    'Generic LPU %s' % i, 'Output')

    V._update_interval = 50
    V.rows = 3
    V.cols = 1
    V.fontsize = 18
    V.out_filename = '%s.avi' % out_name
    V.codec = 'libtheora'
    V.dt = 0.0001
    V.xlim = [0, 1.0]
    V.run()

# Run the visualizations in parallel:
with concurrent.futures.ProcessPoolExecutor() as executor:
    fs_dict = {}
    for out_name in ['un', 'co']:
        res = executor.submit(run, out_name)
        fs_dict[out_name] = res
    concurrent.futures.wait(fs_dict.values())

    # Report any exceptions that may have occurred:
    for k in fs_dict:
        e = fs_dict[k].exception()
        if e:
            print '%s: %s' % (k, e)
