import pandapipes as pp
import pandas as pd
import example
import pandapipes.plotting as plot
import io

net = example.pipe_square_flat(fluid="lgas", p_junction=1.05, tfluid_K=293.15, pipe_d=0.3, pipe_l=1)

def pipes_placement(net, factor = 40):
    rotation = []
    origin_x = []
    origin_y = []
    names=[]
    for i, row in net.pipe.iterrows():
        from_junction = net.pipe['from_junction'].loc[net.pipe.index[i]]
        to_junction = net.pipe['to_junction'].loc[net.pipe.index[i]]
        from_geodata = net.junction_geodata.loc[net.junction_geodata.index[from_junction]]
        to_geodata = net.junction_geodata.loc[net.junction_geodata.index[to_junction]]
        if to_geodata.y == from_geodata.y:
            if to_geodata.x > from_geodata.x:
                rotation.append('0')
            else:
                rotation.append('180')
        else:
            if to_geodata.y > from_geodata.y:
                rotation.append('90')
            else:
                rotation.append('270')

        origin_x.append((to_geodata.x * 0.5 - from_geodata.x * (0.5 - 1)) * factor)
        origin_y.append((to_geodata.y * 0.5 - from_geodata.y * (0.5 - 1)) * factor)
    dict = {'names': net.pipe['name'], 'origin_x': origin_x, 'origin_y': origin_y, 'rotation': rotation}
    geodata_pipe = pd.DataFrame(dict)
    return(geodata_pipe)

def model_placement(net,factor=40, model='sink'):
    origin_x = []
    origin_y = []
    for i, row in net.junction.iterrows():
        if i in getattr(net, model)['junction']:
            junction = getattr(net, model)['junction'].loc[getattr(net, model).index[i]]
            geodata = net.junction_geodata.loc[net.junction_geodata.index[junction]]
            origin_x.append(geodata.x * factor)
            origin_y.append(geodata.y * factor)
    dict = {'names': getattr(net, model)['name'], 'origin_x': origin_x, 'origin_y': origin_y}
    geodata = pd.DataFrame(dict)
    return(geodata)

def node_placement(net,factor=40):
    origin_x = []
    origin_y = []
    for i, row in net.junction.iterrows():
        geodata = net.junction_geodata.loc[i]
        origin_x.append(geodata.x * factor)
        origin_y.append(geodata.y * factor)
    dict = {'names': net.junction['name'], 'origin_x': origin_x, 'origin_y': origin_y}
    geodata = pd.DataFrame(dict)
    return(geodata)


def placement_valves(net, factor, nodes_to):
    rotation = []
    origin_x = []
    origin_y = []
    names=[]
    for i in range(len(nodes_to)):
        pipe_row = net.pipe.loc[net.pipe['to_junction'] == nodes_to[i]]
        from_junction = pipe_row['from_junction'].loc[pipe_row.index[1]]
        to_junction = pipe_row['to_junction'].loc[pipe_row.index[1]]
        from_geodata = net.junction_geodata.loc[net.junction_geodata.index[from_junction]]
        to_geodata = net.junction_geodata.loc[net.junction_geodata.index[to_junction]]

        if to_geodata.y == from_geodata.y:
            if to_geodata.x > from_geodata.x:
                rotation.append('0')
                origin_x.append((to_geodata.x * 0.7 - from_geodata.x * (0.3 - 1)) * factor)
                origin_y.append((to_geodata.y * 0.5 - from_geodata.y * (0.5 - 1)) * factor)
            else:
                rotation.append('180')
                origin_x.append((to_geodata.x * 0.3 - from_geodata.x * (0.7 - 1)) * factor)
                origin_y.append((to_geodata.y * 0.5 - from_geodata.y * (0.5 - 1)) * factor)
        else:
            if to_geodata.y > from_geodata.y:
                rotation.append('90')
                origin_x.append((to_geodata.x * 0.5 - from_geodata.x * (0.5 - 1)) * factor)
                origin_y.append((to_geodata.y * 0.7 - from_geodata.y * (0.3 - 1)) * factor)
            else:
                rotation.append('270')
            origin_x.append((to_geodata.x*0.5 - from_geodata.x*(0.5-1))*factor)
            origin_y.append((to_geodata.y*0.3 - from_geodata.y*(0.7-1))*factor)
        names.append("valve" + str(i))
    dict = {'names': names, 'origin_x': origin_x, 'origin_y': origin_y, 'rotation': rotation}
    geodata = pd.DataFrame(dict)
    return (geodata)


def pipes_annotation(net, xy_scale, size_scale=1, pipe_index=0):
    pipes_geodata = pipes_placement(net, factor=xy_scale)
    a = io.StringIO()
    size = [10*size_scale, 6*size_scale]
    a.write(f'annotation (Placement(transformation(\n'
            f'extent={{{{{size[0]*-1},{size[1]}}},{{{size[0]},{size[1]*-1}}} }}, \n'
            f'rotation={pipes_geodata.rotation[pipe_index]},\n'
            f'origin={{ {pipes_geodata.origin_x[pipe_index]} ,{pipes_geodata.origin_y[pipe_index]} }})));\n')
    return(a.getvalue())
def model_annotation(net, model_a='sink', xy_scale=40, size_scale=1, model_index=0):
    model_geodata = model_placement(net, factor=xy_scale, model=model_a)
    a = io.StringIO()
    if model_a == 'sink':
        size = [8*size_scale, 8*size_scale]
    if model_a == 'ext_grid':
        size = [-8*size_scale, -8*size_scale]
    a.write(f'annotation (Placement(transformation(\n'
            f'extent={{{{{size[0]},{size[1]*-1}}},{{{size[0]*-1},{size[1]}}} }}, \n'
            f'origin={{ {model_geodata.origin_x[model_index]} ,{model_geodata.origin_y[model_index]} }})));\n')
    return(a.getvalue())

def node_annotation(net, xy_scale, size_scale=1, node_to_from='node_to', node_index=1):
    node_geodata = node_placement(net, factor=xy_scale)
    junction_from = net.pipe.groupby(['from_junction']).size()
    junction_to = net.pipe.groupby(['to_junction']).size()
    a = io.StringIO()
    size = [9.5 * size_scale, 6 * size_scale]
    if node_to_from == 'node_from':
        a.write(f'annotation (Placement(transformation(\n'
            f'extent={{{{{size[0]},{size[0]}}},{{{size[0]*-1},{size[1]*-1}}}}},\n'
            f'origin={{{node_geodata["origin_x"].loc[junction_from.index[node_index]]},{node_geodata["origin_y"].loc[junction_from.index[node_index]]}}})));\n')
    if node_to_from == 'node_to':
        a.write(f'annotation (Placement(transformation(\n'
                f'extent={{{{{size[0]},{size[0]}}},{{{size[0] * -1},{size[1] * -1}}}}},\n'
                f'origin={{{node_geodata["origin_x"].loc[junction_to.index[node_index]]},{node_geodata["origin_y"].loc[junction_to.index[node_index]]}}})));\n')
    return(a.getvalue())
def model_connections(net, scale_factor, line_color, init):

    f = io.StringIO()
    # definition of the nodes
    junction_from = net.pipe.groupby(['from_junction']).size()
    nodes_from = []
    for i in range(len(junction_from)):
        if 2 == junction_from.values[i]:
            nodes_from.append(junction_from.index[i])
    junction_to = net.pipe.groupby(['to_junction']).size()
    nodes_to = []
    for i in range(len(junction_to)):
        if 2 == junction_to.values[i]:
            nodes_from.append(junction_to.index[i])
    #geodata
    node_geodata = node_placement(net, scale_factor)
    pipes_geodata = pipes_placement(net, scale_factor)
    sink_geodata = model_placement(net, scale_factor, 'sink')
    ext_geodata = model_placement(net, scale_factor, 'ext_grid')

    #type of connection
    if line_color =='black':
        color = '{0,0,0}'
        thickness = '0.25'
        model_in = 'inlet'
        model_out = 'outlet'
        pipe_inlet = 'inlet'
        pipe_outlet = 'outlet'
        node_in = 'inlet'
        node_out = 'outlet'

    if line_color == 'yellow':
        color = '{255,255,0}'
        thickness = '1.5'
        model_in = 'gasPort'
        model_out = 'gasPort'
        pipe_inlet = 'gasPortIn'
        pipe_outlet = 'gasPortOut'
        node_in = 'gasPort'
        node_out = 'gasPort'

    count_f = 0
    count_t = 0
    for i, row in net.junction.iterrows():
        if i in nodes_from:
            if i in net.pipe['from_junction']:
                pipes_from = net.pipe[net.pipe['from_junction'] == i]
                for b, row in pipes_from.iterrows():
                    count_f = + 1
                    f.write(f"connect(junction{i}.{node_out}{count_f},{pipes_from['name'][b]}.{pipe_inlet})"
                            f'annotation (Line(points='
                            f'{{ {{ {node_geodata["origin_x"].values[i]},{node_geodata["origin_y"].values[i]} }},'
                            f'{{ {pipes_geodata["origin_x"].values[b]},{pipes_geodata["origin_y"].values[b]} }} }},'
                            f'color={color}, thickness={thickness}));\n')

            if i in net.pipe['to_junction']:
                pipes_to = net.pipe[net.pipe['to_junction'] == i]
                for b, row in pipes_to.iterrows():
                    count_f = + 1
                    f.write(f'connect({pipes_to["name"][b]}.{pipe_outlet},junction{i}.{node_in}{count_f})' 
                            f'annotation (Line(points='
                            f'{{ {{ {pipes_geodata["origin_x"].values[b]},{pipes_geodata["origin_y"].values[b]} }},'
                            f'{{ {node_geodata["origin_x"].values[i]},{node_geodata["origin_y"].values[i]} }} }},'
                            f'color={color}, thickness={thickness}));\n')
            if i in net.ext_grid['junction']:
                ext_grid = net.ext_grid[net.ext_grid['junction'] == i]
                for b, row in ext_grid.iterrows():
                    count_f = + 1
                    f.write(f'connect({ext_grid["name"][b]}.{model_out},junction{i}.{node_in}{count_f});'
                            f'annotation (Line(points='
                            f'{{ {{ {ext_geodata["origin_x"].values[b]},{ext_geodata["origin_y"].values[b]} }},'
                            f'{{ {node_geodata["origin_x"].values[i]},{node_geodata["origin_y"].values[i]} }} }},'
                            f'color={color}, thickness={thickness}));\n')
            if i in net.sink['junction']:
                sink = net.sink[net.sink['junction'] == i]
                for b, row in sink.iterrows():
                    count_f = + 1
                    f.write(f'connect(junction{i}.{node_out}{count_f},{sink["name"][0]}.{model_in});'
                            f'annotation (Line(points='
                            f'{{ {{ {node_geodata["origin_x"].values[i]},{node_geodata["origin_y"].values[i]} }},'
                            f'{{ {sink_geodata["origin_x"].values[b]},{sink_geodata["origin_y"].values[b]} }} }},'
                            f'color={color}, thickness={thickness}));\n')
        elif i in nodes_to:
            if i in net.pipe['to_junction']:
                pipes_to = net.pipe[net.pipe['to_junction'] == i]
                for b, row in pipes_to.iterrows():
                    count_t += 1
                    f.write(f'connect({pipes_to["name"][b]}.{pipe_outlet},junction{i}.{node_in}{count_t})'
                            f'annotation (Line(points='
                            f'{{ {{ {node_geodata["origin_x"].values[i]},{node_geodata["origin_y"].values[i]} }},'
                            f'{{ {pipes_geodata["origin_x"].values[b]},{pipes_geodata["origin_y"].values[b]} }} }},'
                            f'color={color}, thickness={thickness}));\n')
            if i in net.pipe['from_junction']:
                pipes_from = net.pipe[net.pipe['from_junction'] == i]
                for b, row in pipes_from.iterrows():
                    f.write(f'connect(junction{i}.{node_out},{pipes_from["name"][b]}.{pipe_inlet})'
                            f'annotation (Line(points='
                            f'{{ {{ {node_geodata["origin_x"].values[i]},{node_geodata["origin_y"].values[i]} }},'
                            f'{{ {pipes_geodata["origin_x"].values[b]},{pipes_geodata["origin_y"].values[b]} }} }},'
                            f'color={color}, thickness={thickness}));\n')
            if i in net.ext_grid['junction']:
                ext_grid = net.ext_grid[net.ext_grid['junction'] == i]
                count_t =+1
                f.write(f'connect({ext_grid["name"][0]}.{model_out},junction{i}.{node_in}{count_t})'
                        f'annotation (Line(points='
                        f'{{ {{ {node_geodata["origin_x"].values[i]},{node_geodata["origin_y"].values[i]} }},'
                        f'{{ {pipes_geodata["origin_x"].values[b]},{pipes_geodata["origin_y"].values[b]} }} }},'
                        f'color={color}, thickness={thickness}));\n')
            if i in net.sink['junction']:
                sink = net.sink[net.sink['junction'] == i]
                f.write(f'connect(junction{i}.{node_out}{2},{sink["name"][0]}.{model_in})'
                        f'annotation (Line(points='
                        f'{{ {{ {node_geodata["origin_x"].values[i]},{node_geodata["origin_y"].values[i]} }},'
                        f'{{ {sink_geodata["origin_x"].values[i]},{sink_geodata["origin_y"].values[i]} }} }},'
                        f'color={color}, thickness={thickness}));\n')


        else:
            pipes_from = net.pipe['name'].loc[net.pipe['from_junction'] == i]
            pipes_to = net.pipe['name'].loc[net.pipe['to_junction'] == i]
            if pipes_to.empty == False and pipes_from.empty == True:
                sink = net.sink['name'].loc[net.sink['junction'] == i]
                s_index = sink.index[0]
                pt_index = pipes_to.index[0]
                f.write(f'connect({pipes_to.values[0]}.{pipe_outlet},{sink.values[0]}.{model_in})'
                        f'annotation (Line(points='
                        f'{{ {{ {pipes_geodata["origin_x"].values[pt_index]},{pipes_geodata["origin_y"].values[pt_index]} }},'
                        f'{{ {sink_geodata["origin_x"].values[s_index]},{sink_geodata["origin_y"].values[s_index]} }} }},'
                        f'color={color}, thickness={thickness}));\n')
            elif pipes_from.empty == False and pipes_to.empty == True:
                ext_grid = net.ext_grid['name'].loc[net.ext_grid['junction'] == i]
                e_index = ext_grid.index[0]
                pf_index = pipes_from.index[0]
                f.write(f'connect({ext_grid.values[0]}.{model_out},{pipes_from.values[0]}.{pipe_inlet})'
                        f'annotation (Line(points='
                        f'{{ {{ {ext_geodata["origin_x"].values[e_index]},{ext_geodata["origin_y"].values[e_index]} }},'
                        f'{{ {pipes_geodata["origin_x"].values[pf_index]},{pipes_geodata["origin_y"].values[pf_index]} }} }},'
                        f'color={color}, thickness={thickness}));\n')
            elif pipes_from.empty == False and pipes_to.empty == False:
                pf_index = pipes_from.index[0]
                pt_index = pipes_from.index[0]
                f.write(f'connect({pipes_to.values[0]}.{pipe_outlet},{pipes_from.values[0]}.{pipe_inlet})'
                        f'annotation (Line(points='
                        f'{{ {{ {pipes_geodata["origin_x"].values[pt_index]},{pipes_geodata["origin_y"].values[pt_index]} }},'
                        f'{{ {pipes_geodata["origin_x"].values[pf_index]},{pipes_geodata["origin_y"].values[pf_index]} }} }},'
                        f'color={color}, thickness={thickness}));\n')
            else:
                print('spezial conect')
    return (f.getvalue())