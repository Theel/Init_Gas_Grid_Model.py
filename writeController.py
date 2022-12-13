
import os
import csv
from scipy.io import matlab
from pandapipes.io.file_io import from_json
import pandas as pd
from pandapipes.control.run_control import run_control
import pandapower.control as control
import pandapipes.networks as networks

from pandapower.timeseries import DFData
from pandapower.timeseries import OutputWriter
from pandapipes.timeseries import run_timeseries

def controller(net, filename, directory="files" ,model_type="sink_at_"):
    df = pd.read_csv(directory+ "/" +filename+".csv")
    i = 0
    for (columnName, columnData) in df.items():
        if columnName != 'Datetime':
            Data=pd.DataFrame(columnData)
            corretDataForm=DFData(Data)
            globals()[f"contoler{columnName}"] = control.ConstControl(net, element="sink", variable='mdot_kg_per_s',
                                                    element_index=net.sink.index.values[i], data_source=corretDataForm,
                                                    profile_name=net.sink.index.values[i].astype(str))
            i+=1


    time_steps = range(columnData.size)

    log_variables = [('res_junction', 'p_bar'),
                     ('res_pipe', 'v_mean_m_per_s'), ('res_pipe', 'reynolds'), ('res_pipe', 'lambda'),
                     ('res_sink', 'mdot_kg_per_s'),
                     ('res_ext_grid', 'mdot_kg_per_s')]
    ow = OutputWriter(net, time_steps, output_path='results', output_file_type='.csv', log_variables=log_variables)

    #run_timeseries(net, time_steps)
    return(time_steps)


filename = "example"
net = from_json(os.path.join("network_files", filename+".json"))
controller(net, "example_loadprofiles_kg_per_s")
