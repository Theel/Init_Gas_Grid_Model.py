from pathlib import Path
import os
import csv
import pandapipes as pp
from scipy.io import matlab
from pandapipes.io.file_io import from_json
import pandas as pd
from pandapipes.control.run_control import run_control
import pandapower.control as control
import pandapipes.networks as networks

from pandapower.timeseries import DFData
from pandapower.timeseries import OutputWriter
from pandapipes.timeseries import run_timeseries

def controller(net, filename, Data_filename , directory="files" ,idexless_modelName="sink_at_",step_range=138):
    df = pd.read_csv(directory + "/" + Data_filename+".csv")
    if idexless_modelName=="sink_at_":
        i = 0
        for (columnName, columnData) in df.items():
            if i > net.sink.index[-1]:
                break
            if columnName != 'Datetime':
                Data=pd.DataFrame(columnData)
                corretDataForm=DFData(Data)
                globals()[f"contoler{columnName}"] = control.ConstControl(net, element="sink", variable='mdot_kg_per_s',
                                                        element_index=net.sink.index.values[i], data_source=corretDataForm,
                                                        profile_name=net.sink.index.values[i].astype(str))
                i+=1


        #time_steps = range(columnData.size)
        time_steps = range(step_range)
        log_variables = [('res_junction', 'p_bar'),
                         ('res_pipe', 'p_from_bar'), ('res_pipe', 'p_to_bar'), ('res_pipe', 'v_mean_m_per_s'),
                         ('res_pipe', 'mdot_from_kg_per_s'), ('res_pipe', 'reynolds'), ('res_pipe', 'lambda'),
                         ('res_sink', 'mdot_kg_per_s'),
                         ('res_ext_grid', 'mdot_kg_per_s')]

    if idexless_modelName=="heat_exchanger_":
        i = 0
        for (columnName, columnData) in df.items():
            if i > net.heat_exchanger.index[-1]:
                break
            if columnName != 'Datetime':
                Data = pd.DataFrame(columnData)
                corretDataForm = DFData(Data)
                globals()[f"contoler{columnName}"] = control.ConstControl(net, element="heat_exchanger", variable='qext_w',
                                                                          element_index=net.heat_exchanger.index.values[i],
                                                                          data_source=corretDataForm,
                                                                          profile_name=net.heat_exchanger.index.values[i].astype(
                                                                              str))
                i += 1

        # time_steps = range(columnData.size)
        time_steps = range(step_range)
        log_variables = [('res_junction', 'p_bar'),
                         ('res_pipe', 'p_from_bar'), ('res_pipe', 'p_to_bar'), ('res_pipe', 'v_mean_m_per_s'),('res_pipe', 'mdot_from_kg_per_s'),
                         ('res_pipe', 'reynolds'), ('res_pipe', 'lambda'), ('res_pipe', 't_from_k'), ('res_pipe', 't_to_k'),
                         ('heat_exchanger', 'mdot_to_kg_per_s'), ('heat_exchanger', 'p_from_bar'), ('heat_exchanger', 'p_to_bar'),
                         ('heat_exchanger', 't_from_k'), ('heat_exchanger', 't_to_k'),
                         ('res_circ_pump_mass', 'mdot_flow_kg_per_s'), ('res_circ_pump_mass', 'deltap_bar')]

    if os.path.exists(f'results/{filename}_results'):
        output_path = f'results/{filename}_results'
    else:
        os.makedirs(f'results/{filename}_results')
        output_path = f'results/{filename}_results'
    ow = OutputWriter(net, time_steps, output_path=output_path, output_file_type='.csv', log_variables=log_variables)

    run_timeseries(net, time_steps, continue_on_divergence=True)



    return(time_steps)

def table_converter(Data_filename, directory="files"):
    df = pd.read_csv(directory + "/" + Data_filename + ".csv")

    dym_filename = fr'{str(Path.cwd())}\files\{Data_filename}_dym.txt'
    f = open("files" + "/" + Data_filename + "_dym.txt", 'w')

    a = 0
    for (columnName, columnData) in df.items():
        if columnName != 'Datetime':
            Data = pd.DataFrame(columnData)
            a += 1
            print(a)
            f.write(f'#{a}\n' # Dymola kann fängt an bei 1 nicht 0
                    f'double tab{a}({Data.shape[0]-1},{Data.shape[1]+1})\n')

            for i in range(Data.shape[0]):
                f.write(f'{Data.index[i]},{Data.values[i][0]}\n')

    f.close()
    return (dym_filename.replace('\\', '/'))

def controll_model(net,model_name="pandapipes_model", Data_filename="simple_time_series_example_sink_profiles", directory="files" ):

    if os.path.exists(f'Models/{model_name}'):
        output_path = f'Models/{model_name}'
    else:
        os.makedirs(f'Models/{model_name}')
        output_path = f'Models/{model_name}'

    f = open(output_path + "/" + model_name + "_control_data.mo", 'w')
    f.write(f'model {model_name}_control_data "{"This model was automatically generated"}"\n')
    f.write(f'import Modelica.Units.SI;\n')
    f.write(f'extends Modelica.Blocks.Interfaces.MO(final nout = {len(net.controller)});\n')
    f.write(f'parameter SI.Time startTime=200;\n')
    f.write(f'parameter SI.Time timeScale=900;\n')
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
        tab_filename = "tab" + str(i+1)
        f.write(f'Modelica.Blocks.Sources.CombiTimeTable {controller[i]}{i}(\n'
                f'tableOnFile=true,\n'
                f'tableName="{tab_filename}",\n'
                f'fileName="{file_path}",\n'
                f'extrapolation=extrapolation,\n'
                f'timeScale=timeScale,\n'
                f'startTime=startTime)\t'
                f'annotation (Placement(transformation(\n'
                f'extent={{{{{-10},{-10}}},{{{10},{10}}} }},\n'
                f'origin={{ {placement_x} ,{placement_y} }})));\n')
        #f.write(f'Modelica.Blocks.Interfaces.RealOutput y{i}\t'
        #        f'annotation (Placement(transformation(\n'
        #        f'extent={{{{{-10},{-10}}},{{{10},{10}}} }},\n'
        #        f'origin={{ {placement_x+20} ,{placement_y} }})));\n')
    f.write("\n\nequation\n\n")
    for i, row in net.controller.iterrows():
        f.write(f'connect({controller[i]}{i}.y[1], y[{i+1}]);\n')
    f.write(f'annotation ( Icon(\n'
            f'coordinateSystem(preserveAspectRatio=true,\n'
            f'  extent={{{{-100.0,-100.0}},{{100.0,100.0}}}}),\n'
            f'  graphics={{ \n'
            f'Polygon(lineColor={{192,192,192}},\n'
            f'  fillColor={{192,192,192}},\n'
            f'  fillPattern=FillPattern.Solid,\n'
            f'  points={{{{-80.0,90.0}},{{-88.0,68.0}},{{-72.0,68.0}},{{-80.0,90.0}} }}),\n'
            f'Line(points={{{{-80.0,68.0}},{{-80.0,-80.0}}}},\n'
            f'  color={{192,192,192}}),\n'
            f'Line(points={{{{-90.0,-70.0}},{{82.0,-70.0}}}},\n'
            f'  color={{192,192,192}}),\n'
            f'Polygon(lineColor={{192,192,192}},\n'
            f'  fillColor={{192,192,192}},\n'
            f'  fillPattern=FillPattern.Solid,\n'
            f'  points={{{{90.0,-70.0}},{{68.0,-62.0}},{{68.0,-78.0}},{{90.0,-70.0}}}}),\n'
            f'Rectangle(lineColor={{255,255,255}},\n'
            f'  fillColor={{255,215,136}},\n'
            f'  fillPattern=FillPattern.Solid,\n'
            f'  extent={{{{-48.0,-50.0}},{{2.0,70.0}}}}),\n'
            f'Line(points={{{{-48.0,-50.0}},{{-48.0,70.0}},{{52.0,70.0}},{{52.0,-50.0}},{{-48.0,-50.0}},{{-48.0,-20.0}},{{52.0,-20.0}},{{52.0,10.0}},{{-48.0,10.0}},{{-48.0,40.0}},{{52.0,40.0}},{{52.0,70.0}},{{2.0,70.0}},{{2.0,-51.0}}}})}}));')
    f.write(f'\n end {model_name}_control_data;')
    return controller

def find_furthestConsumer(net):
    list_list = []
    total_massflow = sum(net.circ_pump_mass['mdot_flow_kg_per_s'])
    for i, row in net.circ_pump_mass.iterrows():
        geodata_producer = net.junction_geodata.loc[
            net.circ_pump_mass['flow_junction'].loc[net.circ_pump_mass.index[i]]]
        list = []
        m_flow_producer = net.circ_pump_mass['mdot_flow_kg_per_s'].loc[net.circ_pump_mass.index[i]]
        for j, row in net.heat_exchanger.iterrows():
            geodata_consumer = net.junction_geodata.loc[
                net.heat_exchanger['from_junction'].loc[net.heat_exchanger.index[j]]]
            distance = ((geodata_consumer.x - geodata_producer.x) ** 2 +
                        (geodata_consumer.y - geodata_producer.y) ** 2) * m_flow_producer / total_massflow
            list.append(distance)
        list_list.append(list)
    a = np.sum(list_list, axis=0).tolist()
    return(a.index(max(a)))

