
import math
import numpy as np
import pandapipes as pp
import pandas as pd
import geodata as gd
import io


def create_init(net,modelName="pandapipes_model"):

    def write_bComment(f, comment):
        f.write('\n  // ' + '-' * 90 + '\n')
        f.write('  //   ' + comment + '\n')
        f.write('  // ' + '-' * 90 + '\n\n')

    def write_sComment(f, comment):
        width = 95 - 5 - 2
        w1 = 4
        remaining = width - len(comment)
        f.write(f'  // {"-" * w1} {comment} {"-" * (remaining - w1)}\n\n')

    #m Model Erstellung
    f = open("Models/"+modelName + "/" + modelName + "_Init.mo", 'w')

    # Model beginn
    f.write(f'model {modelName}_Init\n')

    write_bComment(f, "import extends")
    f.write(f'extends TransiEnt.Basics.Icons.ModelStaticCycle;\n'
            f'import SI = ClaRa.Basics.Units;\n'
            f'outer TransiEnt.SimCenter simCenter;')

    write_bComment(f, " Visible Parameters")
    f.write(f'parameter TILMedia.VLEFluidTypes.BaseVLEFluid medium=simCenter.gasModel1 "|Medium|Medium natural gas mixture";\n')

    write_sComment(f, "Pipes")
    f.write(f'parameter Integer N_cv_gasPipe=3 "|Pipes|";\n'
            f'parameter Boolean FrictionInlet=false "|Pipes|";\n'
            f'parameter Boolean FrictionOutlet=false "|Pipes|";\n')

    write_sComment(f, "Sources")
    f.write(f'parameter SI.AbsolutePressure Ext_p_const=simCenter.p_amb_const + simCenter.p_eff_2 "|Source|Constant absolute pressure" annotation (Dialog(group="Constant Boundaries", enable=not variable_p));\n'
            f'parameter SI.Temperature Ext_T_const=simCenter.T_ground"|Source|Constant temperature of source" annotation (Dialog(group="Constant Boundaries", enable=not variable_T));\n'
            f'SI.AbsolutePressure Source_p_const=simCenter.p_amb_const + simCenter.p_eff_2"|Source|Constant absolute pressure" annotation (Dialog(group="Constant Boundaries", enable=not variable_p));\n'
            f'parameter SI.Temperature Source_T_const=simCenter.T_ground "|Source|Constant temperature of source" annotation (Dialog(group="Constant Boundaries", enable=not variable_T));')

    f.write(f'end {modelName}_Init;')



    return()
#Gasnet_create_init(net, modelName="pandapipes_model")

