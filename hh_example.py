import pandapipes_to_dymola as p_to_d
import writeController as wC
from pandapipes.control.run_control import run_control
import os
from pandapipes.io.file_io import from_json

filename = "example"
Data_filename = "example_loadprofiles_kg_per_s"
net = from_json(os.path.join("network_files", filename+".json"))
time_steps = wC.controller(net, Data_filename)
run_control(net)
p_to_d.CDB_to_Modelica(net, filename, Data_filename, xy_scale=5000)
