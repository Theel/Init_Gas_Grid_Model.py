import Init_Gas_Grid_Model as init
import example
import geodata as gd

net = example.pipe_square_flat(fluid="lgas", p_junction=1.05, tfluid_K=293.15, pipe_d=0.3, pipe_l=1)
def CDB_to_Modelica(net,modelName="pandapipes_model"):

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
    initation = init.Gasnet_create_init(net, modelName)
    f.write(f'{initation.getvalue()}\n')

    # ---------------------------------------------------------------------------
    #   Parameter
    # ---------------------------------------------------------------------------

    #write_bComment(f, "Parameter")

    write_sComment(f, "TransiEnt Models (SimCenter and ModelStatistics)")


    # TransiEnt.SimCenter
    f.write(f'inner TransiEnt.SimCenter simCenter(useHomotopy=false, redeclare TransiEnt.Basics.Media.Gases.VLE_VDIWA_CH4 gasModel1) ' 
            f' annotation (Placement(transformation(extent={{{{-70,80}},{{-50,100}}}})));\n')

    write_bComment(f, "Pipes and Fittings")

    # scalefaktor für die Platzierung im Koordinatensystem
    xy_scale = 40


    for i, row in net.pipe.iterrows():
        pipe_name = net.pipe['name'].loc[net.pipe.index[i]]
        pipe_length = net.pipe['length_km'].loc[net.pipe.index[i]]
        pipe_d = net.pipe['diameter_m'].loc[net.pipe.index[i]]
        f.write(f'TransiEnt.Components.Gas.VolumesValvesFittings.Pipes.PipeFlow_L4_Simple {pipe_name}(\n'
                f'frictionAtInlet=true,\n'
                f'frictionAtOutlet=true,\n'
                f'initOption=0,\n'
                f'N_cv=5,\n'
                f'length(displayUnit="km")={pipe_length},\n'
                f'diameter_i={pipe_d},\n'
                f'redeclare model PressureLoss = ClaRa.Basics.ControlVolumes.Fundamentals.PressureLoss.Generic_PL.QuadraticNominalPoint_L4,\n'
                f'h_start=ones({pipe_name}.N_cv)*init.{pipe_name}.h_in,\n'
                f'p_start=linspace(\n'
                f'  init.{pipe_name}.p_in,\n'
                f'  init.{pipe_name}.p_out,\n'
                f'  {pipe_name}.N_cv),\n'
                f'm_flow_start=ones({pipe_name}.N_cv + 1)*init.{pipe_name}.m_flow,\n'
                f'xi_start=init.{pipe_name}.xi_in)\t'
                f'{gd.pipes_annotation(net, xy_scale, 1, i)}\n\n')

    # node from
    junction_from = net.pipe.groupby(['from_junction']).size()
    for i in range(len(junction_from)):
        if 2 == junction_from.values[i]:
            f.write(f'TransiEnt.Components.Gas.VolumesValvesFittings.Fittings.RealGasJunction_L2 junction{junction_from.index[i]}(\n'
                    f'initOption=0,\n'
                    f'redeclare model PressureLoss2 = ClaRa.Components.VolumesValvesFittings.Fittings.Fundamentals.Linear,\n'
                    f'p(start=init.junction{junction_from.index[i]}.p),\n'
                    f'xi(start=init.junction{junction_from.index[i]}.xi_in),\n'
                    f'h(start=init.junction{junction_from.index[i]}.h_in),\n'
                    f'volume=1)\t'
                    f'{gd.node_annotation(net, xy_scale, node_to_from="node_from", node_index=i)}\n')

        # multi node from
        if 2 < junction_from.values[i]:
            print('multi_nodes_from')

    # node to
    junction_to = net.pipe.groupby(['to_junction']).size()
    for i in range(len(junction_to)):
        if 2 == junction_to.values[i]:
            f.write(f'TransiEnt.Components.Gas.VolumesValvesFittings.Fittings.RealGasJunction_L2 junction{junction_to.index[i]}(\n'
                    f'initOption=0,\n'
                    f'redeclare model PressureLoss2 = ClaRa.Components.VolumesValvesFittings.Fittings.Fundamentals.Linear,\n'
                    f'p(start=init.junction{junction_to.index[i]}.p),\n'
                    f'xi(start=init.junction{junction_to.index[i]}.xi_out),\n'
                    f'h(start=init.junction{junction_to.index[i]}.h_out),\n'
                    f'volume=1)\t'
                    f'{gd.node_annotation(net, xy_scale, node_to_from="node_to", node_index=i)}\n')

        # multi node to
        if 2 < junction_to.values[i]:
            print('multi_nodes_to')

    # controller externe Daten
    controller = []
    if net.controller.empty == False:
        for i, row in net.controller.iterrows():
            controller.append(net.controller.object.values[i].element)

    # sink
    write_sComment(f, 'Consumer')
    for i, row in net.sink.iterrows():
        sink_name = net.sink['name'].loc[net.sink.index[i]]
        sink_mdot = net.sink['mdot_kg_per_s'].loc[net.sink.index[i]]
        if {sink_name} in controller:
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
        ext_name = net.ext_grid['name'].loc[net.ext_grid.index[i]]
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


    #connection= gd.model_connections(net, xy_scale)
    #f.write(f'{connection.getvalue()}\n')
    f.write(f'{gd.model_connections(net, xy_scale, "yellow", init=False)}\n')
    f.write(f'\n'
            f'end {modelName};\n')



    f.close()




CDB_to_Modelica(net,modelName="pandapipes_model")