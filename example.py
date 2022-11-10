

import pandapipes as pp
import pandapipes.plotting as plot
import pandapipes.networks as networks



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
