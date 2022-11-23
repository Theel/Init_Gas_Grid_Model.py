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
    size = [8*size_scale, 8*size_scale]
    a.write(f'annotation (Placement(transformation(\n'
            f'extent={{{{{size[0]},{size[1]*-1}}},{{{size[0]*-1},{size[1]}}} }}, \n'
            f'origin={{ {model_geodata.origin_x[model_index]} ,{model_geodata.origin_y[model_index]} }})));\n')
    return(a.getvalue())