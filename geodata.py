import pandapipes as pp
import pandas as pd
import example
import pandapipes.plotting as plot
import io

net = example.pipe_square_flat(fluid="lgas", p_junction=1.05, tfluid_K=293.15, pipe_d=0.3, pipe_l=1)

def point_zero_xy(net, factor = 40): # point zero (x=0, y=0) at the first ext grid location
    if net.fluid.is_gas == True:
        junction = net.ext_grid['junction'].loc[net.ext_grid.index[0]]
    elif net.fluid.is_gas == False:
        junction = net.circ_pump_mass['flow_junction'].loc[net.circ_pump_mass.index[0]]
    else:
       print("unknown Net")
    geodata = net.junction_geodata.loc[net.junction_geodata.index[junction]]
    point_zero = [geodata.x * factor, geodata.y * factor]
    return(point_zero)

def find_nodes(net):
    componentList = []
    for i in range(len(net.component_list)):
        componentList.append(net.component_list[i].__name__)
    junction_from = net.pipe.groupby(['from_junction']).size()
    junction_to = net.pipe.groupby(['to_junction']).size()
    all_connections = []
    connect = []
    all_nodes = []
    for i, row in net.junction.iterrows():
        connect = 0
        if i in junction_from:
            connect += junction_from[i]
        if i in junction_to:
            connect += junction_to[i]
        if "ExtGrid" in componentList:
            if i in net.ext_grid['junction'].values:
                connect += 1
        if "Sink" in componentList:
            if i in net.sink['junction'].values:
                connect += 1
        if "Source" in componentList:
            if i in net.source['junction'].values:
                connect += 1
        if "HeatExchanger" in componentList:
            if i in net.heat_exchanger['from_junction'].values or i in net.heat_exchanger['to_junction'].values:
                connect += 1
        if "CirculationPumpMass" in componentList:
            if i in net.circ_pump_mass['flow_junction'].values or i in net.circ_pump_mass['return_junction'].values:
                connect += 1



        if connect > 2:
            all_nodes.append(i)
            all_connections.append(connect)
    nodes = pd.DataFrame({'connections': all_connections}, index=all_nodes)
    return(nodes)
def pipes_placement(net, factor = 40):
    point_zero=point_zero_xy(net, factor)
    rotation = []
    origin_x = []
    origin_y = []
    #names=[]
    for i, row in net.pipe.iterrows():
        from_junction = net.pipe['from_junction'].loc[net.pipe.index[i]]
        to_junction = net.pipe['to_junction'].loc[net.pipe.index[i]]
        from_geodata = net.junction_geodata.loc[net.junction_geodata.index[from_junction]]
        to_geodata = net.junction_geodata.loc[net.junction_geodata.index[to_junction]]
        if to_geodata.y+0.01 > from_geodata.y and from_geodata.y > to_geodata.y-0.01:
            if to_geodata.x > from_geodata.x:
                rotation.append('0')
            else:
                rotation.append('180')
        else:
            if to_geodata.y > from_geodata.y:
                rotation.append('90')
            else:
                rotation.append('270')

        origin_x.append((to_geodata.x * 0.5 - from_geodata.x * (0.5 - 1)) * factor-point_zero[0])
        origin_y.append((to_geodata.y * 0.5 - from_geodata.y * (0.5 - 1)) * factor-point_zero[1])
    dict = {'names': net.pipe['name'].replace(" ", ""), 'origin_x': origin_x, 'origin_y': origin_y, 'rotation': rotation}
    geodata_pipe = pd.DataFrame(dict)
    return(geodata_pipe)

def gas_model_placement(net,factor=40, model='sink'):
    point_zero = point_zero_xy(net, factor)
    origin_x = []
    origin_y = []
    for i, row in net.junction.iterrows():
        if i in getattr(net, model)['junction']:
            junction = getattr(net, model)['junction'].loc[getattr(net, model).index[i]]
            geodata = net.junction_geodata.loc[net.junction_geodata.index[junction]]
            origin_x.append(geodata.x * factor-point_zero[0])
            origin_y.append(geodata.y * factor-point_zero[1])
    dict = {'names': getattr(net, model)['name'].replace(" ", ""), 'origin_x': origin_x, 'origin_y': origin_y}
    geodata = pd.DataFrame(dict)
    return(geodata)

def heat_model_placement(net,factor=40, model='heat_exchanger'):
    point_zero = point_zero_xy(net, factor)
    rotation = []
    origin_x = []
    origin_y = []
    if model=='heat_exchanger':
        junction_in = 'from_junction'
        junction_out = 'to_junction'
    else:
        junction_in = 'return_junction'
        junction_out = 'flow_junction'
    for i, row in getattr(net, model).iterrows():
        return_junction = getattr(net, model)[junction_in].loc[getattr(net, model).index[i]]
        flow_junction = getattr(net, model)[junction_out].loc[getattr(net, model).index[i]]
        return_geodata = net.junction_geodata.loc[net.junction_geodata.index[return_junction]]
        flow_geodata = net.junction_geodata.loc[net.junction_geodata.index[flow_junction]]
        if flow_geodata.y + 0.01 > return_geodata.y and return_geodata.y > flow_geodata.y - 0.01:
            if flow_geodata.x > return_geodata.x:
                rotation.append('0')
            else:
                rotation.append('180')
        else:
            if flow_geodata.y > return_geodata.y:
                rotation.append('90')
            else:
                rotation.append('270')

        origin_x.append((flow_geodata.x * 0.5 - return_geodata.x * (0.5 - 1)) * factor - point_zero[0])
        origin_y.append((flow_geodata.y * 0.5 - return_geodata.y * (0.5 - 1)) * factor - point_zero[1])
    dict = {'names': getattr(net, model)['name'].replace(" ", ""), 'origin_x': origin_x, 'origin_y': origin_y,
            'rotation': rotation}
    geodata = pd.DataFrame(dict)
    return (geodata)

def node_placement(net,factor=40):
    point_zero = point_zero_xy(net, factor)
    origin_x = []
    origin_y = []
    for i, row in net.junction.iterrows():
        geodata = net.junction_geodata.loc[i]
        origin_x.append(geodata.x * factor-point_zero[0])
        origin_y.append(geodata.y * factor-point_zero[1])
    dict = {'names': net.junction['name'].replace(" ", ""), 'origin_x': origin_x, 'origin_y': origin_y}
    geodata = pd.DataFrame(dict)
    return(geodata)


def placement_valves(net, factor, nodes_to):
    point_zero = point_zero_xy(net, factor)
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
                origin_x.append((to_geodata.x * 0.7 - from_geodata.x * (0.3 - 1)) * factor-point_zero[0])
                origin_y.append((to_geodata.y * 0.5 - from_geodata.y * (0.5 - 1)) * factor-point_zero[1])
            else:
                rotation.append('180')
                origin_x.append((to_geodata.x * 0.3 - from_geodata.x * (0.7 - 1)) * factor-point_zero[0])
                origin_y.append((to_geodata.y * 0.5 - from_geodata.y * (0.5 - 1)) * factor-point_zero[1])
        else:
            if to_geodata.y > from_geodata.y:
                rotation.append('90')
                origin_x.append((to_geodata.x * 0.5 - from_geodata.x * (0.5 - 1)) * factor-point_zero[0])
                origin_y.append((to_geodata.y * 0.7 - from_geodata.y * (0.3 - 1)) * factor-point_zero[1])
            else:
                rotation.append('270')
            origin_x.append((to_geodata.x*0.5 - from_geodata.x*(0.5-1))*factor-point_zero[0])
            origin_y.append((to_geodata.y*0.3 - from_geodata.y*(0.7-1))*factor-point_zero[1])
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
def gas_model_annotation(net, model_a='sink', xy_scale=40, size_scale=1, model_index=0):
    model_geodata = gas_model_placement(net, factor=xy_scale, model=model_a)
    a = io.StringIO()
    if model_a == 'sink':
        size = [8*size_scale, 8*size_scale]
    if model_a == 'ext_grid' or model_a == 'source':
        size = [-8*size_scale, -8*size_scale]
    a.write(f'annotation (Placement(transformation(\n'
            f'extent={{{{{size[0]},{size[1]*-1}}},{{{size[0]*-1},{size[1]}}} }}, \n'
            f'origin={{ {model_geodata.origin_x[model_index]} ,{model_geodata.origin_y[model_index]} }})));\n')
    return(a.getvalue())
def heat_model_annotation(net, model_a='sink', xy_scale=40, size_scale=1, model_index=0):
    model_geodata = heat_model_placement(net, factor=xy_scale, model=model_a)
    a = io.StringIO()
    size = [8*size_scale, 8*size_scale]
    a.write(f'annotation (Placement(transformation(\n'
            f'extent={{{{{size[0]},{size[1]*-1}}},{{{size[0]*-1},{size[1]}}} }}, \n'
            f'rotation={model_geodata.rotation[model_index]},\n'
            f'origin={{ {model_geodata.origin_x[model_index]} ,{model_geodata.origin_y[model_index]} }})));\n')
    return(a.getvalue())

def node_annotation(net, xy_scale, size_scale=1, node_to_from='node_to', node_index=1):
    node_geodata = node_placement(net, factor=xy_scale)
    #junction_from = net.pipe.groupby(['from_junction']).size()
    #junction_to = net.pipe.groupby(['to_junction']).size()
    a = io.StringIO()
    size = [9.5 * size_scale, 6 * size_scale]
    # if node_to_from == 'node_from':
    #     a.write(f'annotation (Placement(transformation(\n'
    #         f'extent={{{{{size[0]},{size[0]}}},{{{size[0]*-1},{size[1]*-1}}}}},\n'
    #         f'origin={{{node_geodata["origin_x"].loc[junction_from[node_index]]},{node_geodata["origin_y"].loc[junction_from[node_index]]}}})));\n')
    # if node_to_from == 'node_to':
    #     a.write(f'annotation (Placement(transformation(\n'
    #             f'extent={{{{{size[0]},{size[0]}}},{{{size[0] * -1},{size[1] * -1}}}}},\n'
    #             f'origin={{{node_geodata["origin_x"].loc[junction_to[node_index]]},{node_geodata["origin_y"].loc[junction_to[node_index]]}}})));\n')
    # if node_to_from == 'multi_in_out':
    a.write(f'annotation (Placement(transformation(\n'
            f'extent={{{{{size[0]},{size[0]}}},{{{size[0]*-1},{size[1]*-1}}}}},\n'
            f'origin={{{node_geodata["origin_x"].loc[node_index]},{node_geodata["origin_y"].loc[node_index]}}})));\n')
    return(a.getvalue())

def gas_connections(net, componentList, scale_factor, line_color):
    nodes = find_nodes(net)
    f = io.StringIO()
    #geodata
    node_geodata = node_placement(net, scale_factor)
    pipes_geodata = pipes_placement(net, scale_factor)
    sink_geodata = gas_model_placement(net, scale_factor, 'sink')
    ext_geodata = gas_model_placement(net, scale_factor, 'ext_grid')
    if 'Source' in componentList:
        source_geodata = gas_model_placement(net, scale_factor, 'source')

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


    for i, row in net.junction.iterrows():
        count = 0
        if i in nodes.index:

            if i in net.pipe['from_junction'].values:
                pipes_from = net.pipe[net.pipe['from_junction'] == i]
                for b, row in pipes_from.iterrows():
                    count += 1
                    pipe_name = pipes_from['name'][b].replace(" ", "")
                    f.write(f"connect(junction{i}.{node_out}[{count}],{pipe_name}.{pipe_inlet})"
                            f'annotation (Line(points='
                            f'{{ {{ {node_geodata["origin_x"].values[i]},{node_geodata["origin_y"].values[i]} }},'
                            f'{{ {pipes_geodata["origin_x"].values[b]},{pipes_geodata["origin_y"].values[b]} }} }},'
                            f'color={color}, thickness={thickness}));\n')

            if i in net.pipe['to_junction'].values:
                pipes_to = net.pipe[net.pipe['to_junction'] == i]
                for b, row in pipes_to.iterrows():
                    count += 1
                    pipe_name = pipes_to['name'][b].replace(" ", "")
                    f.write(f'connect({pipe_name}.{pipe_outlet},junction{i}.{node_in}[{count}])' 
                            f'annotation (Line(points='
                            f'{{ {{ {pipes_geodata["origin_x"].values[b]},{pipes_geodata["origin_y"].values[b]} }},'
                            f'{{ {node_geodata["origin_x"].values[i]},{node_geodata["origin_y"].values[i]} }} }},'
                            f'color={color}, thickness={thickness}));\n')
            if i in net.ext_grid['junction'].values:
                ext_grid = net.ext_grid[net.ext_grid['junction'] == i]
                for b, row in ext_grid.iterrows():
                    count += 1
                    ext_name = ext_grid["name"][b].replace(" ","")
                    f.write(f'connect({ext_name}.{model_out},junction{i}.{node_in}[{count}]);'
                            f'annotation (Line(points='
                            f'{{ {{ {ext_geodata["origin_x"].values[b]},{ext_geodata["origin_y"].values[b]} }},'
                            f'{{ {node_geodata["origin_x"].values[i]},{node_geodata["origin_y"].values[i]} }} }},'
                            f'color={color}, thickness={thickness}));\n')
            if 'Source' in componentList:
                if i in net.source['junction'].values:
                    source = net.source[net.source['junction'] == i]
                    for b, row in source.iterrows():
                        count += 1
                        source_name = source["name"][b].replace(" ","")
                        f.write(f'connect({source_name}.{model_out},junction{i}.{node_in}[{count}]);'
                                f'annotation (Line(points='
                                f'{{ {{ {source_geodata["origin_x"].values[b]},{source_geodata["origin_y"].values[b]} }},'
                                f'{{ {node_geodata["origin_x"].values[i]},{node_geodata["origin_y"].values[i]} }} }},'
                                f'color={color}, thickness={thickness}));\n')
            if 'Sink' in componentList:
                if i in net.sink['junction'].values:
                    sink = net.sink[net.sink['junction'] == i]
                    for b, row in sink.iterrows():
                        count += 1
                        sink_name = sink["name"][b].replace(" ","")
                        f.write(f'connect(junction{i}.{node_out}[{count}],{sink_name}.{model_in});'
                                f'annotation (Line(points='
                                f'{{ {{ {node_geodata["origin_x"].values[i]},{node_geodata["origin_y"].values[i]} }},'
                                f'{{ {sink_geodata["origin_x"].values[b]},{sink_geodata["origin_y"].values[b]} }} }},'
                                f'color={color}, thickness={thickness}));\n')

        else:
            pipes_from = net.pipe['name'].loc[net.pipe['from_junction'] == i]
            pipes_to = net.pipe['name'].loc[net.pipe['to_junction'] == i]
            if pipes_to.empty == False and pipes_from.empty == True:
                sink = net.sink['name'].loc[net.sink['junction'] == i]
                if 'Source' in componentList:
                    source = net.source['name'].loc[net.source['junction'] == i]
                ext_grid = net.ext_grid['name'].loc[net.ext_grid['junction'] == i]
                pipe_name = pipes_to.values[0].replace(" ","")
                if sink.empty == False:
                    s_index = sink.index[0]
                    pt_index = pipes_to.index[0]
                    sink_name = sink.values[0].replace(" ","")
                    f.write(f'connect({pipe_name}.{pipe_outlet},{sink_name}.{model_in})'
                            f'annotation (Line(points='
                            f'{{ {{ {pipes_geodata["origin_x"].values[pt_index]},{pipes_geodata["origin_y"].values[pt_index]} }},'
                            f'{{ {sink_geodata["origin_x"].values[s_index]},{sink_geodata["origin_y"].values[s_index]} }} }},'
                            f'color={color}, thickness={thickness}));\n')
                if ext_grid.empty == False:
                    e_index = ext_grid.index[0]
                    pt_index = pipes_to.index[0]
                    ext_name = ext_grid.values[0].replace(" ", "")
                    f.write(f'connect({pipe_name}.{pipe_outlet},{ext_name}.{model_out})'
                            f'annotation (Line(points='
                            f'{{ {{ {ext_geodata["origin_x"].values[e_index]},{ext_geodata["origin_y"].values[e_index]} }},'
                            f'{{ {pipes_geodata["origin_x"].values[pt_index]},{pipes_geodata["origin_y"].values[pt_index]} }} }},'
                            f'color={color}, thickness={thickness}));\n')
                if 'Source' in componentList:
                    if source.empty == False:
                        source_index = source.index[0]
                        pt_index = pipes_to.index[0]
                        source_name = source.values[0].replace(" ", "")
                        f.write(f'connect({pipe_name}.{pipe_outlet},{ext_name}.{model_out})'
                                f'annotation (Line(points='
                                f'{{ {{ {source_geodata["origin_x"].values[source_index]},{source_geodata["origin_y"].values[source_index]} }},'
                                f'{{ {pipes_geodata["origin_x"].values[pt_index]},{pipes_geodata["origin_y"].values[pt_index]} }} }},'
                                f'color={color}, thickness={thickness}));\n')
            elif pipes_from.empty == False and pipes_to.empty == True:
                ext_grid = net.ext_grid['name'].loc[net.ext_grid['junction'] == i]
                if 'Source' in componentList:
                    source = net.source['name'].loc[net.source['junction'] == i]
                sink = net.sink['name'].loc[net.sink['junction'] == i]
                pipe_name = pipes_from.values[0].replace(" ", "")
                if ext_grid.empty == False:
                    e_index = ext_grid.index[0]
                    pf_index = pipes_from.index[0]
                    ext_name = ext_grid.values[0].replace(" ", "")
                    f.write(f'connect({ext_name}.{model_out},{pipe_name}.{pipe_inlet})'
                            f'annotation (Line(points='
                            f'{{ {{ {ext_geodata["origin_x"].values[e_index]},{ext_geodata["origin_y"].values[e_index]} }},'
                            f'{{ {pipes_geodata["origin_x"].values[pf_index]},{pipes_geodata["origin_y"].values[pf_index]} }} }},'
                            f'color={color}, thickness={thickness}));\n')
                if 'Source' in componentList:
                    if source.empty == False:
                        source_index = source.index[0]
                        pf_index = pipes_from.index[0]
                        source_name = source.values[0].replace(" ", "")
                        f.write(f'connect({source_name}.{model_out},{pipe_name}.{pipe_inlet})'
                                f'annotation (Line(points='
                                f'{{ {{ {source_geodata["origin_x"].values[source_index]},{source_geodata["origin_y"].values[source_index]} }},'
                                f'{{ {pipes_geodata["origin_x"].values[pf_index]},{pipes_geodata["origin_y"].values[pf_index]} }} }},'
                                f'color={color}, thickness={thickness}));\n')
                if sink.empty == False:
                    s_index = sink.index[0]
                    pf_index = pipes_from.index[0]
                    sink_name = sink.values[0].replace(" ", "")
                    f.write(f'connect({sink_name}.{model_in},{pipe_name}.{pipe_inlet})'
                            f'annotation (Line(points='
                            f'{{ {{ {pipes_geodata["origin_x"].values[pf_index]},{pipes_geodata["origin_y"].values[pf_index]} }},'
                            f'{{ {sink_geodata["origin_x"].values[s_index]},{sink_geodata["origin_y"].values[s_index]} }} }},'
                            f'color={color}, thickness={thickness}));\n')
            elif pipes_from.empty == False and pipes_to.empty == False:
                pf_index = pipes_from.index[0]
                pt_index = pipes_from.index[0]
                pipe_to_name = pipes_to.values[0].replace(" ", "")
                pipe_from_name = pipes_from.values[0].replace(" ", "")
                f.write(f'connect({pipe_to_name}.{pipe_outlet},{pipe_from_name}.{pipe_inlet})'
                        f'annotation (Line(points='
                        f'{{ {{ {pipes_geodata["origin_x"].values[pt_index]},{pipes_geodata["origin_y"].values[pt_index]} }},'
                        f'{{ {pipes_geodata["origin_x"].values[pf_index]},{pipes_geodata["origin_y"].values[pf_index]} }} }},'
                        f'color={color}, thickness={thickness}));\n')
            else:
                print('spezial conect')
    return (f.getvalue())

def heat_connections(net, componentList, scale_factor, line_color):
    nodes = find_nodes(net)
    f = io.StringIO()
    #geodata
    node_geodata = node_placement(net, scale_factor)
    pipes_geodata = pipes_placement(net, scale_factor)
    heat_exchanger_geodata = heat_model_placement(net, scale_factor, 'heat_exchanger')
    circ_pump_geodata = heat_model_placement(net, scale_factor, 'circ_pump_mass')
    if 'Source' in componentList:
        source_geodata = heat_model_placement(net, scale_factor, 'source')

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

    if line_color =='blue':
        color = '{0,0,0}'
        thickness = '0.25'
        model_in = 'inlet'
        model_out = 'outlet'
        pipe_inlet = 'inlet'
        pipe_outlet = 'outlet'
        node_in = 'inlet'
        node_out = 'outlet'


    for i, row in net.junction.iterrows():
        count = 0
        if i in nodes.index:

            if i in net.pipe['from_junction'].values:
                pipes_from = net.pipe[net.pipe['from_junction'] == i]
                for b, row in pipes_from.iterrows():
                    count += 1
                    pipe_name = pipes_from['name'][b].replace(" ", "")
                    f.write(f"connect(junction{i}.{node_out}[{count}],{pipe_name}.{pipe_inlet})"
                            f'annotation (Line(points='
                            f'{{ {{ {node_geodata["origin_x"].values[i]},{node_geodata["origin_y"].values[i]} }},'
                            f'{{ {pipes_geodata["origin_x"].values[b]},{pipes_geodata["origin_y"].values[b]} }} }},'
                            f'color={color}, thickness={thickness}));\n')

            if i in net.pipe['to_junction'].values:
                pipes_to = net.pipe[net.pipe['to_junction'] == i]
                for b, row in pipes_to.iterrows():
                    count += 1
                    pipe_name = pipes_to['name'][b].replace(" ", "")
                    f.write(f'connect({pipe_name}.{pipe_outlet},junction{i}.{node_in}[{count}])' 
                            f'annotation (Line(points='
                            f'{{ {{ {pipes_geodata["origin_x"].values[b]},{pipes_geodata["origin_y"].values[b]} }},'
                            f'{{ {node_geodata["origin_x"].values[i]},{node_geodata["origin_y"].values[i]} }} }},'
                            f'color={color}, thickness={thickness}));\n')
            if i in net.ext_grid['junction'].values:
                ext_grid = net.ext_grid[net.ext_grid['junction'] == i]
                for b, row in ext_grid.iterrows():
                    count += 1
                    ext_name = ext_grid["name"][b].replace(" ","")
                    f.write(f'connect({ext_name}.{model_out},junction{i}.{node_in}[{count}]);'
                            f'annotation (Line(points='
                            f'{{ {{ {ext_geodata["origin_x"].values[b]},{ext_geodata["origin_y"].values[b]} }},'
                            f'{{ {node_geodata["origin_x"].values[i]},{node_geodata["origin_y"].values[i]} }} }},'
                            f'color={color}, thickness={thickness}));\n')
            if 'Source' in componentList:
                if i in net.source['junction'].values:
                    source = net.source[net.source['junction'] == i]
                    for b, row in source.iterrows():
                        count += 1
                        source_name = source["name"][b].replace(" ","")
                        f.write(f'connect({source_name}.{model_out},junction{i}.{node_in}[{count}]);'
                                f'annotation (Line(points='
                                f'{{ {{ {source_geodata["origin_x"].values[b]},{source_geodata["origin_y"].values[b]} }},'
                                f'{{ {node_geodata["origin_x"].values[i]},{node_geodata["origin_y"].values[i]} }} }},'
                                f'color={color}, thickness={thickness}));\n')
            if 'Sink' in componentList:
                if i in net.sink['junction'].values:
                    sink = net.sink[net.sink['junction'] == i]
                    for b, row in sink.iterrows():
                        count += 1
                        sink_name = sink["name"][b].replace(" ","")
                        f.write(f'connect(junction{i}.{node_out}[{count}],{sink_name}.{model_in});'
                                f'annotation (Line(points='
                                f'{{ {{ {node_geodata["origin_x"].values[i]},{node_geodata["origin_y"].values[i]} }},'
                                f'{{ {sink_geodata["origin_x"].values[b]},{sink_geodata["origin_y"].values[b]} }} }},'
                                f'color={color}, thickness={thickness}));\n')

        else:
            pipes_from = net.pipe['name'].loc[net.pipe['from_junction'] == i]
            pipes_to = net.pipe['name'].loc[net.pipe['to_junction'] == i]
            if pipes_to.empty == False and pipes_from.empty == True:
                sink = net.sink['name'].loc[net.sink['junction'] == i]
                if 'Source' in componentList:
                    source = net.source['name'].loc[net.source['junction'] == i]
                ext_grid = net.ext_grid['name'].loc[net.ext_grid['junction'] == i]
                pipe_name = pipes_to.values[0].replace(" ","")
                if sink.empty == False:
                    s_index = sink.index[0]
                    pt_index = pipes_to.index[0]
                    sink_name = sink.values[0].replace(" ","")
                    f.write(f'connect({pipe_name}.{pipe_outlet},{sink_name}.{model_in})'
                            f'annotation (Line(points='
                            f'{{ {{ {pipes_geodata["origin_x"].values[pt_index]},{pipes_geodata["origin_y"].values[pt_index]} }},'
                            f'{{ {sink_geodata["origin_x"].values[s_index]},{sink_geodata["origin_y"].values[s_index]} }} }},'
                            f'color={color}, thickness={thickness}));\n')
                if ext_grid.empty == False:
                    e_index = ext_grid.index[0]
                    pt_index = pipes_to.index[0]
                    ext_name = ext_grid.values[0].replace(" ", "")
                    f.write(f'connect({pipe_name}.{pipe_outlet},{ext_name}.{model_out})'
                            f'annotation (Line(points='
                            f'{{ {{ {ext_geodata["origin_x"].values[e_index]},{ext_geodata["origin_y"].values[e_index]} }},'
                            f'{{ {pipes_geodata["origin_x"].values[pt_index]},{pipes_geodata["origin_y"].values[pt_index]} }} }},'
                            f'color={color}, thickness={thickness}));\n')
                if 'Source' in componentList:
                    if source.empty == False:
                        source_index = source.index[0]
                        pt_index = pipes_to.index[0]
                        source_name = source.values[0].replace(" ", "")
                        f.write(f'connect({pipe_name}.{pipe_outlet},{ext_name}.{model_out})'
                                f'annotation (Line(points='
                                f'{{ {{ {source_geodata["origin_x"].values[source_index]},{source_geodata["origin_y"].values[source_index]} }},'
                                f'{{ {pipes_geodata["origin_x"].values[pt_index]},{pipes_geodata["origin_y"].values[pt_index]} }} }},'
                                f'color={color}, thickness={thickness}));\n')
            elif pipes_from.empty == False and pipes_to.empty == True:
                ext_grid = net.ext_grid['name'].loc[net.ext_grid['junction'] == i]
                if 'Source' in componentList:
                    source = net.source['name'].loc[net.source['junction'] == i]
                sink = net.sink['name'].loc[net.sink['junction'] == i]
                pipe_name = pipes_from.values[0].replace(" ", "")
                if ext_grid.empty == False:
                    e_index = ext_grid.index[0]
                    pf_index = pipes_from.index[0]
                    ext_name = ext_grid.values[0].replace(" ", "")
                    f.write(f'connect({ext_name}.{model_out},{pipe_name}.{pipe_inlet})'
                            f'annotation (Line(points='
                            f'{{ {{ {ext_geodata["origin_x"].values[e_index]},{ext_geodata["origin_y"].values[e_index]} }},'
                            f'{{ {pipes_geodata["origin_x"].values[pf_index]},{pipes_geodata["origin_y"].values[pf_index]} }} }},'
                            f'color={color}, thickness={thickness}));\n')
                if 'Source' in componentList:
                    if source.empty == False:
                        source_index = source.index[0]
                        pf_index = pipes_from.index[0]
                        source_name = source.values[0].replace(" ", "")
                        f.write(f'connect({source_name}.{model_out},{pipe_name}.{pipe_inlet})'
                                f'annotation (Line(points='
                                f'{{ {{ {source_geodata["origin_x"].values[source_index]},{source_geodata["origin_y"].values[source_index]} }},'
                                f'{{ {pipes_geodata["origin_x"].values[pf_index]},{pipes_geodata["origin_y"].values[pf_index]} }} }},'
                                f'color={color}, thickness={thickness}));\n')
                if sink.empty == False:
                    s_index = sink.index[0]
                    pf_index = pipes_from.index[0]
                    sink_name = sink.values[0].replace(" ", "")
                    f.write(f'connect({sink_name}.{model_in},{pipe_name}.{pipe_inlet})'
                            f'annotation (Line(points='
                            f'{{ {{ {pipes_geodata["origin_x"].values[pf_index]},{pipes_geodata["origin_y"].values[pf_index]} }},'
                            f'{{ {sink_geodata["origin_x"].values[s_index]},{sink_geodata["origin_y"].values[s_index]} }} }},'
                            f'color={color}, thickness={thickness}));\n')
            elif pipes_from.empty == False and pipes_to.empty == False:
                pf_index = pipes_from.index[0]
                pt_index = pipes_from.index[0]
                pipe_to_name = pipes_to.values[0].replace(" ", "")
                pipe_from_name = pipes_from.values[0].replace(" ", "")
                f.write(f'connect({pipe_to_name}.{pipe_outlet},{pipe_from_name}.{pipe_inlet})'
                        f'annotation (Line(points='
                        f'{{ {{ {pipes_geodata["origin_x"].values[pt_index]},{pipes_geodata["origin_y"].values[pt_index]} }},'
                        f'{{ {pipes_geodata["origin_x"].values[pf_index]},{pipes_geodata["origin_y"].values[pf_index]} }} }},'
                        f'color={color}, thickness={thickness}));\n')
            else:
                print('spezial conect')
    return (f.getvalue())