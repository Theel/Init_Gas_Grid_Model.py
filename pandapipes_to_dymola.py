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
    f.write(f'  inner TransiEnt.SimCenter simCenter(useHomotopy=false, redeclare TransiEnt.Basics.Media.Gases.VLE_VDIWA_CH4 gasModel1) \n' 
            f'    annotation (Placement(transformation(extent={{{{-70,80}},{{-50,100}}}})));\n')

    write_bComment(f, "Pipes and Fittings")

    # scalefaktor für die Platzierung im Koordinatensystem
    xy_scale = 40

    #node_geodata = gd.node_placement(net, scale_factor)
    #pipes_geodata = gd.pipes_placement(net, scale_factor)
    #sink_geodata = gd.model_placement(net, scale_factor, 'sink')
    #ext_geodata = gd.model_placement(net, scale_factor, 'ext_grid')

    for i, row in net.pipe.iterrows():
        pipe_name = net.pipe['name'].loc[net.pipe.index[i]]
        pipe_length = net.pipe['length_km'].loc[net.pipe.index[i]]
        pipe_d = net.pipe['diameter_m'].loc[net.pipe.index[i]]
        f.write(f'TransiEnt.Components.Gas.VolumesValvesFittings.Pipes.PipeFlow_L4_Simple {pipe_name}(\n'
                f'frictionAtInlet=true,\n'
                f'frictionAtOutlet=true,\n'
                f'initOption=0\n,'
                f'N_cv=5\n,'
                f'length(displayUnit="km")={pipe_length}\n,'
                f'diameter_i={pipe_d}\n,'
                f'redeclare model PressureLoss = ClaRa.Basics.ControlVolumes.Fundamentals.PressureLoss.Generic_PL.QuadraticNominalPoint_L4,\n'
                f'h_start=ones(pipe1.N_cv)*init.pipe1.h_in,\n'
                f'p_start=linspace(\n'
                f'  init.{pipe_name}.p_in,\n'
                f'  init.{pipe_name}.p_out,\n'
                f'  {pipe_name}.N_cv),\n'
                f'm_flow_start=ones({pipe_name}.N_cv + 1)*init.{pipe_name}.m_flow,\n'
                f'xi_start=init.{pipe_name}.xi_in)\t'
                f'{gd.pipes_annotation(net, xy_scale, 1, i)};\n')



    # sink
    controller = []
    if net.controller.empty == False:
        for i, row in net.controller.iterrows():
            controller.append(net.controller.object.values[i].element)

    write_sComment(f, 'Consumer')
    for i, row in net.sink.iterrows():
        sink_name = net.sink['name'].loc[net.sink.index[i]]
        sink_mdot = net.sink['mdot_kg_per_s'].loc[net.sink.index[i]]
        if {sink_name} in controller:
            control_sink = True
        else:
            control_sink = False
        f.write(f'TransiEnt.Components.Boundaries.Gas.BoundaryRealGas_Txim_flow sink1(\n'
                f'p_nom=0,\n'
                f'm_flow_const={sink_mdot},\n'
                f'variable_m_flow={control_sink})\t'
                f'{gd.model_annotation(net, "sink",xy_scale, 1, i)};\n')




    f.write("equation\n\n")


    f.write(f'\n'
            f'end {modelName};\n')
    f.close()




CDB_to_Modelica(net,modelName="pandapipes_model")