import Init_Gas_Grid_Model as init
import example
import os
import io
import geodata as gd
import Table_converter as Tc
import writeController as wC
from pandapipes.io.file_io import from_json

def write_bComment(f, comment):
    f.write('\n  // ' + '-' * 90 + '\n')
    f.write('  //   ' + comment + '\n')
    f.write('  // ' + '-' * 90 + '\n\n')


def write_sComment(f, comment):
    width = 95 - 5 - 2
    w1 = 4
    remaining = width - len(comment)
    f.write(f'  // {"-" * w1} {comment} {"-" * (remaining - w1)}\n\n')

def CDB_to_Modelica(net,modelName="pandapipes_model", Data_filename = "simple_time_series_example_sink_profiles", xy_scale=40):

    # open model file
    if os.path.exists(f'Models/{modelName}'):
        output_path = f'Models/{modelName}'
    else:
        os.makedirs(f'Models/{modelName}')
        output_path = f'Models/{modelName}'


    f = open(output_path + "/" + modelName + ".mo", 'w')


    f.write(f'model {modelName} "{"This model was automatically generated"}"\n')

    # find net type heat or gas
    if net.fluid.is_gas == True:
        f.write(gas_net(net, modelName, Data_filename, xy_scale))
    elif net.fluid.is_gas == False:
        f.write(heat_net(net, modelName, Data_filename, xy_scale))
    else:
       print("unknown Net")




    f.write(f'\n'
            f'end {modelName};\n')

    f.close()

def gas_net(net,modelName="pandapipes_model", Data_filename = "simple_time_series_example_sink_profiles", xy_scale=40):

    f = io.StringIO()
    # ---------------------------------------------------------------------------
    #   Instances of other Classes
    # ---------------------------------------------------------------------------
    write_bComment(f, 'Instances of other Classes')
    # initation = init.Gasnet_create_init(net, modelName)
    # f.write(f'{initation.getvalue()}\n')

    # ---------------------------------------------------------------------------
    #   Parameter
    # ---------------------------------------------------------------------------

    # write_bComment(f, "Parameter")

    write_sComment(f, "TransiEnt Models (SimCenter and ModelStatistics)")

    # TransiEnt.SimCenter
    f.write(f'inner TransiEnt.SimCenter simCenter(useHomotopy=true, redeclare TransiEnt.Basics.Media.Gases.VLE_VDIWA_CH4 gasModel1)'
            f' annotation (Placement(transformation(extent={{{{-70,80}},{{-50,100}}}})));\n'
            f'parameter TILMedia.VLEFluidTypes.BaseVLEFluid medium = simCenter.gasModel1 "Medium natural gas mixture";\n')

    # Init
    init.create_init(net, modelName=modelName)
    write_sComment(f, "Init")
    f.write(f'{modelName}_Init\n'
            f'init(\n'
            f'medium=simCenter.gasModel1,\n'
            f'N_cv_gasPipe=3,\n'
            f'FrictionInlet=false,\n'
            f'FrictionOutlet=false)'
            f'annotation(Placement(transformation(extent={{{{-100, 80}}, {{-80, 100}}}})));')

    componentList = []
    for i in range(len(net.component_list)):
        componentList.append(net.component_list[i].__name__)

    # Pipes
    if "Pipe" in componentList:

        write_bComment(f, "Pipes")

        for i, row in net.pipe.iterrows():
            pipe_name = net.pipe['name'].loc[net.pipe.index[i]].replace(" ", "")
            pipe_length = net.pipe['length_km'].loc[net.pipe.index[i]]
            pipe_d = net.pipe['diameter_m'].loc[net.pipe.index[i]]
            # pipe_p = net.pipe['diameter_m'].loc[net.pipe.index[i]]*1e5
            p_start_in = net.res_pipe["p_from_bar"].loc[net.pipe.index[i]] * 1e5
            p_start_out = net.res_pipe["p_to_bar"].loc[net.pipe.index[i]] * 1e5
            m_flow_start = abs(net.res_pipe["mdot_from_kg_per_s"].loc[net.pipe.index[i]])
            pipe_T = net.res_pipe['t_from_k'].loc[net.pipe.index[i]]
            # Delta_p_nom = 10000
            # m_flow_nom = 100
            if abs(p_start_in - p_start_out) == 0:
                Delta_p_nom = 1100
                m_flow_nom = 0.5
            else:
                Delta_p_nom = abs(p_start_in - p_start_out)
                m_flow_nom = m_flow_start
            f.write(f'PipeFlow_L4_Advanced {pipe_name}(\n'
                    f'useHomotopy=true,\n'
                    f'medium=medium,\n'
                    f'frictionAtInlet=init.FrictionInlet,\n'
                    f'frictionAtOutlet=init.FrictionOutlet,\n'
                    f'initOption=0,\n'
                    f'N_cv=init.N_cv_gasPipe,\n'
                    f'm_flow_nom={m_flow_nom},\n'
                    f'Delta_p_nom={Delta_p_nom},\n'
                    f'length={pipe_length * 1000},\n'
                    f'diameter_i={pipe_d},\n'
                    # f'p_nom=ones({pipe_name}.N_cv)*{pipe_p},\n'
                    f'xi_start=medium.xi_default,\n'
                    f'h_start=TILMedia.Internals.VLEFluidConfigurations.FullyMixtureCompatible.VLEFluidFunctions.specificEnthalpy_pTxi(medium,{pipe_name}.p_start,{pipe_name}.T_start,{pipe_name}.xi_start),\n'
                    f'T_start=ones({pipe_name}.N_cv)*{pipe_T},\n'
                    f'p_start=linspace(\n'
                    f'  {p_start_in},\n'
                    f'  {p_start_out},\n'
                    f'  {pipe_name}.N_cv),\n'
                    f'm_flow_start=ones({pipe_name}.N_cv + 1)*{m_flow_start})\t'
                    f'{gd.pipes_annotation(net, xy_scale, 1, i)}\n\n')

    write_bComment(f, "Nodes")  #

    # Nodes
    if "Junction" in componentList:
        nodes = gd.find_nodes(net)
        for i, row in nodes.iterrows():
            p_start = net.res_junction["p_bar"].loc[net.pipe.index[i]] * 1e5
            f.write(f'TransiEnt.Components.Gas.VolumesValvesFittings.Fittings.RealGasJunction_L2_nPorts junction{i}(\n'
                    f'initOption=simCenter.initOptionGasPipes,\n'
                    # f'medium=medium,\n'
                    f'p(start={p_start}),\n'
                    f'n_ports={nodes["connections"][i]})\t'
                    f'{gd.node_annotation(net, xy_scale, node_to_from="node_from", node_index=i)}\n')

    # controller externe Daten
    write_sComment(f, 'Controller')

    controller = []
    if net.controller.empty == False:
        controller = wC.controll_model(net, modelName, Data_filename)
        f.write(f'{modelName}_control_data control_data\t'
                f'annotation(Placement(transformation('
                f'extent={{{{-100,54}},{{-80,74}}}})));\n')
    # sink
    if "Sink" in componentList:
        write_sComment(f, 'Consumer')
        for i, row in net.sink.iterrows():
            sink_name = net.sink['name'].loc[net.sink.index[i]].replace(" ", "")
            sink_mdot = net.sink['mdot_kg_per_s'].loc[net.sink.index[i]]
            if 'sink' in controller:  # Anpassen für großes Netz
                control_sink = 'true'
            else:
                control_sink = 'false'

            f.write(f'TransiEnt.Components.Boundaries.Gas.BoundaryRealGas_Txim_flow {sink_name}(\n'
                    f'p_nom=0,\n'
                    # f'medium=medium,\n'
                    f'm_flow_const={sink_mdot},\n'
                    f'variable_m_flow={control_sink})\t'
                    f'{gd.gas_model_annotation(net, "sink", xy_scale, 1, i)}\n\n')

    # ext_grid
    if "ExtGrid" in componentList:
        write_sComment(f, 'Sources')
        for i, row in net.ext_grid.iterrows():
            ext_name = net.ext_grid['name'].loc[net.ext_grid.index[i]].replace(" ", "")
            ext_p = net.ext_grid['p_bar'].loc[net.ext_grid.index[i]] * 1e5
            ext_T = net.ext_grid['t_k'].loc[net.ext_grid.index[i]]
            if {ext_name} in controller:
                control_ext = 'true'
            else:
                control_ext = 'false'
            f.write(f'TransiEnt.Components.Boundaries.Gas.BoundaryRealGas_pTxi {ext_name}(\n'
                    f'p_const={ext_p},\n'
                    f'T_const={ext_T},\n'
                    # f'medium=medium,\n'
                    # f'xi_const=init.{ext_name}.xi,\n'
                    f'variable_p={control_ext},\n'
                    f'variable_T={control_ext},\n'
                    f'variable_xi={control_ext})\t'
                    f'{gd.gas_model_annotation(net, "ext_grid", xy_scale, 1, i)}\n')

    # sources
    if "Source" in componentList:
        for i, row in net.source.iterrows():
            source_name = net.source['name'].loc[net.source.index[i]].replace(" ", "")
            # ext_p = net.source['p_bar'].loc[net.ext_grid.index[i]]
            source_T = net.source['t_k'].loc[net.source.index[i]]
            if {source_name} in controller:
                control_source = 'true'
            else:
                control_source = 'false'
            f.write(f'TransiEnt.Components.Boundaries.Gas.BoundaryRealGas_pTxi {source_name}(\n'
                    # f'p_const={source_p},\n'
                    f'T_const={source_T},\n'
                    # f'medium=medium,\n'
                    # f'xi_const=init.{ext_name}.xi,\n'
                    f'variable_p={control_source},\n'
                    f'variable_T={control_source},\n'
                    f'variable_xi={control_source})\t'
                    f'{gd.gas_model_annotation(net, "source", xy_scale, 1, i)}\n')

    f.write("equation\n\n")

    # Connections
    f.write(f'{gd.connections(net, componentList, xy_scale, "yellow")}')
    for i in range(len(controller)):
        sink_name = net.sink['name'].loc[net.sink.index[i]].replace(" ", "")
        f.write(f'connect(control_data.y[{i + 1}], {sink_name}.m_flow);\n')

    return(f.getvalue())


def heat_net(net, modelName="pandapipes_model", Data_filename = "simple_time_series_example_sink_profiles", xy_scale=40):
    f = io.StringIO()
    # ---------------------------------------------------------------------------
    #   Instances of other Classes
    # ---------------------------------------------------------------------------
    write_bComment(f, 'Instances of other Classes')
    # initation = init.Gasnet_create_init(net, modelName)
    # f.write(f'{initation.getvalue()}\n')

    # ---------------------------------------------------------------------------
    #   Parameter
    # ---------------------------------------------------------------------------

    # write_bComment(f, "Parameter")

    write_sComment(f, "TransiEnt Models (SimCenter and ModelStatistics)")

    # TransiEnt.SimCenter
    f.write(f'inner TransiEnt.SimCenter simCenter(useHomotopy=true, k_H2_fraction=0.6)'
            f' annotation (Placement(transformation(extent={{{{-70,80}},{{-50,100}}}})));\n'
            f'parameter TILMedia.VLEFluidTypes.BaseVLEFluid medium = simCenter.fluid1\n;')

    # Init
    init.create_init(net, modelName=modelName)
    write_sComment(f, "Init")
    f.write(f'{modelName}_Init\n'
            f'init(\n'
            f'medium=simCenter.gasModel1,\n'
            f'N_cv_gasPipe=3,\n'
            f'FrictionInlet=false,\n'
            f'FrictionOutlet=false)'
            f'annotation(Placement(transformation(extent={{{{-100, 80}}, {{-80, 100}}}})));')

    componentList = []
    for i in range(len(net.component_list)):
        componentList.append(net.component_list[i].__name__)

    # Pipes
    if "Pipe" in componentList:

        write_bComment(f, "Pipes")

        for i, row in net.pipe.iterrows():
            pipe_name = net.pipe['name'].loc[net.pipe.index[i]].replace(" ", "")
            pipe_length = net.pipe['length_km'].loc[net.pipe.index[i]]
            pipe_d = net.pipe['diameter_m'].loc[net.pipe.index[i]]
            # pipe_p = net.pipe['diameter_m'].loc[net.pipe.index[i]]*1e5
            p_start_in = net.res_pipe["p_from_bar"].loc[net.pipe.index[i]] * 1e5
            p_start_out = net.res_pipe["p_to_bar"].loc[net.pipe.index[i]] * 1e5
            m_flow_start = abs(net.res_pipe["mdot_from_kg_per_s"].loc[net.pipe.index[i]])
            pipe_T = net.res_pipe['t_from_k'].loc[net.pipe.index[i]]
            # Delta_p_nom = 10000
            # m_flow_nom = 100
            if abs(p_start_in - p_start_out) == 0:
                Delta_p_nom = 1100
                m_flow_nom = 0.5
            else:
                Delta_p_nom = abs(p_start_in - p_start_out)
                m_flow_nom = m_flow_start
            f.write(f'ClaRa.Components.VolumesValvesFittings.Pipes.PipeFlowVLE_L4_Simple {pipe_name}(\n'
                    f'useHomotopy=true,\n'
                    f'medium=medium,\n'
                    f'frictionAtInlet=init.FrictionInlet,\n'
                    f'frictionAtOutlet=init.FrictionOutlet,\n'
                    f'initOption=0,\n'
                    f'N_cv=init.N_cv_gasPipe,\n'
                    f'm_flow_nom={m_flow_nom},\n'
                    f'Delta_p_nom={Delta_p_nom},\n'
                    f'length={pipe_length * 1000},\n'
                    f'diameter_i={pipe_d},\n'
                    # f'p_nom=ones({pipe_name}.N_cv)*{pipe_p},\n'
                    f'xi_start=medium.xi_default,\n'
                    f'h_start=TILMedia.Internals.VLEFluidConfigurations.FullyMixtureCompatible.VLEFluidFunctions.specificEnthalpy_pTxi(medium,{pipe_name}.p_start,{pipe_name}.T_start,{pipe_name}.xi_start),\n'
                    f'T_start=ones({pipe_name}.N_cv)*{pipe_T},\n'
                    f'p_start=linspace(\n'
                    f'  {p_start_in},\n'
                    f'  {p_start_out},\n'
                    f'  {pipe_name}.N_cv),\n'
                    f'm_flow_start=ones({pipe_name}.N_cv + 1)*{m_flow_start})\t'
                    f'{gd.pipes_annotation(net, xy_scale, 1, i)}\n\n')

    write_bComment(f, "Nodes")  #

    # Nodes
    if "Junction" in componentList:
        nodes = gd.find_nodes(net)
        for i, row in nodes.iterrows():
            p_start = net.res_junction["p_bar"].loc[net.pipe.index[i]] * 1e5
            f.write(f'ClaRa.Components.VolumesValvesFittings.Fittings.JoinVLE_L2_Y junction{i}(\n'
                    f'initOption=0,\n'
                    f'volume=1,\n'
                    f'p(start={p_start}),\n'
                    f'n_ports={nodes["connections"][i]})\t'
                    f'{gd.node_annotation(net, xy_scale, node_to_from="node_from", node_index=i)}\n')

    # controller externe Daten
    write_sComment(f, 'Controller')

    controller = []
    if net.controller.empty == False:
        controller = wC.controll_model(net, modelName, Data_filename)
        f.write(f'{modelName}_control_data control_data\t'
                f'annotation(Placement(transformation('
                f'extent={{{{-98,58}},{{-78,78}}}})));\n')

    # HeatExchanger
    if "HeatExchanger" in componentList:
        write_sComment(f, 'Consumer')

        for i, row in net.heat_exchanger.iterrows():
            heat_exchanger_name = net.heat_exchanger['name'].loc[net.heat_exchanger.index[i]].replace(" ", "")
            heat_exchanger_Qflow = net.heat_exchanger['qext_w'].loc[net.heat_exchanger.index[i]]
            if 'heat_exchanger' in controller:  # Anpassen für großes Netz
                control_heat_exchanger = 'true'
            else:
                control_heat_exchanger = 'false'

            f.write(f'TransiEnt.Components.Boundaries.Heat.Heatflow_L1 {heat_exchanger_name}(\n'
                    f'p_nom=0,\n'
                    # f'medium=medium,\n'
                    f'Q_flow_const={heat_exchanger_Qflow},\n'
                    f'variable_m_flow={control_heat_exchanger})\t'
                    f'{gd.heat_model_annotation(net, "heat_exchanger", xy_scale, 1, i)}\n\n')

    # CirculationPumpMass
    if "CirculationPumpMass" in componentList:
        write_sComment(f, 'Sources')
        for i, row in net.circ_pump_mass.iterrows():
            circ_pump_name = net.circ_pump_mass['name'].loc[net.circ_pump_mass.index[i]].replace(" ", "")
            circ_pump_pDrop = net.res_circ_pump_mass['deltap_bar'].loc[net.circ_pump_mass.index[i]] * 1e5
            circ_pump_m_flow = net.circ_pump_mass['mdot_flow_kg_per_s'].loc[net.circ_pump_mass.index[i]]
            #circ_pump_T = net.circ_pump_mass['t_flow_k'].loc[net.circ_pump_mass.index[i]]
            if {circ_pump_name} in controller:
                control_circ_pump = 'true'
            else:
                control_circ_pump = 'false'
            f.write(f'TransiEnt.Components.Boundaries.Heat.Heatflow_L1 {circ_pump_name}(\n'
                    f'medium=init.medium,\n'
                    f'p_drop={circ_pump_pDrop},\n'
                    f'm_flow_nom={circ_pump_m_flow}\n'
                    #f'T_const={circ_pump_T},\n'
                    # f'xi_const=init.{ext_name}.xi,\n'
                    #f'variable_p={control_circ_pump},\n'
                    #f'variable_T={control_circ_pump},\n'
                    #f'variable_xi={control_circ_pump}
                    f')\t'
                    f'{gd.heat_model_annotation(net, "circ_pump_mass", xy_scale, 1, i)}\n')

    # sources
    if "Source" in componentList:
        for i, row in net.source.iterrows():
            source_name = net.source['name'].loc[net.source.index[i]].replace(" ", "")
            # ext_p = net.source['p_bar'].loc[net.ext_grid.index[i]]
            source_T = net.source['t_k'].loc[net.source.index[i]]
            if {source_name} in controller:
                control_source = 'true'
            else:
                control_source = 'false'
            f.write(f'TransiEnt.Components.Boundaries.Gas.BoundaryRealGas_pTxi {source_name}(\n'
                    # f'p_const={source_p},\n'
                    f'T_const={source_T},\n'
                    # f'medium=medium,\n'
                    # f'xi_const=init.{ext_name}.xi,\n'
                    f'variable_p={control_source},\n'
                    f'variable_T={control_source},\n'
                    f'variable_xi={control_source})\t'
                    f'{gd.heat_model_annotation(net, "source", xy_scale, 1, i)}\n')

    f.write("equation\n\n")

    # Connections
    f.write(f'{gd.heat_connections(net, componentList, xy_scale, "yellow")}')
    for i in range(len(controller)):
        heat_exchanger_name = net.heat_exchanger['name'].loc[net.heat_exchanger.index[i]].replace(" ", "")
        f.write(f'connect(control_data.y[{i + 1}], {heat_exchanger_name}.m_flow);\n')

    return (f.getvalue())

#net = example.pipe_square_flat_controller(fluid="lgas", p_junction=1.05, tfluid_K=293.15, pipe_d=0.3, pipe_l=1)

#CDB_to_Modelica(net, modelName="pandapipes_model")
filename = "heat"
net = from_json(os.path.join("network_files", filename+".json"))
CDB_to_Modelica(net, filename, xy_scale=5000)

