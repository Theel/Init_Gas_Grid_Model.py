import pandapipes as pp
import pandas as pd
import pandapipes_to_dymola as p_to_d
import example
import writeController as wC
import pandapipes.plotting as plot
import geodata as gd
import numpy as np
import io
import csv
import re
import collections
import os
import itertools

from pandapower.control import ConstControl
from pandapower.timeseries import DFData
from control_central_heating import ControlCentralHeat
from itertools import chain
from pathlib import Path
from pandapipes.io.file_io import from_json
from pandapipes.control.run_control import run_control


# Data_filename = "Heating_20Households_simulated_angepasst"
# filename = "heat_2"
# net = from_json(os.path.join("network_files", filename+".json"))
# #net.circ_pump_mass.type[0]='pt'
# #net.circ_pump_mass.type[1]='pt'
# #ControlCentralHeat(net, 0, None, 'circ_pump_mass')
# #run_control(net)
# #time_steps = wC.controller(net, filename, Data_filename, idexless_modelName='heat_exchanger_')
# #net = example.pipe_square_flat()
# #plot.simple_plot(net, pipe_width=2.0, junction_size=1.0, plot_sinks=True, plot_sources=True, sink_size=1.0, source_size=1.0, show_plot=True)
# #df = pd.read_csv(directory+ "/example_loadprofiles_kg_per_s.csv")
#
# df = pd.read_csv("files/Heat/Temperature_Hamburg_3600s_TMY.txt", sep='\t', engine='python')
# temperatures = df.T_in_Grad
#
# n_time_steps = 365*24
# demand_w = 20000*np.random.rand(n_time_steps,18)
# heat_df = pd.DataFrame(data=demand_w)
# ds_heat = DFData(heat_df)
#
#
#
#
# #max_steps = heat_df.shape[0]
# #temp_daily = temperatures.resample("1D").mean()
# #new_value = temperatures.tail(1)
# #temp_daily = pd.concat([temperatures,pd.Series(data=new_value.to_numpy(), index=new_value.index)], ignore_index=False)
# a = -1
# b = 90
# tk_slack_numpy = a * temperatures.to_numpy() + b + 273.15
# tk_slack_with_bounds = np.clip(tk_slack_numpy,273.15+70,273.15+120)
# #t_k_slack = pd.DataFrame(data=tk_slack_with_bounds, index=temp_daily.index)
# #t_k_slack = t_k_slack.resample("15T").mean()
# #t_k_slack = t_k_slack.interpolate(method='linear')
# #temp_profile = pd.DataFrame(data=t_k_slack.to_numpy())
# #temp_profile.plot()
#
# const_producer_idx = [0,1]
# temp_profile_np = tk_slack_numpy.reshape((tk_slack_numpy.shape[0],))
# slack_temp_np = np.tile(temp_profile_np,(len(const_producer_idx),1)).transpose()
# df_slack_temp = pd.DataFrame(data=slack_temp_np)
# ds_temp = DFData(df_slack_temp)
# ConstControl(net, element='circ_pump_mass', variable='t_flow_k', element_index=const_producer_idx, data_source=ds_temp, profile_name=df_slack_temp.columns)

filename = "pipe_comparison_1"
Data_filename = "Test_bench\Pipe"
net = example.pipe_comparision_x_model(number_ofPipes=1)

#plot.simple_plot(net, pipe_width=2.0, junction_size=1.0, plot_sinks=True, plot_sources=True, sink_size=1.0, source_size=1.0, show_plot=True)
#time_steps = wC.controller(net, filename, Data_filename)
#run_control(net)
#p_to_d.CDB_to_Modelica(net, filename, Data_filename, xy_scale=50)


