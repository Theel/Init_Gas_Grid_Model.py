import Init_Gas_Grid_Model as init
import example
import geodata as gd
import Table_converter as Tc

def CDB_to_Modelica(net,modelName="pandapipes_model", xy_scale=40):

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
    c_modelName = modelName

    # open model file
    f = open(c_packageMain + "/" + c_modelName + ".mo", 'w')


    f.write(f'model {modelName} "{"This model was automatically generated"}"\n')

    # ---------------------------------------------------------------------------
    #   Instances of other Classes
    # ---------------------------------------------------------------------------
    write_bComment(f, 'Instances of other Classes')
    #initation = init.Gasnet_create_init(net, modelName)
    #f.write(f'{initation.getvalue()}\n')

    # ---------------------------------------------------------------------------
    #   Parameter
    # ---------------------------------------------------------------------------

    #write_bComment(f, "Parameter")

    write_sComment(f, "TransiEnt Models (SimCenter and ModelStatistics)")


    # TransiEnt.SimCenter
    f.write(f'inner TransiEnt.SimCenter simCenter(useHomotopy=false, redeclare TransiEnt.Basics.Media.Gases.VLE_VDIWA_CH4 gasModel1) ' 
            f' annotation (Placement(transformation(extent={{{{-70,80}},{{-50,100}}}})));\n')

    write_bComment(f, "Pipes and Fittings")



    for i, row in net.pipe.iterrows():
        pipe_name = net.pipe['name'].loc[net.pipe.index[i]].replace(" ", "")
        pipe_length = net.pipe['length_km'].loc[net.pipe.index[i]]
        pipe_d = net.pipe['diameter_m'].loc[net.pipe.index[i]]
        f.write(f'TransiEnt.Components.Gas.VolumesValvesFittings.Pipes.PipeFlow_L4_Simple {pipe_name}(\n'
                f'frictionAtInlet=true,\n'
                f'frictionAtOutlet=true,\n'
                f'initOption=0,\n'
                f'N_cv=5,\n'
                f'length(displayUnit="km")={pipe_length},\n'
                f'diameter_i={pipe_d})\t'
                #f'redeclare model PressureLoss = ClaRa.Basics.ControlVolumes.Fundamentals.PressureLoss.Generic_PL.QuadraticNominalPoint_L4,\n'
                #f'h_start=ones({pipe_name}.N_cv)*init.{pipe_name}.h_in,\n'
                #f'p_start=linspace(\n'
                #f'  init.{pipe_name}.p_in,\n'
                #f'  init.{pipe_name}.p_out,\n'
                #f'  {pipe_name}.N_cv),\n'
                #f'm_flow_start=ones({pipe_name}.N_cv + 1)*init.{pipe_name}.m_flow,\n'
                #f'xi_start=init.{pipe_name}.xi_in)\t'
                f'{gd.pipes_annotation(net, xy_scale, 1, i)}\n\n')

    # node from
    junction_from = net.pipe.groupby(['from_junction']).size()
    junction_to = net.pipe.groupby(['to_junction']).size()
    nodes_to = []
    nodes_from = []
    for i in range(len(junction_to)):
        node_connections = 0
        if i in net.ext_grid['junction']:
            node_connections = junction_to.values[i] + 1
        else:
            node_connections = junction_to.values[i]
        if 1 < node_connections:
            nodes_to.append(junction_to.index[i])
    for i in range(len(junction_from)):
        node_connections = 0
        if i in net.sink['junction']:
            node_connections = junction_to.values[i] + 1
        else:
            node_connections = junction_to.values[i]
        if 1 < node_connections:
            nodes_from.append(junction_from.index[i])
    multi_in_out = set(nodes_from) & set(nodes_to)
    nodes_to = [i for i in nodes_to if i not in multi_in_out]
    nodes_from = [i for i in nodes_from if i not in multi_in_out]
    for i in nodes_from:
        f.write(f'TransiEnt.Components.Gas.VolumesValvesFittings.Fittings.RealGasJunction_L2_nPorts junction{i}(\n'
                f'initOption=simCenter.initOptionGasPipes)\t'
                #f'redeclare model PressureLoss2 = ClaRa.Components.VolumesValvesFittings.Fittings.Fundamentals.Linear,\n'
                #f'p(start=init.junction{i}.p),\n'
                #f'xi(start=init.junction{i}.xi_in),\n'
                #f'h(start=init.junction{i}.h_in),\n'
                #f'volume=1)\t'
                f'{gd.node_annotation(net, xy_scale, node_to_from="node_from", node_index=i)}\n')

    for i in nodes_to:
        f.write(f'TransiEnt.Components.Gas.VolumesValvesFittings.Fittings.RealGasJunction_L2_nPorts junction{i}(\n'
                f'initOption=simCenter.initOptionGasPipes)\t'
                #f'redeclare model PressureLoss2 = ClaRa.Components.VolumesValvesFittings.Fittings.Fundamentals.Linear,\n'
                #f'p(start=init.junction{i}.p),\n'
                #f'xi(start=init.junction{i}.xi_in),\n'
                #f'h(start=init.junction{i}.h_in),\n'
                #f'volume=1)\t'
                f'{gd.node_annotation(net, xy_scale, node_to_from="node_to", node_index=i)}\n')
    for i in multi_in_out:
        f.write(f'TransiEnt.Components.Gas.VolumesValvesFittings.Fittings.RealGasJunction_L2_nPorts junction{i}(\n'
                f'initOption=simCenter.initOptionGasPipes)\t'
                f'{gd.node_annotation(net, xy_scale, node_to_from="node_from", node_index=i)}\n')
    # node from
    # junction_from = net.pipe.groupby(['from_junction']).size()
    # junction_to = net.pipe.groupby(['to_junction']).size()
    # nodes_to = []
    # nodes_from = []
    # for i in range(len(junction_to)):
    #     if 1 < junction_to.values[i]:
    #         nodes_to.append(junction_to.index[i])
    # for i in range(len(junction_from)):
    #     if 1 < junction_from.values[i]:
    #         nodes_from.append(junction_from.index[i])
    # multi_in_out = set(nodes_from) & set(nodes_to)
    # nodes_to = [i for i in nodes_to if i not in multi_in_out]
    # nodes_from = [i for i in nodes_from if i not in multi_in_out]
    #
    #
    # for i in nodes_from:
    #     if junction_from[i] == 2:
    #         f.write(f'TransiEnt.Components.Gas.VolumesValvesFittings.Fittings.RealGasJunction_L2 junction{i}(\n'
    #                 f'initOption=0,\n'
    #                 f'redeclare model PressureLoss2 = ClaRa.Components.VolumesValvesFittings.Fittings.Fundamentals.Linear,\n'
    #                 f'p(start=init.junction{i}.p),\n'
    #                 f'xi(start=init.junction{i}.xi_in),\n'
    #                 f'h(start=init.junction{i}.h_in),\n'
    #                 f'volume=1)\t'
    #                 f'{gd.node_annotation(net, xy_scale, node_to_from="node_from", node_index=i)}\n')
    #
    #     # multi node from
    #     if 2 < junction_from[i]:
    #         print('multi_nodes_from')
    #
    # # node to
    #
    #
    #      if junction_to[i] == 2:
    #         f.write(f'TransiEnt.Components.Gas.VolumesValvesFittings.Fittings.RealGasJunction_L2 junction{i}(\n'
    #                 f'initOption=0,\n'
    #                 f'redeclare model PressureLoss2 = ClaRa.Components.VolumesValvesFittings.Fittings.Fundamentals.Linear,\n'
    #                 f'p(start=init.junction{i}.p),\n'
    #                 f'xi(start=init.junction{i}.xi_out),\n'
    #                 f'h(start=init.junction{i}.h_out),\n'
    #                 f'volume=1)\t'
    #                 f'{gd.node_annotation(net, xy_scale, node_to_from="node_to", node_index=i)}\n')
    #
    #     # multi node to
    #     if 2 < junction_to[i]:
    #         print('multi_nodes_to')

    # controller externe Daten
    write_sComment(f, 'Controller')
    controller = []
    if net.controller.empty == False:
        for i, row in net.controller.iterrows():
            controller.append(net.controller.object.values[i].element)
            tab_filename = 'simple_time_series_example_sink_profiles'
            Data_file = r'files'                                                     # the file directory used by the Controller
            dym_filename = Tc.table_converter(tab_filename, Data_file)
            f.write(f'Modelica.Blocks.Sources.CombiTimeTable { controller[i]}(\n'
                    f'tableOnFile=true,\n'
                    f'tableName="{tab_filename}",\n'
                    f'fileName="{dym_filename}",\n'
                    f'extrapolation=Modelica.Blocks.Types.Extrapolation.HoldLastPoint,\n'
                    f'startTime=200)\t'
                    f'annotation (Placement(transformation(extent={{{{-100,52}},{{-80,72}}}})));\n')

    # sink
    write_sComment(f, 'Consumer')
    for i, row in net.sink.iterrows():
        sink_name = net.sink['name'].loc[net.sink.index[i]].replace(" ", "")
        sink_mdot = net.sink['mdot_kg_per_s'].loc[net.sink.index[i]]
        if 'sink' in controller: # Anpassen für großes Netz
            control_sink = 'true'
        else:
            control_sink = 'false'
        f.write(f'TransiEnt.Components.Boundaries.Gas.BoundaryRealGas_Txim_flow {sink_name}(\n'
                f'p_nom=0,\n'
                f'm_flow_const={sink_mdot},\n'
                f'variable_m_flow={control_sink})\t'
                f'{gd.model_annotation(net, "sink",xy_scale, 1, i)}\n\n')

    # sources
    write_sComment(f, 'Sources')
    for i, row in net.ext_grid.iterrows():
        ext_name = net.ext_grid['name'].loc[net.ext_grid.index[i]].replace(" ", "")
        if {ext_name} in controller:
            control_ext = 'true'
        else:
            control_ext = 'false'
        f.write(f'TransiEnt.Components.Boundaries.Gas.BoundaryRealGas_pTxi {ext_name}(\n'
                f'p_const=init.{ext_name}_p,\n'
                f'T_const=init.{ext_name}_T,\n'
                f'xi_const=init.{ext_name}.xi,\n'
                f'variable_p={control_ext},\n'
                f'variable_T={control_ext},\n'
                f'variable_xi={control_ext})\t'
                f'{gd.model_annotation(net, "ext_grid", xy_scale, 1, i)}\n')

    f.write("equation\n\n")

    # Connections
    #f.write(f'{gd.model_connections(net, xy_scale, "yellow")}')
    for i in range(len(controller)):                                                                # noch erweitern
        f.write(f'connect({controller[i]}.y[1], sink1.m_flow);\n')



    f.write(f'\n'
            f'end {modelName};\n')



    f.close()




#net = example.pipe_square_flat_controller(fluid="lgas", p_junction=1.05, tfluid_K=293.15, pipe_d=0.3, pipe_l=1)

#CDB_to_Modelica(net, modelName="pandapipes_model")

