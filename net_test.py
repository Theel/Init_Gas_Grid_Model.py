import pandapipes as pp
import pandas as pd
import example
import pandapipes.plotting as plot
import geodata as gd
import io
import csv
from pathlib import Path
import os
from pandapipes.io.file_io import from_json
from pandapipes.control.run_control import run_control

filename = 'example'
directory="files"
net = from_json(os.path.join("network_files", filename+".json"))
#plot.simple_plot(net, pipe_width=2.0, junction_size=1.0, plot_sinks=True, plot_sources=True, sink_size=1.0, source_size=1.0, show_plot=True)
df = pd.read_csv(directory+ "/example_loadprofiles_kg_per_s.csv")
i=0
print(net.sink["mdot_kg_per_s"].values[0])
for (columnName, columnData) in df.items():
    if columnName != 'Datetime':
        net.sink["mdot_kg_per_s"].values[i] = columnData[2389]
        i += 1
run_control(net)