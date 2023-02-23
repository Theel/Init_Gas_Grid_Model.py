from pandapower.control import ConstControl
from pandapower.control.basic_controller import Controller
from pandapipes.properties.fluids import get_fluid
from pandas.errors import InvalidIndexError

# taken and adapted from pandapipes.multinet.control.controller.multinet_control


class ControlCentralHeat(Controller):

    """
    A controller to be used in a DHN. Controls the heat generation based on the temperature at the critical end user

    This controller couples a gas network (from pandapipes) and a power network (from
    pandapower) that are stored in a multinet. Requires one or multiple 'sink' elements in the gas
    net and as many corresponding 'sgen'/'gen' elements in the power net.
    If 'calc_gas_from_power' is False (default), it reads the gas mass consumption values
    of given 'sink' elements, applies the efficiency factor and unit conversions and writes the
    resulting power output to 'sgen' (default) or 'gen' elements in the power net.
    If 'calc_gas_from_power' is True, it reads the power output of
    given 'sgen' (default) or 'gen' elements, calculates the corresponding gas consumption by
    appling the efficiency factor and unit conversions, and writes the resulting gas consumption
    mass flow to the given 'sink' elements in the gas net.
    It is stored in the controller-DataFrame of the multinet (multinet.controller).
    It is run by run_control_multinet.run_control() or within
    run_time_series_multinet.run_timeseries().

    :param multinet: pandapipes-Mulitnet that includes the power and gas network with sgen/gen and
                     sink elements
    :type multinet: attrdict (pandapipes.MultiNet)
    :param element_index_power: Index of one or more elements in the power net from which
                                the power generation will be read from or written to (either
                                'sgen' or 'gen' elements, as defined by element_type_power).
                                For each entry, a corresponding gas sink element has to be
                                provided in element_index_gas.
    :type element_index_power: int or iterable of integers
    :param element_index_gas: Index of one or more sink elements in the gas net from which the
                              G2P units' gas consumption (mass flow) is read from or written to.
                              For each sink element, a corresponding sgen/gen element has to be
                              provided in element_index_power.
    :type element_index_gas: int or iterable of integers
    :param efficiency: constant efficiency factor (default: based on HHV)
    :type efficiency: float
    :param name_power_net: Key name to find the power net in multinet['nets']
    :type name_power_net: str
    :param name_gas_net: Key name to find the gas net in multinet['nets']
    :type name_gas_net: str
    :param element_type_power: type of the corresponding power generation units, either 'sgen' or 'gen'
    :type element_type_power: str
    :param in_service: Indicates if the controllers are currently in_service
    :type in_service: bool
    :param order: within the same level, controllers with lower order are called before controllers
                  with numerical higher order
    :type order: int or float
    :param level: level to which the controller belongs. Low level is called before higher level.
                  Respective run function for the nets are called at least once per level.
    :type level: int or float
    :param drop_same_existing_ctrl: Indicates if already existing controllers of the same type and
                                    with the same matching parameters (e.g. at same element) should
                                    be dropped
    :type drop_same_existing_ctrl: bool
    :param initial_run: Whether a power and pipe flow should be run before the control step is
                        applied or not
    :type initial_run: bool
    :param main_product: (default: 'heat') Specifies whether the heat or the electric power determines the gas
                            consumption
    :type main_product: str
    :param kwargs: optional additional controller arguments that were implemented by users
    :type kwargs: any
    """

    def __init__(self, heat, element_index_heat, critical_enduser_index, element_type_heat="heat_exchanger",
                 variable='temperature', min_temp_k_end_user=320, max_temp_k_end_user=340, min_pressure_lift_bar=2,
                 max_pressure_lift_bar=10, max_mass_flow_kg_per_s=100, min_mass_flow_kg_per_s=10,
                 pressure_variation_bar=0.1, mass_flow_variation_kg_per_s=0.5, temperature_variation_k=1,
                 in_service=True, order=0, level=0, drop_same_existing_ctrl=False, initial_run=True, **kwargs):
        """
        see class docstring
        """
        super().__init__(heat, in_service, order, level,
                         drop_same_existing_ctrl=drop_same_existing_ctrl, initial_run=initial_run,
                         **kwargs)

        self.elm_idx_heat = element_index_heat
        self.crit_eu_idx = critical_enduser_index
        self.elm_type_heat = element_type_heat
        self.variable = variable
        self.min_temp_k_end_user = min_temp_k_end_user
        self.max_temp_k_end_user = max_temp_k_end_user
        self.max_temp_supply_k = 150 + 273.15
        self.min_temp_supply_k = 50 + 273.15
        self.next_temp_at_gen_supply = max_temp_k_end_user
        self.next_mass_flow_kg_per_s_at_gen = 0
        self.next_pressure_lift_bar_at_gen = 0
        self.min_pressure_lift = min_pressure_lift_bar
        self.max_pressure_lift = max_pressure_lift_bar
        self.min_mass_flow = min_mass_flow_kg_per_s
        self.max_mass_flow = max_mass_flow_kg_per_s
        self.pressure_var = pressure_variation_bar
        self.massflow_var = mass_flow_variation_kg_per_s
        self.temperature_var = temperature_variation_k
        self.mdot_kg_per_s = None
        self.applied = False
        self.change_temp = False
        self.change_pressure = False
        self.change_mass_flow = False

    def initialize_control(self, heat):
        # is needed if you want to call "control step" not only once but in each time step. I. e. constant controllers
        # dont need this function. However real controllers need it. If applied is false, the
        self.change_temp = False
        self.change_pressure = False
        self.change_mass_flow = False
        self.applied = False

    def control_step(self, heat):
        # junction index of return line of critical end user
        if self.crit_eu_idx is None:
            ce_idx = heat.res_heat_exchanger.t_from_k.idxmin()
            crit_eu_return_idx = heat["heat_exchanger"].at[ce_idx, 'to_junction']
        else:
            crit_eu_return_idx = heat["heat_exchanger"].at[self.crit_eu_idx, 'to_junction']
        # junction index of supply line of specified heat generation unit
        if self.elm_type_heat == 'heat_exchanger':
            producer_supply_idx = heat["heat_exchanger"].at[self.elm_idx_heat, 'to_junction']
        elif self.elm_type_heat == 'circ_pump_mass' or self.elm_type_heat == 'circ_pump_pressure':
            producer_supply_idx = heat[self.elm_type_heat].at[self.elm_idx_heat, 'flow_junction']
        else:
            producer_supply_idx = None
            print('unknown producer type')
        # return temperature of the critical end user
        t_k_crit = heat["res_junction"].at[crit_eu_return_idx, 't_k']
        if self.variable == 'temperature':
            # we control the temperature in order to increase the heat transported to the end-user
            # temperature at last time step
            last_temp_at_gen_supply = heat["res_junction"].at[producer_supply_idx, 't_k']
            if t_k_crit < self.min_temp_k_end_user:
                self.next_temp_at_gen_supply = last_temp_at_gen_supply + self.temperature_var
                self.change_temp = True
            elif t_k_crit > self.max_temp_k_end_user:
                self.next_temp_at_gen_supply = last_temp_at_gen_supply - self.temperature_var
                self.change_temp = True
        else:
            # we control the mass flow or pressure in order to increase the heat transported to the end-user
            if self.elm_type_heat == "circ_pump_mass":
                current_mass_flow_kg_per_s_at_gen = heat["res_circ_pump_mass"].at[self.elm_idx_heat, 'mdot_flow_kg_per_s']
                if t_k_crit < self.min_temp_k_end_user:
                    self.next_mass_flow_kg_per_s_at_gen = current_mass_flow_kg_per_s_at_gen + self.massflow_var
                    self.change_mass_flow = True
                elif t_k_crit > self.max_temp_k_end_user:
                    self.next_mass_flow_kg_per_s_at_gen = current_mass_flow_kg_per_s_at_gen - self.massflow_var
                    self.change_mass_flow = True
                self.next_mass_flow_kg_per_s_at_gen = max(self.next_mass_flow_kg_per_s_at_gen, self.min_mass_flow)
                if self.next_mass_flow_kg_per_s_at_gen > self.max_mass_flow:
                    self.next_mass_flow_kg_per_s_at_gen = self.max_mass_flow
                    current_temp_at_gen_supply = heat["circ_pump_mass"].at[self.elm_idx_heat, 't_flow_k']
                    self.next_temp_at_gen_supply = current_temp_at_gen_supply + self.temperature_var
                    self.change_temp = True
            else:
                current_pressure_lift_bar_at_gen = heat["res_circ_pump_pressure"].at[
                    self.elm_idx_heat, 'deltap_bar']
                if t_k_crit < self.min_temp_k_end_user:
                    self.next_pressure_lift_bar_at_gen = current_pressure_lift_bar_at_gen + self.pressure_var
                    self.change_pressure = True
                elif t_k_crit > self.max_temp_k_end_user:
                    self.next_pressure_lift_bar_at_gen = current_pressure_lift_bar_at_gen - self.pressure_var
                    self.change_pressure = True
                self.next_pressure_lift_bar_at_gen = max(self.next_pressure_lift_bar_at_gen, self.min_pressure_lift)
                if self.next_pressure_lift_bar_at_gen > self.max_pressure_lift:
                    self.next_pressure_lift_bar_at_gen = self.max_pressure_lift
                    current_temp_at_gen_supply = heat["circ_pump_pressure"].at[self.elm_idx_heat, 't_flow_k']
                    self.next_temp_at_gen_supply = current_temp_at_gen_supply + self.temperature_var
                    self.change_temp = True
        self.next_temp_at_gen_supply = min(max(self.min_temp_supply_k, self.next_temp_at_gen_supply),
                                           self.max_temp_supply_k)
        self.write_to_net(heat)
        self.applied = True

    def write_to_net(self, heat):
        if self.change_temp:
            if self.elm_type_heat == 'heat_exchanger':
                print('so far missing')
            elif self.elm_type_heat == 'circ_pump_mass' or self.elm_type_heat == 'circ_pump_pressure':
                heat[self.elm_type_heat].t_flow_k[self.elm_idx_heat] = self.next_temp_at_gen_supply
            else:
                print('unknown heat producer type')
        if self.change_pressure:
            heat.circ_pump_pressure.plift_bar[self.elm_idx_heat] = self.next_pressure_lift_bar_at_gen
        if self.change_mass_flow:
            heat.circ_pump_mass.mdot_flow_kg_per_s[self.elm_idx_heat] = self.next_mass_flow_kg_per_s_at_gen

    def is_converged(self, multinet):
        return self.applied

