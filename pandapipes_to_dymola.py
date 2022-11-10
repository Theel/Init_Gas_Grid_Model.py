


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


    # open model file
    f = open(directory + c_packageMain + "/" + c_modelName + ".mo", 'w')

    f.write(f'within {"Pandapipes_Model"};\n')
    f.write(f'model{modelName} "{"This model was automatically generated"}";\n')

    # ---------------------------------------------------------------------------
    #   Parameter
    # ---------------------------------------------------------------------------

    write_bComment(f, "Parameter")

    write_sComment(f, "TransiEnt Models (SimCenter and ModelStatistics)")

    position = [-c_mw_extentModel[0] / 2 + c_mw_extentTransiEnt[0] / 2,
                c_mw_extentModel[1] / 2 - c_mw_extentTransiEnt[1]]

    # TransiEnt.SimCenter
    f.write('  inner TransiEnt.SimCenter simCenter \n' \
            f'    annotation ({str_placement(position, c_mw_extentTransiEnt)});\n')

    position = [position[0] + c_mw_extentTransiEnt[0] * 1.5, position[1]]

    # TransiEnt.ModelStatistics
    f.write('  inner TransiEnt.ModelStatistics modelStatistics \n' \
            f'    annotation ({str_placement(position, c_mw_extentTransiEnt)});\n\n')

