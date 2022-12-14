from pathlib import Path
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

def table_converter(filename, directory="files"):
    df = pd.read_csv(directory + "/" + filename + ".csv")

    dym_filename = fr'{str(Path.cwd())}\files\{filename}_dym.txt'
    f = open("files" + "/" + filename + "_dym.txt", 'w')

    a = 0
    for (columnName, columnData) in df.items():
        if columnName != 'Datetime':
            Data = pd.DataFrame(columnData)
            a += 1
            print(a)
            f.write(f'#{a}\n'
                    f'double tab{a}({Data.shape[0]-1},{Data.shape[1]+1})\n')

            for i in range(Data.shape[0]):
                f.write(f'{Data.index[i]},{Data.values[i][0]}\n')

    f.close()
    return (dym_filename.replace('\\', '/'))

def controll_model(net,c_model_name="pandapipes_model", Data_filename="simple_time_series_example_sink_profiles", directory="files" ):
    f = open("Models/" + c_model_name + "_control_data.mo", 'w')
    f.write(f'model {c_model_name}_control_data "{"This model was automatically generated"}"\n')
    f.write(f'import Modelica.Units.SI;\n')
    f.write(f'parameter SI.Time startTime=200;\n')
    f.write(f'parameter Modelica.Blocks.Types.Extrapolation extrapolation=Modelica.Blocks.Types.Extrapolation.HoldLastPoint;\n')


    file_path = table_converter(Data_filename, directory)
    controller = []
    x = 0
    c = 0
    for i, row in net.controller.iterrows():
        if i % 10 == 0:
            x_T = -90 + 40*x
            y_T = 90
            x +=1
            c = 0
        placement_x = x_T
        placement_y = y_T - 26*c
        c += 1
        controller.append(net.controller.object.values[i].element)
        tab_filename = "tab" + str(i + 1)
        f.write(f'Modelica.Blocks.Sources.CombiTimeTable {controller[i]}{i}(\n'
                f'tableOnFile=true,\n'
                f'tableName="{tab_filename}",\n'
                f'fileName="{file_path}",\n'
                f'extrapolation=extrapolation,\n'
                f'startTime=startTime)\t'
                f'annotation (Placement(transformation(\n'
                f'extent={{{{{-10},{-10}}},{{{10},{10}}} }},\n'
                f'origin={{ {placement_x} ,{placement_y} }})));\n')
        f.write(f'Modelica.Blocks.Interfaces.RealOutput y{i}\t'
                f'annotation (Placement(transformation(\n'
                f'extent={{{{{-10},{-10}}},{{{10},{10}}} }},\n'
                f'origin={{ {placement_x+20} ,{placement_y} }})));\n')
    f.write("\n\nequation\n\n")
    for i, row in net.controller.iterrows():
        f.write(f'connect({controller[i]}{i}.y[1], y{i});\n')
    f.write(f'\n end {c_model_name}_control_data;')
    return controller
filename = "example"
net = from_json(os.path.join("network_files", filename+".json"))
controller(net, "example_loadprofiles_kg_per_s")
