import matplotlib.pyplot as plt
import numpy as np

# for the output writer functionalities
import pandapipes as ppipes
import pandapower as ppower
from os.path import join, dirname
from pandapower.timeseries import OutputWriter
import math
from math import sqrt
#from gridplanning import ArrayOrScalar, Scalar
import pandas as pd

def timesteps_to_list(dataframe, steps):
    timelist = dataframe.index.tolist()
    idx = [timelist.index(x) for x in steps]
    start_step = min(idx)
    end_step = max(idx) + 1
    return start_step, end_step


def plot_results(time, y_values, y_label, y_axis_label, start_k=0, end_k=40000, font_size=22, label_loc: int=0, ylim_bottom=None, ylim_top=None):
    if not y_values.shape[1] == len(y_label):
        raise ValueError('lists do not have the same length')
    # ensure end_k is in range
    end_k = min(end_k, time.shape[0])

    # create figure
    fig, ax = plt.subplots(figsize=(12, 6))

    # Set general font size
    plt.rcParams['font.size'] = '16'

    # Set tick font size
    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        label.set_fontsize(16)

    for name, y_value_idx in zip(y_label, range(y_values.shape[1])):
        ax.plot(time[start_k:end_k], y_values[start_k:end_k, y_value_idx], label=name)

    plt.xlabel('Time', fontsize=font_size)
    plt.ylabel(y_axis_label, fontsize=font_size)
    plt.xticks(rotation=45)

    ax.legend(loc=label_loc, prop={'size': font_size})

    if ylim_top is not None and ylim_bottom is not None:
        plt.ylim(bottom=ylim_bottom, top=ylim_top)
    plt.show()
    return 0


def load_watt_to_kg_per_s(load_watt, gcv_kwatt_h_per_cubicmeter=11.46, density_kg_per_cubicmeter=0.7):
    # inputs:
    #   heating load of a household in Watt
    #   gross calorific value in kWh/m^3
    #   density in kg/m^3
    
    # calculate gross calorifc value in Ws/m^3
    gcv_watt_s_cubicmeter = gcv_kwatt_h_per_cubicmeter * 1000 * 60 * 60
    load_kg_per_s = load_watt * density_kg_per_cubicmeter / gcv_watt_s_cubicmeter
    return load_kg_per_s


def energy_kg_to_mega_watt_h(energy_kg, gcv_kwatt_h_per_cubicmeter=11.46, density_kg_per_cubicmeter=0.7):
    # inputs:
    #   mass in kg
    #   gross calorific value in kWh/m^3
    #   density in kg/m^3
    return energy_kg / density_kg_per_cubicmeter * gcv_kwatt_h_per_cubicmeter


def create_output_writers(nets, time_steps=None, gridplanning=False):
    if isinstance(nets, ppipes.multinet.multinet.MultiNet):
        ow = create_ow_multinet(nets, time_steps, gridplanning)
        return ow
    elif isinstance(nets, ppower.pandapowerNet) or isinstance(nets, ppipes.pandapipesNet):
        ow = create_ow_net(nets, time_steps, gridplanning)
        return ow
    else:
        print('unknown net type')
        return None


def create_ow_multinet(multinet, time_steps, gridplanning):
    nets = multinet["nets"]
    ows = dict()
    for key_net in nets.keys():
        ows[key_net] = {}
        if isinstance(nets[key_net], ppower.pandapowerNet):
            if gridplanning:
                log_variables = [('res_line', 'loading_percent'),
                                ('res_trafo', 'loading_percent'),
                                ('res_ext_grid', 'p_mw'),
                                ('res_ext_grid', 'q_mvar')]
                ow = OutputWriter(nets[key_net], time_steps=time_steps,
                                    log_variables=log_variables)
            else:
                log_variables = [('res_bus', 'vm_pu'),
                                ('res_line', 'loading_percent'),
                                ('res_trafo', 'loading_percent'),
                                ('res_line', 'i_ka'),
                                ('res_bus', 'p_mw'),
                                ('res_bus', 'q_mvar'),
                                ('res_load', 'p_mw'),
                                ('res_load', 'q_mvar'),
                                ('res_ext_grid', 'p_mw'),
                                ('res_ext_grid', 'q_mvar')]
                ow = OutputWriter(nets[key_net], time_steps=time_steps,
                                    log_variables=log_variables,
                                    output_path=join(dirname('__file__'),'timeseries', 'results', 'power'),
                                    output_file_type=".json")
            ows[key_net] = ow
        elif isinstance(nets[key_net], ppipes.pandapipesNet) and nets[key_net].fluid.is_gas:
            if gridplanning:
                log_variables = [('res_ext_grid', 'mdot_kg_per_s')]
                ow = OutputWriter(nets[key_net], time_steps=time_steps,
                                    log_variables=log_variables)
            else:
                log_variables = [('res_sink', 'mdot_kg_per_s'),
                                ('res_ext_grid', 'mdot_kg_per_s'),
                                ('res_pipe', 'v_mean_m_per_s'),
                                ('res_pipe', 'mdot_from_kg_per_s'),
                                ('res_junction', 'p_bar'),
                                ('res_junction', 't_k')]
                ow = OutputWriter(nets[key_net], time_steps=time_steps,
                                    log_variables=log_variables,
                                    output_path=join(dirname('__file__'), 'timeseries', 'results', 'gas'),
                                    output_file_type=".csv")
            ows[key_net] = ow
        elif isinstance(nets[key_net], ppipes.pandapipesNet) and  not nets[key_net].fluid.is_gas:
            if gridplanning:
                log_variables = [] 
                ow = OutputWriter(nets[key_net], time_steps=time_steps,
                                    log_variables=log_variables)
            else:
                log_variables = [('res_pipe', 'v_mean_m_per_s'),
                                ('res_pipe', 'mdot_from_kg_per_s'),
                                ('res_junction', 'p_bar'),
                                ('res_junction', 't_k'),
                                ('res_heat_exchanger', 'v_mean_m_per_s')
                                ]
                ow = OutputWriter(nets[key_net], time_steps=time_steps,
                                log_variables=log_variables,
                                output_path=join(dirname('__file__'), 'timeseries', 'results', 'heat'),
                                output_file_type=".csv")
            ows[key_net] = ow
        else:
            raise AttributeError("Could not create an output writer for nets of kind " + str(key_net))
    return ows


def create_ow_net(net, time_steps, gridplanning):
    if isinstance(net, ppower.pandapowerNet):
        log_variables = [('res_bus', 'vm_pu'),
                         ('res_line', 'loading_percent'),
                         ('res_trafo', 'loading_percent'),
                         ('res_line', 'i_ka'),
                         ('res_bus', 'p_mw'),
                         ('res_bus', 'q_mvar'),
                         ('res_load', 'p_mw'),
                         ('res_load', 'q_mvar')]
        ow = OutputWriter(net, time_steps=time_steps,
                          log_variables=log_variables,
                          output_path=join(dirname('__file__'),'timeseries', 'results', 'power'),
                          output_file_type=".csv")
    elif isinstance(net, ppipes.pandapipesNet) and net.fluid.is_gas:
        log_variables = [('res_sink', 'mdot_kg_per_s'),
                         ('res_ext_grid', 'mdot_kg_per_s'),
                         ('res_pipe', 'v_mean_m_per_s'),
                         ('res_pipe', 'mdot_from_kg_per_s'),
                         ('res_junction', 'p_bar'),
                         ('res_junction', 't_k')]
        ow = OutputWriter(net, time_steps=time_steps,
                          log_variables=log_variables,
                          output_path=join(dirname('__file__'), 'timeseries', 'results', 'gas'),
                          output_file_type=".csv")
    elif isinstance(net, ppipes.pandapipesNet) and  not net.fluid.is_gas:
        log_variables = [('res_pipe', 'v_mean_m_per_s'),
                         ('res_pipe', 'mdot_from_kg_per_s'),
                         ('res_junction', 'p_bar'),
                         ('res_junction', 't_k'),
                         #('res_heat_exchanger', 'qext_w')
                         ]
        ow = OutputWriter(net, time_steps=time_steps,
                          log_variables=log_variables,
                          output_path=join(dirname('__file__'), 'timeseries', 'results', 'heat'),
                          output_file_type=".csv")
    else:
        raise AttributeError("Could not create an output writer for nets of kind " + str(type(net)))
    return ow


def calc_distance(geodata,from_junction,to_junction):
    distance = math.sqrt((geodata.x[from_junction] - geodata.x[to_junction])**2 + (geodata.y[from_junction] - geodata.y[to_junction])**2)
    return distance


def smooth_max(a,b, epsilon):
    # approximates the max function with a smooth function. See https://en.wikipedia.org/wiki/Smooth_maximum for more information
    return (a+b+sqrt((a-b)**2+epsilon))/2


def turn_dhn_edges_off(heat, turn_off_junction):
    turn_off_pipe = []
    turn_off_heat_exchanger = []
    for junction in turn_off_junction:
        turn_off_pipe = turn_off_pipe + heat.pipe.index[heat.pipe['from_junction'] == junction].to_list()
        turn_off_pipe = turn_off_pipe + heat.pipe.index[heat.pipe['to_junction'] == junction].to_list()
        turn_off_heat_exchanger = turn_off_heat_exchanger + heat.heat_exchanger.index[heat.heat_exchanger['from_junction'] == junction].to_list()
        turn_off_heat_exchanger = turn_off_heat_exchanger + heat.heat_exchanger.index[heat.heat_exchanger['to_junction'] == junction].to_list()
    heat.pipe.in_service[turn_off_pipe] = False
    heat.heat_exchanger.in_service[turn_off_heat_exchanger] = False
    heat.junction.in_service[turn_off_junction] = False


# def calc_cop(
#         temperature_source_celsius: np.ndarray,
#         t_supply_c: Scalar = 45,
#         coefficient: Scalar = 0.58,
#         delta_t: Scalar = 11.5,
#         part_load_coef: Scalar = 0.25,
#         part_load_ratio: ArrayOrScalar = 1
# ) -> ArrayOrScalar:
#     t_source_c = temperature_source_celsius.reshape([temperature_source_celsius.shape[0], 1])
#     t_source_k = t_source_c + 273.15
#     part_load = 1-part_load_coef*(1-part_load_ratio)
#     # check if it matches the model used in the transient library
#     cop = coefficient*np.multiply(np.divide((t_source_k-delta_t), (t_supply_c-t_source_c+2*delta_t)), part_load)
#     return np.clip(cop, 1, 10)

