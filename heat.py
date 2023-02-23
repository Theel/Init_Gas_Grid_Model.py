import pandapipes_to_dymola as p_to_d
import writeController as wC
import pandapipes.plotting as plot
import pandapipes as pp
import pandas as pd
import numpy as np
import os

from utils import create_output_writers
from pandapower.control import ConstControl
from pandapower.timeseries import DFData
from control_central_heating import ControlCentralHeat
from pandapipes.control.run_control import run_control
from pandapipes.io.file_io import from_json
from pandapipes.timeseries import run_timeseries


filename = "heat_1"
#Data_filename = "example_loadprofiles_kg_per_s"
net = from_json(os.path.join("network_files", filename+".json"))
#time_steps = wC.controller(net, filename, Data_filename)
#net.circ_pump_mass.type[0] = 'pt'
#net.circ_pump_mass.type[1] = 'pt'
#ControlCentralHeat(net, 0, None, 'circ_pump_mass')
#plot.simple_plot(net, junction_size=0.1, heat_exchanger_size=0.2, pump_size=0.4)
#pp.pipeflow(net)
componentList = []
for i in range(len(net.component_list)):
    componentList.append(net.component_list[i].__name__)

n_time_steps = 365*24
demand_w = 20000*np.random.rand(n_time_steps,18)
heat_df = pd.DataFrame(data=demand_w)
ds_heat = DFData(heat_df)

const_sink_heat = ConstControl(net, element='heat_exchanger', variable='qext_w', element_index=net.heat_exchanger.index.values, data_source=ds_heat, profile_name=heat_df.columns)

##

df = pd.read_csv("files/Heat/UndergroundTemperature_Duesseldorf_1m_2017.txt", sep=';', engine='python')
soil_temp_celsius = df.T_in_K.to_numpy()
print(soil_temp_celsius)
number_pipes = net.pipe.shape[0]
soil_temp_pipes = np.tile(soil_temp_celsius,(number_pipes,1)).transpose()
df_soil_temp = pd.DataFrame(data=soil_temp_pipes)
ds_soil_temp = DFData(df_soil_temp)
ConstControl(net, element='pipe', variable='text_k', element_index=net.pipe.index.values, data_source=ds_soil_temp, profile_name=df_soil_temp.columns)

##
if "CirculationPumpPressure" in componentList:
    mass_flow_kg_per_s = 4
    net.circ_pump_pressure.mdot_flow_kg_per_s = [mass_flow_kg_per_s for i in range(net.circ_pump_pressure.shape[0])]
    model = 'circ_pump_pressure'
if "CirculationPumpMass" in componentList:
    mass_flow_kg_per_s = 4
    net.circ_pump_mass.mdot_flow_kg_per_s = [mass_flow_kg_per_s for i in range(net.circ_pump_mass.shape[0])]
    model = 'circ_pump_mass'

##

df = pd.read_csv("files/Heat/Temperature_Hamburg_3600s_TMY.txt", sep='\t', engine='python')
temperatures = df.T_in_Grad

a = -1
b = 90
tk_slack_numpy = a * temperatures.to_numpy() + b + 273.15
tk_slack_with_bounds = np.clip(tk_slack_numpy,273.15+70,273.15+120)

const_producer_idx = [0,1]
temp_profile_np = tk_slack_numpy.reshape((tk_slack_numpy.shape[0],))
slack_temp_np = np.tile(temp_profile_np, (len(const_producer_idx), 1)).transpose()
df_slack_temp = pd.DataFrame(data=slack_temp_np)
ds_temp = DFData(df_slack_temp)
ConstControl(net, element=model, variable='t_flow_k', element_index=const_producer_idx, data_source=ds_temp, profile_name=df_slack_temp.columns)

##

heat_gen_idx = 2
crit_eu_idx = 7
ControlCentralHeat(heat=net, element_index_heat=heat_gen_idx, critical_enduser_index=crit_eu_idx, element_type_heat=model)

ows = create_output_writers(net, n_time_steps)

run_timeseries(net=net, time_steps=n_time_steps, output_writers=ows, mode='all', continue_on_divergence=True)
p_to_d.CDB_to_Modelica(net, filename, xy_scale=1)
