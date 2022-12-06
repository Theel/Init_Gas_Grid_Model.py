import os
from pandapipes.io.file_io import from_json
import pandapipes.plotting as plot
import pandapipes_to_dymola as p_to_d
filename = "hh_gas.json"

net = from_json(os.path.join("network_files", filename))
#plot.simple_plot(net, pipe_width=2.0, junction_size=1.0, plot_sinks=True, plot_sources=True, sink_size=1.0, source_size=1.0, show_plot=True)

p_to_d.CDB_to_Modelica(net, modelName="hh_gas", xy_scale=5000)

