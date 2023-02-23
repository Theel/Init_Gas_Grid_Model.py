import pandas as pd
import os

from scipy.io import matlab

import example
import pandapower.control as control
import pandapipes.plotting as plot
import pandapipes.networks as networks

from pandapower.timeseries import DFData
from pandapower.timeseries import OutputWriter
from pandapipes.timeseries import run_timeseries

net = example.pipe_square_flat(fluid="lgas", p_junction=1.05, tfluid_K=293.15, pipe_d=0.3, pipe_l=1)
plot.simple_plot(net, pipe_width=2.0, junction_size=1.0, plot_sinks=True, plot_sources=True, sink_size=1.0, source_size=1.0, show_plot=True)


#filename = 'square_pipe_flat'
#Data_file = open(filename, 'a')
#Data_file.write(net_flat.pipe.to_string())
#Data_file.write("\n")
#Data_file.write(net_valve.res_pipe.to_string())
#Data_file.write
#Data_file.close()

#filename = 'square_junctions'
#Data_file = open(filename, 'a')
#Data_file.write(net.junction.to_string())
#Data_file.write("\n")
#Data_file.write(net.res_junction.to_string())
#Data_file.close()
#print('ext_grid')
#print(net.ext_grid)
#print(net.res_ext_grid)

#Zeitabhängige Simulation

profiles_sink = pd.read_csv(os.path.join('files', 'simple_time_series_example_sink_profiles.csv'), index_col=0)
print(profiles_sink)
ds_sink = DFData(profiles_sink)
const_sink = control.ConstControl(net, element='sink', variable='mdot_kg_per_s',
                                  element_index=net.sink.index.values, data_source=ds_sink,
                                  profile_name=net.sink.index.values.astype(str))


time_steps = range(10)



log_variables = [('res_junction', 'p_bar'),
                  ('res_pipe', 'v_mean_m_per_s'), ('res_pipe', 'reynolds'), ('res_pipe', 'lambda'),
                  ('res_sink', 'mdot_kg_per_s'),
                  ('res_ext_grid', 'mdot_kg_per_s')]
ow = OutputWriter(net, time_steps, output_path='results', output_file_type='.csv', log_variables=log_variables)



run_timeseries(net, time_steps)


#res_junctions = ow.np_results["res_pipe.v_mean_m_per_s"]
#print(ow.np_results["res_pipe.v_mean_m_per_s"])

#print("pressure:")
#print(ow.np_results["res_junction.p_bar"])
#print("mass flow sink:")
#print(ow.np_results["res_sink.mdot_kg_per_s"])


#object=net.controller.object.values[0].element
#print(object)