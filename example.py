
import pandas as pd
import pandapipes as pp
import pandapipes.plotting as plot
import pandapipes.networks as networks
import os
import pandapower.control as control
from pandapower.timeseries import DFData
from pandapower.timeseries import OutputWriter
from pandapipes.timeseries import run_timeseries

#Parameters:
#method (str, default "nikuradse") – Which results should be loaded: nikuradse or prandtl-colebrook
#Returns:
#net - STANET network converted to a pandapipes network
#Return type:
#pandapipesNet

def pipe_square_high(method="n"):
    net = networks.simple_gas_networks.gas_meshed_square(method=method)
    pp.pipeflow(net)
    return net

def meshed_delta():
    net = networks.simple_gas_networks.gas_meshed_delta()
    #pp.pipeflow(net)
    return net

def pipe_square_flat(fluid="lgas", p_junction=1.05, tfluid_K=293.15, pipe_d=0.3, pipe_l=1):

    net = pp.create_empty_network(fluid=fluid)

    junction_source = pp.create_junction(net, pn_bar=p_junction, tfluid_k=tfluid_K, name="Junction_ext_grid", geodata=(0, 0))
    junction1 = pp.create_junction(net, pn_bar=p_junction, tfluid_k=tfluid_K, name="Junction1", geodata=(2, 0))
    junction2 = pp.create_junction(net, pn_bar=p_junction, tfluid_k=tfluid_K, name="Junction2", geodata=(4, 0))
    junction3 = pp.create_junction(net, pn_bar=p_junction, tfluid_k=tfluid_K, name="Junction3", geodata=(2, 4))
    junction4 = pp.create_junction(net, pn_bar=p_junction, tfluid_k=tfluid_K, name="Junction4", geodata=(4, 4))
    junction_sink = pp.create_junction(net, pn_bar=p_junction, tfluid_k=tfluid_K, name="Junction_sink", geodata=(6, 0))

    pipe1 = pp.create_pipe_from_parameters(net, from_junction=junction_source, to_junction=junction1, length_km=pipe_l,
                                           diameter_m=pipe_d, name="pipe1")
    pipe2 = pp.create_pipe_from_parameters(net, from_junction=junction1, to_junction=junction2, length_km=pipe_l,
                                           diameter_m=pipe_d, name="pipe2")
    pipe3 = pp.create_pipe_from_parameters(net, from_junction=junction1, to_junction=junction3, length_km=pipe_l,
                                           diameter_m=pipe_d, name="pipe3")
    pipe4 = pp.create_pipe_from_parameters(net, from_junction=junction3, to_junction=junction4, length_km=pipe_l,
                                           diameter_m=pipe_d, name="pipe4")
    pipe5 = pp.create_pipe_from_parameters(net, from_junction=junction4, to_junction=junction2, length_km=pipe_l,
                                           diameter_m=pipe_d, name="pipe5")
    pipe6 = pp.create_pipe_from_parameters(net, from_junction=junction2, to_junction=junction_sink, length_km=pipe_l,
                                           diameter_m=pipe_d, name="pipe6")

    ext_grid = pp.create_ext_grid(net, junction=junction_source, p_bar=p_junction, name="ext_grid", t_k=tfluid_K)
    sink = pp.create_sink(net, junction=junction_sink, mdot_kg_per_s=0.545, name="sink1")
    pp.pipeflow(net)
    return net

def pipe_square_valve(fluid="lgas", p_junction=1.05, tfluid_K=293.15, pipe_d=0.3, pipe_l=1):
    net = pp.create_empty_network(fluid="lgas")

    junction_source = pp.create_junction(net, pn_bar=p_junction, tfluid_k=tfluid_K, name="Junction_source", geodata=(0, 0))
    junction1 = pp.create_junction(net, pn_bar=p_junction, tfluid_k=tfluid_K, name="Junction1", geodata=(0, 2))
    junction2 = pp.create_junction(net, pn_bar=p_junction, tfluid_k=tfluid_K, name="Junction2", geodata=(0, 4))
    junction3 = pp.create_junction(net, pn_bar=p_junction, tfluid_k=tfluid_K, name="Junction3", geodata=(4, 2))
    junction4 = pp.create_junction(net, pn_bar=p_junction, tfluid_k=tfluid_K, name="Junction4", geodata=(4, 4))
    junction5 = pp.create_junction(net, pn_bar=p_junction, tfluid_k=tfluid_K, name="Junction4", geodata=(2, 4))
    junction_sink = pp.create_junction(net, pn_bar=p_junction, tfluid_k=tfluid_K, name="Junction_sink", geodata=(0, 6))

    pipe1 = pp.create_pipe_from_parameters(net, from_junction=junction_source, to_junction=junction1, length_km=pipe_l,
                                           diameter_m=pipe_d, name="pipe1")
    pipe2 = pp.create_pipe_from_parameters(net, from_junction=junction1, to_junction=junction2, length_km=pipe_l,
                                           diameter_m=pipe_d, name="pipe2")
    pipe3 = pp.create_pipe_from_parameters(net, from_junction=junction1, to_junction=junction3, length_km=pipe_l,
                                           diameter_m=pipe_d, name="pipe3")
    pipe4 = pp.create_pipe_from_parameters(net, from_junction=junction3, to_junction=junction4, length_km=pipe_l,
                                           diameter_m=pipe_d, name="pipe4")
    pipe5 = pp.create_pipe_from_parameters(net, from_junction=junction4, to_junction=junction5, length_km=pipe_l,
                                           diameter_m=pipe_d, name="pipe5")
    pipe6 = pp.create_pipe_from_parameters(net, from_junction=junction2, to_junction=junction_sink, length_km=pipe_l,
                                           diameter_m=pipe_d, name="pipe6")

    valve1 = pp.create_valve(net, from_junction=junction5, to_junction=junction2, diameter_m=pipe_d, open=True)

    ext_grid = pp.create_ext_grid(net, junction=junction_source, p_bar=p_junction, name="ext_grid",
                                  t_k=tfluid_K, type="pt")
    sink = pp.create_sink(net, junction=junction_sink, mdot_kg_per_s=0.545, name="sink1")
    pp.pipeflow(net)
    return net

def pipe_square_flat_controller(fluid="lgas", p_junction=1.05, tfluid_K=293.15, pipe_d=0.3, pipe_l=1):
    net = pipe_square_flat(fluid="lgas", p_junction=1.05, tfluid_K=293.15, pipe_d=0.3, pipe_l=1)

    profiles_sink = pd.read_csv(os.path.join('files', 'simple_time_series_example_sink_profiles.csv'), index_col=0)

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
    return(net)

def pipe_square_flat_mod(fluid="lgas", p_junction=16, tfluid_K=293.15):

    net = pp.create_empty_network(fluid=fluid)

    junction0 = pp.create_junction(net, pn_bar=p_junction, tfluid_k=tfluid_K, name="Junction0", geodata=(0, 0))
    junction1 = pp.create_junction(net, pn_bar=p_junction, tfluid_k=tfluid_K, name="Junction1", geodata=(2, 0))
    junction2 = pp.create_junction(net, pn_bar=p_junction, tfluid_k=tfluid_K, name="Junction2", geodata=(4, 0))
    junction3 = pp.create_junction(net, pn_bar=p_junction, tfluid_k=tfluid_K, name="Junction3", geodata=(2, 4))
    junction4 = pp.create_junction(net, pn_bar=p_junction, tfluid_k=tfluid_K, name="Junction4", geodata=(4, 4))
    junction5 = pp.create_junction(net, pn_bar=p_junction, tfluid_k=tfluid_K, name="Junction5", geodata=(6, 0))

    Pipe0 = pp.create_pipe_from_parameters(net, from_junction=junction0, to_junction=junction1, length_km=5,
                                           diameter_m=0.3, name="Pipe0")
    Pipe1 = pp.create_pipe_from_parameters(net, from_junction=junction1, to_junction=junction2, length_km=5,
                                           diameter_m=0.3, name="Pipe1")
    Pipe2 = pp.create_pipe_from_parameters(net, from_junction=junction1, to_junction=junction3, length_km=2,
                                           diameter_m=0.1, name="Pipe2")
    Pipe3 = pp.create_pipe_from_parameters(net, from_junction=junction3, to_junction=junction4, length_km=3,
                                           diameter_m=0.15, name="Pipe3")
    Pipe4 = pp.create_pipe_from_parameters(net, from_junction=junction4, to_junction=junction2, length_km=2,
                                           diameter_m=0.1, name="Pipe4")
    Pipe5 = pp.create_pipe_from_parameters(net, from_junction=junction2, to_junction=junction5, length_km=6,
                                           diameter_m=0.2, name="Pipe5")

    Ext_grid_at_0 = pp.create_ext_grid(net, junction=junction0, p_bar=p_junction, name="external_grid_at_0", t_k=tfluid_K)
    Ext_grid_at_4 = pp.create_ext_grid(net, junction=junction4, p_bar=p_junction, name="external_grid_at_4", t_k=tfluid_K)
    Sink_at_3 = pp.create_sink(net, junction=junction3, mdot_kg_per_s=0.545, name="Sink_at_3")
    Sink_at_5 = pp.create_sink(net, junction=junction5, mdot_kg_per_s=0.545, name="Sink_at_5")
    pp.pipeflow(net)
    return net

def pipe_comparision_model(fluid="lgas", p_junction=16, tfluid_K=293.15):

    net = pp.create_empty_network(fluid=fluid)

    junction0 = pp.create_junction(net, pn_bar=p_junction, tfluid_k=tfluid_K, name="Junction0", geodata=(0, 0))
    junction1 = pp.create_junction(net, pn_bar=p_junction, tfluid_k=tfluid_K, name="Junction1", geodata=(2, 0))


    Pipe0 = pp.create_pipe_from_parameters(net, from_junction=junction0, to_junction=junction1, length_km=5,
                                           diameter_m=0.3, name="Pipe0")

    Ext_grid_at_0 = pp.create_ext_grid(net, junction=junction0, p_bar=p_junction, name="external_grid_at_0", t_k=tfluid_K)
    Sink_at_1 = pp.create_sink(net, junction=junction1, mdot_kg_per_s=0.545, name="Sink_at_1")
    pp.pipeflow(net)

    return net

def pipe_comparision_x_model(fluid="lgas", p_junction=16, tfluid_K=293.15, number_ofPipes=5):

    net = pp.create_empty_network(fluid=fluid)

    junction = []
    Pipe = []

    for i in range(number_ofPipes+1):
        junction.append(pp.create_junction(net, pn_bar=p_junction, tfluid_k=tfluid_K, name=f'Junction{i}', geodata=(i*2, 0)))

    for i in range(number_ofPipes):
        Pipe.append(pp.create_pipe_from_parameters(net, from_junction=junction[i], to_junction=junction[i+1], length_km=5,
                                           diameter_m=0.3, name=f'Pipe{i}'))

    Ext_grid_at_0 = pp.create_ext_grid(net, junction=junction[0], p_bar=p_junction, name="external_grid_at_0", t_k=tfluid_K)

    Sink=[]

    for i in range(number_ofPipes+1):
        if (i+1)%2==0:
            Sink = pp.create_sink(net, junction=junction[i], mdot_kg_per_s=0.545, name=f'Sink_at_{i}')
            pp.pipeflow(net)

    return net