import pandapipes_to_dymola as p_to_d
import writeController as wC
import pandapipes.plotting as plot
from pandapipes.control.run_control import run_control
import os
from pandapipes.io.file_io import from_json

filename = "example"
Data_filename = "example_loadprofiles_kg_per_s"
net = from_json(os.path.join("network_files", filename+".json"))
plot.simple_plot(net, pipe_width=2.0, junction_size=1.0, plot_sinks=True, plot_sources=True, sink_size=1.0, source_size=1.0, show_plot=True)
time_steps = wC.controller(net, filename, Data_filename)
run_control(net)
p_to_d.CDB_to_Modelica(net, filename, Data_filename, xy_scale=5000)
print('Hallo')