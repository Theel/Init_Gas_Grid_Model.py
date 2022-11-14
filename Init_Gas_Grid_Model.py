
import math
import numpy as np
import pandapipes as pp
import pandas as pd
import example

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

    f.write(f'model Init_{modelName} "{"This model was automatically generated"}"\n')

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
        f.write(f'parameter Modelica.Units.SI.MassFraction {ext_grid_name}_xi[medium.nc - 1]=source1.medium.xi_default "|Sources|Mass specific composition at the source";\n')
    f.write('\n')

    write_bComment(f, "Outer Models")
    f.write(f'outer TransiEnt.SimCenter simCenter;\n')

    write_bComment(f, "Instances of other Classes")

    def str_placement_pipe(to_geodata, from_geodata, factor):
        if to_geodata.y == from_geodata.y:
            if to_geodata.x > from_geodata.x:
                rotation = '0'
            else:
                rotation = '180'
        else:
            if to_geodata.y > from_geodata.y:
                rotation = '90'
            else:
                rotation = '270'
        origin = (str((to_geodata.x*0.5 - from_geodata.x*(0.5-1))*factor),
                  str((to_geodata.y*0.5 - from_geodata.y*(0.5-1))*factor))

        return ("Placement(transformation(\n"
                "extent={{-10,6},{10,-6}}, \n"
                "rotation="+rotation +", \n"
                "origin={" +origin[0]+","+origin[1]+ "}))")


    def str_placement(geodata, factor):
        origin = (str(geodata.x * factor), str(to_geodata.y * factor))
        return ("Placement(transformation(\n"
                "extent={{-15,15},{15,-15}}, \n"
                "origin={" + origin[0] + "," + origin[1] + "}))")

    def str_placement_nodes(geodata, factor):
        origin = (str(geodata.x * factor), str(to_geodata.y * factor))
        return ("Placement(transformation(\n"
                "extent={{9.5,6},{-9.5,-6}}, \n"
                "origin={" + origin[0] + "," + origin[1] + "}))")

    def str_placement_valves(net, factor, node):
        pipe_row = net.pipe.loc[net.pipe['to_junction'] == node]
        from_junction = pipe_row['from_junction'].loc[pipe_row.index[1]]
        to_junction = pipe_row['to_junction'].loc[pipe_row.index[1]]
        from_geodata = net.junction_geodata.loc[net.junction_geodata.index[from_junction]]
        to_geodata = net.junction_geodata.loc[net.junction_geodata.index[to_junction]]
        if to_geodata.y == from_geodata.y:
            if to_geodata.x > from_geodata.x:
                rotation = '0'
                origin = (str((to_geodata.x * 0.7 - from_geodata.x * (0.3 - 1)) * factor),
                          str((to_geodata.y * 0.5 - from_geodata.y * (0.5 - 1)) * factor))
            else:
                rotation = '180'
                origin = (str((to_geodata.x * 0.3 - from_geodata.x * (0.7 - 1)) * factor),
                          str((to_geodata.y * 0.5 - from_geodata.y * (0.5 - 1)) * factor))
        else:
            if to_geodata.y > from_geodata.y:
                rotation = '90'
                origin = (str((to_geodata.x * 0.5 - from_geodata.x * (0.5 - 1)) * factor),
                          str((to_geodata.y * 0.7 - from_geodata.y * (0.3 - 1)) * factor))
            else:
                rotation = '270'
            origin = (str((to_geodata.x*0.5 - from_geodata.x*(0.5-1))*factor),
                      str((to_geodata.y*0.3 - from_geodata.y*(0.7-1))*factor))
        return ("Placement(transformation(\n"
                "extent={{-8,4},{8,-4}}, \n"
                "rotation="+rotation +", \n"
                "origin={" + origin[0] + "," + origin[1] + "}))")

    if net.fluid.fluid_type == 'gas':
        color = 'yellow'
    else:
        color = 'blue'

    #Factor für die Entfernung der einzelnen Bauteile zueinander
    scale_factor = 40

    #pipes
    for i, row in net.pipe.iterrows():
        pipe_name = net.pipe['name'].loc[net.pipe.index[i]]
        from_junction = net.pipe['from_junction'].loc[net.pipe.index[i]]
        to_junction = net.pipe['to_junction'].loc[net.pipe.index[i]]
        from_geodata = net.junction_geodata.loc[net.junction_geodata.index[from_junction]]
        to_geodata = net.junction_geodata.loc[net.junction_geodata.index[to_junction]]
        f.write(f'TransiEnt.Grid.Gas.StaticCycles.Pipe_{color} {pipe_name}(\n'
                f'medium=medium,\n'
                f'Delta_p_nom={pipe_name}_Delta_p_nom,\n'
                f'm_flow_nom={pipe_name}_m_flow_nom,\n'
                f'quadraticPressureLoss=quadraticPressureLoss)'
                f'    annotation ({str_placement_pipe(to_geodata, from_geodata, scale_factor)});\n')
    #source
    for i, row in net.ext_grid.iterrows():
        ext_grid_name = net.ext_grid['name'].loc[net.ext_grid.index[i]]
        junction = net.ext_grid['junction'].loc[net.ext_grid.index[i]]
        geodata = net.junction_geodata.loc[net.junction_geodata.index[junction]]
        f.write(f'TransiEnt.Grid.Gas.StaticCycles.Source_{color}_T {ext_grid_name}(\n'
        f'medium=medium,\n'
        f'p={ext_grid_name}_p,\n'
        f'T={ext_grid_name}_T,\n'
        f'xi={ext_grid_name}_xi)'
        f'    annotation ({str_placement(geodata, scale_factor)});\n')

    #sink
    for i, row in net.ext_grid.iterrows():
        sink_name = net.sink['name'].loc[net.sink.index[i]]
        junction = net.sink['junction'].loc[net.sink.index[i]]
        geodata = net.junction_geodata.loc[net.junction_geodata.index[junction]]
        f.write(f'TransiEnt.Grid.Gas.StaticCycles.Sink_{color} {sink_name}(\n'
        f'm_flow={sink_name}_m_flow,\n'
        f'medium=medium)'
        f'    annotation ({str_placement(geodata, scale_factor)});\n')

    #nodes
    junction_from = net.pipe.groupby(['from_junction']).size()
    junction_to = net.pipe.groupby(['to_junction']).size()

    # node from
    nodes_from = []
    for i in range(len(junction_from)):
        if 2 == junction_from.values[i]:
            nodes_from.append(junction_from.index[i])
            geodata = net.junction_geodata.loc[junction_from.index[i]]
            f.write(f'TransiEnt.Grid.Gas.StaticCycles.Split junction{junction_from.index[i]}(medium=medium)'
                    f'    annotation ({str_placement_nodes(geodata, scale_factor)});\n')

        # multi node from
        if 2 < junction_from.values[i]:
            print('multi_nodes_from')

    #node to
    nodes_to = []
    for i in range(len(junction_to)):
        if 2 == junction_to.values[i]:
            nodes_to.append(junction_to.index[i])
            geodata = net.junction_geodata.loc[junction_to.index[i]]
            f.write(f'TransiEnt.Grid.Gas.StaticCycles.Mixer1 junction{junction_to.index[i]}(medium=medium)'
                    f'    annotation ({str_placement_nodes(geodata, scale_factor)});\n')
            #Valve
            f.write(f'TransiEnt.Grid.Gas.StaticCycles.Valve_cutFlow valve_cutFlow{i}(medium=medium)'
                    f'    annotation ({str_placement_valves(net, scale_factor, junction_to.index[i])});\n')

        # multi node to
        if 2 < junction_to.values[i]:
            print('multi_nodes_to')


    f.write("equation\n\n")

    #connections

    for i, row in net.junction.iterrows():
        if i in nodes_from:
            if i in net.pipe['from_junction']:
                pipes_from = net.pipe[net.pipe['from_junction'] == i]
                for b, row in pipes_from.iterrows():
                    f.write(f'connect(junction{i}.outlet{b+1},{pipes_from["name"][b]}.inlet )\n')
            if i in net.pipe['to_junction']:
                pipes_from = net.pipe[net.pipe['to_junction'] == i]
                for b, row in pipes_to.iterrows():
                    f.write(f'connect({pipes_from["name"][b]}.outlet,junction{i}.inlet )\n')
            if i in net.ext_grid['junction']:
                ext_grid = net.ext_grid[net.ext_grid['junction'] == i]
                f.write(f'connect({ext_grid["name"][0]}.outlet,junction{i}.inlet )\n')
            if i in net.sink['junction']:
                sink = net.sink[net.sink['junction'] == i]
                f.write(f'connect(junction{i}.outlet{2},{sink["name"][0]}.inlet )\n')

        if i in nodes_to:
            f.write(f'connect(valve{i}.outlet,junction{i}.inlet2 )\n')
            if i in net.pipe['to_junction']:
                pipes_to = net.pipe[net.pipe['to_junction'] == i]
                for b, row in pipes_to.iterrows():
                    if b == 0:
                        f.write(f'connect({pipes_to["name"][b]}.outlet,junction{i}.inlet{b+1} )\n')
                    else:
                        f.write(f'connect({pipes_to["name"][b]}.outlet,valve{i}.inlet )\n')
            if i in net.pipe['from_junction']:
                pipes_from = net.pipe[net.pipe['from_junction'] == i]
                for b, row in pipes_from.iterrows():
                    f.write(f'connect(junction{i}.outlet,{pipes_from["name"][b]}.inlet )\n')
            if i in net.ext_grid['junction']:
                ext_grid = net.ext_grid[net.ext_grid['junction'] == i]
                f.write(f'connect({ext_grid["name"][0]}.outlet,junction{i}.inlet )\n')
            if i in net.sink['junction']:
                sink = net.sink[net.sink['junction'] == i]
                f.write(f'connect(junction{i}.outlet{2},{sink["name"][0]}.inlet )\n')
        else:
            pipes_from = net.pipe[net.pipe['from_junction'] == i]
            pipes_to = net.pipe[net.pipe['to_junction'] == i]
            if pipes_to.empty == False and pipes_from.empty == True:
                sink = net.sink[net.sink['junction'] == i]
                f.write(f'connect({pipes_to["name"][0]}.outlet,{sink["name"][0]}.inlet)\n')
            if pipes_from.empty == False and pipes_to.empty == True:
                ext_grid = net.ext_grid[net.ext_grid['junction'] == i]
                f.write(f'connect({ext_grid["name"][0]}.outlet,{pipes_from["name"][0]}.inlet)\n')
            if pipes_to.empty == True and pipes_from.empty == True:
                print('spezial conect')



    f.write(f'end {c_modelName};\n')

    f.close()

Modelica_create_init(net, modelName="pandapipes_model")

