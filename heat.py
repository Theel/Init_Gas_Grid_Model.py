import pandapipes_to_dymola as p_to_d
import writeController as wC
import pandapipes.plotting as plot
from pandapipes.control.run_control import run_control
import os
from pandapipes.io.file_io import from_json

filename = "heat"
#Data_filename = "example_loadprofiles_kg_per_s"
net = from_json(os.path.join("network_files", filename+".json"))
#time_steps = wC.controller(net, filename, Data_filename)
#run_control(net)
plot.simple_plot(net, junction_size=0.1, heat_exchanger_size=0.2, pump_size=0.4)
p_to_d.CDB_to_Modelica(net, filename, xy_scale=5000)
print('Hallo')