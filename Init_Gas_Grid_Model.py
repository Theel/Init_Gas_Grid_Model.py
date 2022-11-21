
import math
import numpy as np
import pandapipes as pp
import pandas as pd
import example
import geodata as gd

net = example.pipe_square_flat(fluid="lgas", p_junction=1.05, tfluid_K=293.15, pipe_d=0.3, pipe_l=1)

#print(pp.pp_elements(junction=True, include_node_elements=False, include_branch_elements=False,
#                     include_res_elements=False, net=net))


def Modelica_create_init(net,modelName="pandapipes_model"):


    def write_bComment(f, comment):
        f.write('\n  // ' + '-' * 90 + '\n')
        f.write('  //   ' + comment + '\n')
        f.write('  // ' + '-' * 90 + '\n\n')

    def write_sComment(f, comment):
        width = 95 - 5 - 2
        w1 = 4
        remaining = width - len(comment)
        f.write(f'  // {"-" * w1} {comment} {"-" * (remaining - w1)}\n\n')

    c_packageMain = "Models"
    c_modelName = (modelName+'_init')
    c_modelComment = "This model was automatically generated"
    c_packageModels = "CellModels"

    # --- model data ---

    c_data_local = 'Modelica.Utilities.System.getEnvironmentVariable("cyentee_data_dir")'
    c_data_local_comment = "Directory containing simulation data"

    # --- data for model writing ---
    c_mw_coordFactor = 70000
    c_mw_offsetHouseholdGeo = 20 / c_mw_coordFactor
    c_mw_extentHousehold = [15] * 2
    c_mw_extentInterface = np.array([10] * 2)
    c_mw_extentTransiEnt = np.array([20] * 2)
    c_mw_extentNode = np.array([5, 5], dtype='float')
    c_mw_extentModel = np.array([200, 200], dtype='float')

    # --- physical data ---

    # angular frequency electrical grid
    c_phy_omega = 100 * math.pi

    # factor to scale load profile (for MW and MVAr: 1e6)
    c_phy_loadProfileScale = 1e6

    # --- physical data ---

    # ---------------------------------------------------------------------------
    #   start model file
    # ---------------------------------------------------------------------------

    # open model file
    f = open(c_packageMain + "/" + c_modelName + ".mo", 'w')

    f.write(f'model init_{modelName} "{"This model was automatically generated"}"\n')

    # ---------------------------------------------------------------------------
    #   Parameter
    # ---------------------------------------------------------------------------

    write_bComment(f, "Parameter")

    #position = [-c_mw_extentModel[0] / 2 + c_mw_extentTransiEnt[0] / 2,
    #           c_mw_extentModel[1] / 2 - c_mw_extentTransiEnt[1]]

    # Fluid
    if net.fluid.fluid_type == 'gas':
        f.write('parameter TILMedia.VLEFluidTypes.BaseVLEFluid medium=simCenter.gasModel1 "Medium natural gas mixture" ;\n\n')

    # Pipes
    f.write(f'parameter Boolean quadraticPressureLoss=false "|Pipes|Nominal point pressure loss, set to true for quadratic coefficient";\n')
    # presure
    for i, row in net.pipe.iterrows():
        pipe_name = net.pipe['name'].loc[net.pipe.index[i]]
        f.write(f'parameter Modelica.Units.SI.Pressure {pipe_name}_Delta_p_nom "|Pipes|Nominal pressure loss";\n')
    # massflow
    f.write('\n')
    for i, row in net.pipe.iterrows():
        pipe_name = net.pipe['name'].loc[net.pipe.index[i]]
        f.write(f'parameter Modelica.Units.SI.MassFlowRate {pipe_name}_m_flow_nom "|Pipes|Nominal mass flow rate";\n')
    f.write('\n')

    #Sinks
    for i, row in net.sink.iterrows():
        sink_name = net.sink['name'].loc[net.sink.index[i]]
        f.write(f'parameter Modelica.Units.SI.MassFlowRate {sink_name}_m_flow "|Sinks|Mass flow rate at source";\n')
    f.write('\n')

    #Source/external grids
    for i, row in net.ext_grid.iterrows():
        ext_grid_name = net.ext_grid['name'].loc[net.ext_grid.index[i]]
        f.write(f'parameter Modelica.Units.SI.Pressure {ext_grid_name}_p=simCenter.p_eff_2 + simCenter.p_amb_const "|Sources|Pressure at the source";\n')
        f.write(f'parameter Modelica.Units.SI.Temperature {ext_grid_name}_T=simCenter.T_ground "|Sources|Temperature at the source";\n')
        f.write(f'parameter Modelica.Units.SI.MassFraction {ext_grid_name}_xi[medium.nc - 1]={ext_grid_name}.medium.xi_default "|Sources|Mass specific composition at the source";\n')
    f.write('\n')

    write_bComment(f, "Outer Models")
    f.write(f'outer TransiEnt.SimCenter simCenter;\n')

    write_bComment(f, "Instances of other Classes")


    if net.fluid.fluid_type == 'gas':
        color = 'yellow'
    else:
        color = 'blue'

    #Factor für die Entfernung der einzelnen Bauteile zueinander
    scale_factor = 40

    #DataFrames mit den Koordinaten
    node_geodata = gd.node_placement(net, scale_factor)
    pipes_geodata = gd.pipes_placement(net, scale_factor)
    sink_geodata = gd.model_placement(net, scale_factor, 'sink')
    ext_geodata = gd.model_placement(net, scale_factor, 'ext_grid')

    #pipes
    for i, row in net.pipe.iterrows():
        pipe_name = net.pipe['name'].loc[net.pipe.index[i]]
        f.write(f'TransiEnt.Grid.Gas.StaticCycles.Pipe_{color} {pipe_name}(\n'
                f'medium=medium,\n'
                f'Delta_p_nom={pipe_name}_Delta_p_nom,\n'
                f'm_flow_nom={pipe_name}_m_flow_nom,\n'
                f'quadraticPressureLoss=quadraticPressureLoss)'
                f'annotation (Placement(transformation(\n'
                f'extent={{ {{-10,6}},{{10,-6}} }}, \n'
                f'rotation={pipes_geodata.rotation[i]},\n'
                f'origin={{ {pipes_geodata.origin_x[i]} ,{pipes_geodata.origin_y[i]} }})));\n')

    #source
    for i, row in net.ext_grid.iterrows():
        ext_grid_name = net.ext_grid['name'].loc[net.ext_grid.index[i]]
        f.write(f'TransiEnt.Grid.Gas.StaticCycles.Source_{color}_T {ext_grid_name}(\n'
        f'medium=medium,\n'
        f'p={ext_grid_name}_p,\n'
        f'T={ext_grid_name}_T,\n'
        f'xi={ext_grid_name}_xi)'
        f'    annotation (Placement(transformation(\n'
        f'extent={{ {{-15,15}},{{15,-15}} }}, \n'
        f'origin={{ {ext_geodata.origin_x[i]} ,{ext_geodata.origin_y[i]} }})));\n')

    #sink
    for i, row in net.ext_grid.iterrows():
        sink_name = net.sink['name'].loc[net.sink.index[i]]
        f.write(f'TransiEnt.Grid.Gas.StaticCycles.Sink_{color} {sink_name}(\n'
        f'm_flow={sink_name}_m_flow,\n'
        f'medium=medium)'
        f'    annotation (Placement(transformation(\n'
        f'extent={{ {{-15,15}},{{15,-15}} }},\n'
        f'origin={{ {sink_geodata.origin_x[i]} ,{sink_geodata.origin_y[i]} }})));\n')

    #nodes
    junction_from = net.pipe.groupby(['from_junction']).size()
    junction_to = net.pipe.groupby(['to_junction']).size()

    # node from
    nodes_from = []
    for i in range(len(junction_from)):
        if 2 == junction_from.values[i]:
            nodes_from.append(junction_from.index[i])
            f.write(f'TransiEnt.Grid.Gas.StaticCycles.Split junction{junction_from.index[i]}(medium=medium)'
            f'annotation (Placement(transformation(\n'
            f'extent={{{{9.5,6}},{{-9.5,-6}}}},\n'
            f'origin={{{node_geodata["origin_x"].loc[junction_from.index[i]]},{node_geodata["origin_y"].loc[junction_from.index[i]]}}})));\n')


        # multi node from
        if 2 < junction_from.values[i]:
            print('multi_nodes_from')

    #node to
    nodes_to = []
    for i in range(len(junction_to)):
        if 2 == junction_to.values[i]:
            nodes_to.append(junction_to.index[i])
            f.write(f'TransiEnt.Grid.Gas.StaticCycles.Mixer1 junction{junction_to.index[i]}(medium=medium)'
                    f'    annotation(Placement(transformation(\n'
                    f'extent={{{{9.5,6}},{{-9.5,-6}}}},\n'
                    f'origin={{{node_geodata["origin_x"].loc[junction_to.index[i]]},{node_geodata["origin_y"].loc[junction_to.index[i]]}}})));\n')

        # multi node to
        if 2 < junction_to.values[i]:
            print('multi_nodes_to')


    #Valve
    valve_geodata = gd.placement_valves(net, scale_factor, nodes_to)
    for i in range(len(nodes_to)):
        f.write(f'TransiEnt.Grid.Gas.StaticCycles.Valve_cutFlow valve{nodes_to[i]}(medium=medium)'
                f'annotation (Placement(transformation(\n'
                f'extent={{ {{-10,6}},{{10,-6}} }}, \n'
                f'rotation={valve_geodata.rotation[i]},\n'
                f'origin={{ {valve_geodata.origin_x[i]} ,{valve_geodata.origin_y[i]} }})));\n')

        # multi node to
        if 2 < junction_to.values[i]:
            print('multi_nodes_to')


    f.write("equation\n\n")

    #connections
    for i, row in net.junction.iterrows():
        if i in nodes_from:
            if i in net.pipe['from_junction']:
                pipes_from = net.pipe[net.pipe['from_junction'] == i]
                count = 1
                for b, row in pipes_from.iterrows():
                    f.write(f"connect(junction{i}.outlet{count},{pipes_from['name'][b]}.inlet)"
                            f'annotation (Line(points='
                            f'{{ {{ {node_geodata["origin_x"].values[i]},{node_geodata["origin_y"].values[i]} }},'
                            f'{{ {pipes_geodata["origin_x"].values[b]},{pipes_geodata["origin_y"].values[b]} }} }},'
                            f'color={{0,0,0}}));\n')
                    count += 1
            if i in net.pipe['to_junction']:
                pipes_to = net.pipe[net.pipe['to_junction'] == i]
                for b, row in pipes_to.iterrows():
                    f.write(f'connect({pipes_to["name"][b]}.outlet,junction{i}.inlet)' 
                            f'annotation (Line(points='
                            f'{{ {{ {pipes_geodata["origin_x"].values[b]},{pipes_geodata["origin_y"].values[b]} }},'
                            f'{{ {node_geodata["origin_x"].values[i]},{node_geodata["origin_y"].values[i]} }} }},'
                            f'color={{0,0,0}}));\n')
            if i in net.ext_grid['junction']:
                ext_grid = net.ext_grid[net.ext_grid['junction'] == i]
                for b, row in ext_grid.iterrows():
                    f.write(f'connect({ext_grid["name"][b]}.outlet,junction{i}.inlet);'
                            f'annotation (Line(points='
                            f'{{ {{ {ext_geodata["origin_x"].values[b]},{ext_geodata["origin_y"].values[b]} }},'
                            f'{{ {node_geodata["origin_x"].values[i]},{node_geodata["origin_y"].values[i]} }} }},'
                            f'color={{0,0,0}}));\n')
            if i in net.sink['junction']:
                sink = net.sink[net.sink['junction'] == i]
                for b, row in sink.iterrows():
                    f.write(f'connect(junction{i}.outlet{2},{sink["name"][0]}.inlet);'
                            f'annotation (Line(points='
                            f'{{ {{ {node_geodata["origin_x"].values[i]},{node_geodata["origin_y"].values[i]} }},'
                            f'{{ {sink_geodata["origin_x"].values[b]},{sink_geodata["origin_y"].values[b]} }} }},'
                            f'color={{0,0,0}}));\n')

        elif i in nodes_to:
            valve_count = 0
            f.write(f'connect(valve{i}.outlet,junction{i}.inlet2)'
                    f'annotation (Line(points='
                    f'{{ {{ {valve_geodata["origin_x"].values[valve_count]},{valve_geodata["origin_y"].values[valve_count]} }},'
                    f'{{ {sink_geodata["origin_x"].values[b]},{sink_geodata["origin_y"].values[b]} }} }},'
                    f'color={{0,0,0}}));\n')
            if i in net.pipe['to_junction']:
                pipes_to = net.pipe[net.pipe['to_junction'] == i]
                c = 1
                for b, row in pipes_to.iterrows():
                    if c % 2 == 0:
                        f.write(f'connect({pipes_to["name"][b]}.outlet,valve{i}.inlet)'
                                f'annotation (Line(points='
                                f'{{ {{ {pipes_geodata["origin_x"].values[b]},{pipes_geodata["origin_y"].values[b]} }},'
                                f'{{ {valve_geodata["origin_x"].values[valve_count]},{valve_geodata["origin_y"].values[valve_count]} }} }},'
                                f'color={{0,0,0}}));\n')
                    else:
                        f.write(f'connect({pipes_to["name"][b]}.outlet,junction{i}.inlet{c})'
                                f'annotation (Line(points='
                                f'{{ {{ {node_geodata["origin_x"].values[i]},{node_geodata["origin_y"].values[i]} }},'
                                f'{{ {pipes_geodata["origin_x"].values[b]},{pipes_geodata["origin_y"].values[b]} }} }},'
                                f'color={{0,0,0}}));\n')
                    c += 1
            valve_count += 1
            if i in net.pipe['from_junction']:
                pipes_from = net.pipe[net.pipe['from_junction'] == i]
                for b, row in pipes_from.iterrows():
                    f.write(f'connect(junction{i}.outlet,{pipes_from["name"][b]}.inlet)'
                            f'annotation (Line(points='
                            f'{{ {{ {node_geodata["origin_x"].values[i]},{node_geodata["origin_y"].values[i]} }},'
                            f'{{ {pipes_geodata["origin_x"].values[b]},{pipes_geodata["origin_y"].values[b]} }} }},'
                            f'color={{0,0,0}}));\n')
            if i in net.ext_grid['junction']:
                ext_grid = net.ext_grid[net.ext_grid['junction'] == i]
                f.write(f'connect({ext_grid["name"][0]}.outlet,junction{i}.inlet)'
                        f'annotation (Line(points='
                        f'{{ {{ {node_geodata["origin_x"].values[i]},{node_geodata["origin_y"].values[i]} }},'
                        f'{{ {pipes_geodata["origin_x"].values[b]},{pipes_geodata["origin_y"].values[b]} }} }},'
                        f'color={{0,0,0}}));\n')
            if i in net.sink['junction']:
                sink = net.sink[net.sink['junction'] == i]
                f.write(f'connect(junction{i}.outlet{2},{sink["name"][0]}.inlet)'
                        f'annotation (Line(points='
                        f'{{ {{ {node_geodata["origin_x"].values[i]},{node_geodata["origin_y"].values[i]} }},'
                        f'{{ {sink_geodata["origin_x"].values[i]},{sink_geodata["origin_y"].values[i]} }} }},'
                        f'color={{0,0,0}}));\n')


        else:
            pipes_from = net.pipe['name'].loc[net.pipe['from_junction'] == i]
            pipes_to = net.pipe['name'].loc[net.pipe['to_junction'] == i]
            if pipes_to.empty == False and pipes_from.empty == True:
                sink = net.sink['name'].loc[net.sink['junction'] == i]
                s_index = sink.index[0]
                pt_index = pipes_to.index[0]
                f.write(f'connect({pipes_to.values[0]}.outlet,{sink.values[0]}.inlet)'
                        f'annotation (Line(points='
                        f'{{ {{ {pipes_geodata["origin_x"].values[pt_index]},{pipes_geodata["origin_y"].values[pt_index]} }},'
                        f'{{ {sink_geodata["origin_x"].values[s_index]},{sink_geodata["origin_y"].values[s_index]} }} }},'
                        f'color={{0,0,0}}));\n')
            elif pipes_from.empty == False and pipes_to.empty == True:
                ext_grid = net.ext_grid['name'].loc[net.ext_grid['junction'] == i]
                e_index = ext_grid.index[0]
                pf_index = pipes_from.index[0]
                f.write(f'connect({ext_grid.values[0]}.outlet,{pipes_from.values[0]}.inlet)'
                        f'annotation (Line(points='
                        f'{{ {{ {ext_geodata["origin_x"].values[e_index]},{ext_geodata["origin_y"].values[e_index]} }},'
                        f'{{ {pipes_geodata["origin_x"].values[pf_index]},{pipes_geodata["origin_y"].values[pf_index]} }} }},'
                        f'color={{0,0,0}}));\n')
            elif pipes_from.empty == False and pipes_to.empty == False:
                pf_index = pipes_from.index[0]
                pt_index = pipes_from.index[0]
                f.write(f'connect({pipes_to.values[0]}.outlet,{pipes_from.values[0]}.inlet)'
                        f'annotation (Line(points='
                        f'{{ {{ {pipes_geodata["origin_x"].values[pt_index]},{pipes_geodata["origin_y"].values[pt_index]} }},'
                        f'{{ {pipes_geodata["origin_x"].values[pf_index]},{pipes_geodata["origin_y"].values[pf_index]} }} }},'
                        f'color={{0,0,0}}));\n')
            else:
                print('spezial conect')


    f.write(f'\n'
            f'end init_{modelName};\n')

    f.close()

    # init für übergeordnetes Gasnetz
    init = io.StringIO()

    init.write(f'inner init_{modelName} init(\n'
               f'quadraticPressureLoss=true,\n')
    for i, row in net.pipe.iterrows():
        pipe_name = net.pipe['name'].loc[net.pipe.index[i]]
        init.write(f'{pipe_name}_Delta_p_nom={pipe_name}.Delta_p_nom,\n')
        init.write(f'{pipe_name}_m_flow_nom={pipe_name}.m_flow_nom,,\n')
    for i, row in net.sink.iterrows():
        sink_name = net.sink['name'].loc[net.sink.index[i]]
        init.write(f'{sink_name}_m_flow=sink1.m_flow_const,\n')
    for i, row in net.ext_grid.iterrows():
        ext_grid_name = net.ext_grid['name'].loc[net.ext_grid.index[i]]
        init.write(f'ext_grid_name_p = 105000,\n')
        init.write(f'ext_grid_name_T = ext_grid_name.T_const,\n'
        init.write(f'ext_grid_name_xi = ext_grid_name.xi_const\n')
    int.write(f')\n')

    return(init)
Modelica_create_init(net, modelName="pandapipes_model")

