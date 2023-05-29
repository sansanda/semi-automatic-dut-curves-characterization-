import logging
import sys
import time
from time import sleep
from pymeasure.instruments.tektronix.tek371A import Tektronix371A

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class TektronixCurveTracer:
    """ Represents a generic Tektronix Curve Tracer
    and provides a high-level interface for interacting with
    the instrument using the SCPI command set.

    .. code-block:: python

    tct = TektronixCurveTracer("GPIB0::23::INSTR")

    print(tct.id)

    """

    VALID_PEAK_POWER = [300, 3000]
    N_HORIZONTAL_DIVS = 10
    N_VERTICAL_DIVS = 10

    STEPGEN_MIN_OFFSET = 0.0
    STEPGEN_OFFSET_RESOLUTION = 0.01

    COLLECTOR_SUPPLY_RESOLUTION = 0.1

    def __init__(self, concrete_tek_ct=Tektronix371A):
        self.concrete_tek_ct = concrete_tek_ct

    def initialize(self):

        self.concrete_tek_ct.initialize()
        time.sleep(2)
        # COLLECTOR SUPPLY
        self.concrete_tek_ct.cs_peakpower = 300
        self.concrete_tek_ct.cs_polarity = "POS"
        self.concrete_tek_ct.cs_collector_supply = 0
        # STEP GEN
        self.concrete_tek_ct.stepgen_step_source_and_size = ("VOLTAGE", 5.0)
        self.concrete_tek_ct.stepgen_number_steps = 0
        self.concrete_tek_ct.stepgen_offset = 0
        # DISPLAY
        self.concrete_tek_ct.diplay_store_mode = "STO"
        self.concrete_tek_ct.display_horizontal_source_sensitivity = ("COLLECT", 1.0E-1)
        self.concrete_tek_ct.display_vertical_source_sensitivity = ("COLLECT", 500.0E-3)
        self.concrete_tek_ct.set_cursor_mode("DOT", 1)
        # MEASUREMENT
        self.concrete_tek_ct.measure_mode = "REP"

    def initialize_per_3Q_measure(self,
                                  peakpower=3000,
                                  step_gen_offset=0,
                                  vertical_sens=2.0,
                                  horizontal_sens=0.5):

        # COLLECTOR SUPPLY
        self.concrete_tek_ct.cs_peakpower = peakpower
        self.concrete_tek_ct.cs_polarity = "NEG"
        self.concrete_tek_ct.cs_collector_supply = 0
        # STEP GEN
        self.concrete_tek_ct.stepgen_step_source_and_size = ("VOLTAGE", 5.0)
        self.concrete_tek_ct.stepgen_number_steps = 0
        self.concrete_tek_ct.stepgen_offset = step_gen_offset
        # DISPLAY
        self.concrete_tek_ct.diplay_store_mode = "STO"
        self.concrete_tek_ct.display_horizontal_source_sensitivity = ("COLLECT", horizontal_sens)
        self.concrete_tek_ct.display_vertical_source_sensitivity = ("COLLECT", vertical_sens)
        self.concrete_tek_ct.set_cursor_mode("DOT", 1)
        # MEASUREMENT
        self.concrete_tek_ct.measure_mode = "REP"

    def initialize_per_output_characteristics_measure(self,
                                                      peakpower=3000,
                                                      step_gen_offset=0,
                                                      vertical_sens=2.0,
                                                      horizontal_sens=0.5):

        # COLLECTOR SUPPLY
        self.concrete_tek_ct.cs_peakpower = peakpower
        self.concrete_tek_ct.cs_polarity = "POS"
        self.concrete_tek_ct.cs_collector_supply = 0
        # STEP GEN
        self.concrete_tek_ct.stepgen_step_source_and_size = ("VOLTAGE", 5.0)
        self.concrete_tek_ct.stepgen_number_steps = 0
        self.concrete_tek_ct.stepgen_offset = step_gen_offset
        # DISPLAY
        self.concrete_tek_ct.diplay_store_mode = "STO"
        self.concrete_tek_ct.display_horizontal_source_sensitivity = ("COLLECT", horizontal_sens)
        self.concrete_tek_ct.display_vertical_source_sensitivity = ("COLLECT", vertical_sens)
        self.concrete_tek_ct.set_cursor_mode("DOT", 1)
        # MEASUREMENT
        self.concrete_tek_ct.measure_mode = "REP"

    def initialize_per_transfer_characteristics_measure(self,
                                                        peakpower=3000,
                                                        collector_supply=66.6,
                                                        step_gen_offset=0,
                                                        vertical_sens=2.0,
                                                        horizontal_sens=1.0):

        # STEP GEN
        self.concrete_tek_ct.stepgen_step_source_and_size = ("VOLTAGE", 5.0)
        self.concrete_tek_ct.stepgen_number_steps = 0
        self.concrete_tek_ct.stepgen_offset = step_gen_offset
        # COLLECTOR SUPPLY
        self.concrete_tek_ct.cs_peakpower = peakpower
        self.concrete_tek_ct.cs_polarity = "POS"
        self.concrete_tek_ct.cs_collector_supply = collector_supply
        # DISPLAY
        self.concrete_tek_ct.diplay_store_mode = "STO"
        self.concrete_tek_ct.display_horizontal_source_sensitivity = ("STP", horizontal_sens)
        self.concrete_tek_ct.display_vertical_source_sensitivity = ("COLLECT", vertical_sens)
        self.concrete_tek_ct.set_cursor_mode("DOT", 1)
        # MEASUREMENT
        self.concrete_tek_ct.measure_mode = "REP"

    def get_peak_power(self):
        return self.concrete_tek_ct.cs_peakpower

    def set_peak_power(self, pp):
        if pp not in self.VALID_PEAK_POWER:
            raise Exception(
                "Peak Power must be one of the values:"
                + str(self.VALID_PEAK_POWER)
            )
        else:
            self.concrete_tek_ct.cs_peakpower = pp

    def reset_peak_power(self):
        self.set_peak_power(self.VALID_PEAK_POWER[0])

    def increase_peak_power(self):
        self.set_peak_power(self.VALID_PEAK_POWER[1])

    def decrease_peak_power(self):
        self.set_peak_power(self.VALID_PEAK_POWER[0])

    def get_collector_suplly(self):
        return self.concrete_tek_ct.cs_collector_supply

    def set_collector_suplly(self, value):
        self.concrete_tek_ct.cs_collector_supply = value

    def change_collector_supply(self, increase=True, delta=COLLECTOR_SUPPLY_RESOLUTION):
        """
        changes the actual value of the collector supply
        :param increase: if increase is True then the collector supply will change in order to rise the
        power applied to the DUT. Otherwise if False.
        :param delta: is the variation or delta (in %) we want to vary the collector supply. Min
        allowed increments of 0.1%
        :return: None
        """
        actual_cs = self.concrete_tek_ct.cs_collector_supply
        _delta = self.COLLECTOR_SUPPLY_RESOLUTION if delta < self.COLLECTOR_SUPPLY_RESOLUTION else abs(
            delta)
        if not increase:
            _delta = - _delta
        self.set_collector_suplly(actual_cs + delta)

    def increase_collector_supply(self, delta=COLLECTOR_SUPPLY_RESOLUTION):
        self.change_collector_supply(increase=True, delta=delta)

    def decrease_collector_supply(self, delta=COLLECTOR_SUPPLY_RESOLUTION):
        self.change_collector_supply(increase=False, delta=delta)

    def reset_collector_supply(self):
        self.set_collector_suplly(0.0)

    def reset_horizontal_sensitivity(self):
        horizontal_sensitivities = self.get_valid_horizontal_sensitivities()
        self.set_horizontal_sensitivity(horizontal_sensitivities[0])

    def set_horizontal_sensitivity(self, sensitivity):
        h_source = self.concrete_tek_ct.display_horizontal_source_sensitivity[0]
        self.concrete_tek_ct.display_horizontal_source_sensitivity = (h_source, sensitivity)

    def get_horizontal_sensitivity(self):
        return self.concrete_tek_ct.display_horizontal_source_sensitivity[1]

    def change_horizontal_sensitivity(self, increase=True):
        """
        changes the actual value of the horizontal sensitivity
        :param increase: if increase is True then the horizontal sensitivity will change in order to reduce the
        volts/div. If False the will change will change in order to raise the volts/div.
        :return: None
        """
        horizontal_sensitivity = self.get_horizontal_sensitivity()
        horizontal_sensitivities = self.get_valid_horizontal_sensitivities()
        index = horizontal_sensitivities.index(horizontal_sensitivity)
        new_index = index + 1
        if increase:
            new_index = index - 1
        try:
            self.set_horizontal_sensitivity(horizontal_sensitivities[new_index])
        except (Exception,):
            pass

    def increase_horizontal_sensitivity(self):
        self.change_horizontal_sensitivity(increase=True)

    def decrease_horizontal_sensitivity(self):
        self.change_horizontal_sensitivity(increase=False)

    def get_valid_horizontal_sensitivities(self):
        horizontal_source = self.concrete_tek_ct.display_horizontal_source_sensitivity[0]
        pp = self.get_peak_power()
        return self.concrete_tek_ct. \
            HORIZONTAL_DISPLAY_SENSITIVITY_VALID_SELECTIONS_VS_PEAKPOWER_FOR_SOURCE[
            horizontal_source][pp]

    def get_horizontal_range(self):
        return self.get_horizontal_sensitivity() * self.N_HORIZONTAL_DIVS

    def reset_horizontal_range(self):
        self.reset_horizontal_sensitivity()

    def increase_horizontal_range(self):
        self.decrease_horizontal_sensitivity()

    def decrease_horizontal_range(self):
        self.increase_horizontal_sensitivity()

    def reset_vertical_sensitivity(self):
        vertical_sensitivities = self.get_valid_vertical_sensitivities()
        self.set_vertical_sensitivity(vertical_sensitivities[0])

    def set_vertical_sensitivity(self, sensitivity):
        vertical_source = self.concrete_tek_ct.display_vertical_source_sensitivity[0]
        self.concrete_tek_ct.display_vertical_source_sensitivity = (vertical_source, sensitivity)

    def get_vertical_sensitivity(self):
        return self.concrete_tek_ct.display_vertical_source_sensitivity[1]

    def change_vertical_sensitivity(self, increase=True):
        """
        changes the actual value of the vertical sensitivity
        :param increase: if increase is True then the vertical sensitivity will change in order to reduce the
        amps/div. If False the will change will change in order to raise the amps/div.
        :return: None
        """
        vertical_sensitivity = self.get_vertical_sensitivity()
        vertical_sensitivities = self.get_valid_vertical_sensitivities()
        index = vertical_sensitivities.index(vertical_sensitivity)
        new_index = index + 1
        if increase:
            new_index = index - 1
        try:
            self.set_vertical_sensitivity(vertical_sensitivities[new_index])
        except (Exception,):
            pass

    def increase_vertical_sensitivity(self):
        self.change_vertical_sensitivity(increase=True)

    def decrease_vertical_sensitivity(self):
        self.change_vertical_sensitivity(increase=False)

    def get_valid_vertical_sensitivities(self):
        vertical_source = self.concrete_tek_ct.display_vertical_source_sensitivity[0]
        pp = self.get_peak_power()
        return self.concrete_tek_ct. \
            VERTICAL_DISPLAY_SENSITIVITY_VALID_SELECTIONS_VS_PEAKPOWER_FOR_SOURCE[vertical_source][
            pp]

    def get_vertical_range(self):
        return self.get_vertical_sensitivity() * self.N_VERTICAL_DIVS

    def reset_vertical_range(self):
        self.reset_vertical_sensitivity()

    def increase_vertical_range(self):
        self.decrease_vertical_sensitivity()

    def decrease_vertical_range(self):
        self.increase_vertical_sensitivity()

    def reset_number_of_steps(self):
        self.set_number_of_steps(0)

    def set_number_of_steps(self, n_steps):
        self.concrete_tek_ct.stepgen_number_steps = n_steps

    def get_number_of_steps(self):
        return self.concrete_tek_ct.stepgen_number_steps

    def change_number_of_steps(self, increase=True):
        """
        changes the actual value of the number of steps in the step generator
        :param increase: if increase is True then the number of steps in the step generator will raise by one.
        Otherwise will decrease by one.
        :return: None
        """
        n_steps = self.get_number_of_steps()
        if increase:
            n_steps = n_steps + 1
        else:
            n_steps = n_steps - 1
        try:
            self.set_number_of_steps(n_steps)
        except (Exception,):
            pass

    def increase_number_of_steps(self):
        self.change_number_of_steps(increase=True)

    def decrease_number_of_steps(self):
        self.change_number_of_steps(increase=False)

    def reset_stepgen_offset(self):
        self.set_stepgen_offset(self.STEPGEN_MIN_OFFSET)

    def set_stepgen_offset(self, offset):
        self.concrete_tek_ct.stepgen_offset = offset

    def get_stepgen_offset(self):
        return self.concrete_tek_ct.stepgen_offset

    def __change_stepgen_offset(self, delta=0.1, limit=10, increase=True):
        offset = self.get_stepgen_offset()
        r_offset = round(offset, 2)

        abs_limit_value = abs(limit)
        if -abs_limit_value >= r_offset or r_offset >= abs_limit_value:
            return

        step = self.get_stepgen_step_size()
        min_delta = - self.STEPGEN_OFFSET_RESOLUTION * step
        min_delta = max(round(min_delta, ndigits=3), abs(delta))
        if not increase:
            min_delta = - min_delta
        self.set_stepgen_offset(offset + min_delta)

    def vary_stepgen_offset(self, delta=0.1, limit=10):
        """
        Changes the step generator offset following the variation which can be negative.
        :param delta: the amount of variaton
        :param limit: the -limit, limit imposed to the minimum or maximun value
        that the offset can reach.
        :return: None
        """
        if delta <= 0:
            self.__change_stepgen_offset(delta, limit, increase=False)
        else:
            self.__change_stepgen_offset(delta, limit, increase=True)

    def reset_stepgen_step_size(self):
        stepgen_sizes = self.get_valid_stepgen_step_sizes()
        self.set_stepgen_step_size(stepgen_sizes[0])

    def set_stepgen_step_size(self, step_size):
        stepgen_source = self.concrete_tek_ct.stepgen_step_source_and_size[0]
        self.concrete_tek_ct.stepgen_step_source_and_size = (stepgen_source, step_size)

    def get_stepgen_step_size(self):
        return self.concrete_tek_ct.stepgen_step_source_and_size[1]

    def change_stepgen_step_size(self, increase=True):
        """
        changes the actual value of the step size in the step generator
        :param increase: if increase is True then the step size in the step generator will raise.
        Otherwise will decrease.
        :return: None
        """
        stepgen_size = self.get_stepgen_step_size()
        stepgen_sizes = self.get_valid_stepgen_step_sizes()
        index = stepgen_sizes.index(stepgen_size)
        if increase:
            if not (index == (len(stepgen_sizes) - 1)):
                index = index + 1
        else:
            if not (index == 0):
                index = index - 1
        try:
            self.set_stepgen_step_size(stepgen_sizes[index])
        except (Exception,):
            pass

    def increase_stepgen_step_size(self):
        self.change_stepgen_step_size(increase=True)

    def decrease_stepgen_step_size(self):
        self.change_stepgen_step_size(increase=False)

    def get_valid_stepgen_step_sizes(self):
        stepgen_source = self.get_stepgen_source()
        pp = self.get_peak_power()
        return self.concrete_tek_ct. \
            STEP_GENERATOR_VALID_STEP_SELECTIONS_FOR_STEP_SOURCE[stepgen_source][pp]

    def set_stepgen_source(self, stepgen_source):
        stepgen_sizes = self.get_valid_stepgen_step_sizes()
        self.concrete_tek_ct.stepgen_step_source_and_size = (stepgen_source, stepgen_sizes[0])

    def get_stepgen_source(self):
        return self.concrete_tek_ct.stepgen_step_source_and_size[0]

    def get_current_readout(self):
        return self.concrete_tek_ct.crt_readout_v

    def get_voltage_readout(self):
        return self.concrete_tek_ct.crt_readout_h

    def activate_srq(self):
        self.concrete_tek_ct.enable_srq_event()

    def wait_for_srq(self):
        self.concrete_tek_ct.wait_for_srq()

    def start_sweep(self):
        self.concrete_tek_ct.measure_mode = "SWEep"

    def get_curve(self):
        return self.concrete_tek_ct.get_curve()

    def set_number_of_curve_points(self, n):
        self.concrete_tek_ct.waveform_points = n


def measure_3Q(tct,
               peakpower=3000,
               step_gen_offset=0,
               vertical_sens=2.0,
               horizontal_sens=0.5,
               min_i=-20,
               min_v=-5,
               results_file_name="test",
               repeat=2):
    """
    :type tct:TektronixCurveTracer
    """

    n_measures = 0
    while n_measures < repeat:
        print("MEASURING 3Q WITH Vgs=", step_gen_offset, "V. Measure number ", n_measures + 1)
        tct.initialize_per_3Q_measure(peakpower,
                                      step_gen_offset,
                                      vertical_sens,
                                      horizontal_sens)
        tct.activate_srq()
        i_cursor = 0
        v_cursor = 0
        sleep(0.1)

        while i_cursor > min_i and v_cursor > min_v:
            tct.increase_collector_supply(1.0)
            sleep(0.5)
            i_cursor = tct.get_current_readout()
            v_cursor = tct.get_voltage_readout()
            print(v_cursor, i_cursor)

        tct.start_sweep()
        tct.wait_for_srq()
        curve = tct.get_curve()  # list of tuples [(x0, y0), (x1, y1) .... (xn-1, yn-1)]
        time.sleep(2)  # wait for instrment response
        curve_points = curve.points
        curve_points.reverse()
        print(curve_points)

        with open(results_file_name + '_' + str(n_measures + 1), 'w') as file:
            for curve_point in curve_points:
                row_text = str(curve_point[0]) + '\t' + str(curve_point[1]) + '\n'
                file.write(row_text)

        tct.concrete_tek_ct.discard_and_disable_all_events()
        n_measures = n_measures + 1


def measure_IdVd(tct,
                 peakpower=3000,
                 step_gen_offset=0,
                 vertical_sens=2.0,
                 horizontal_sens=0.5,
                 max_i=20,
                 max_v=5,
                 results_file_name="test",
                 repeat=2):
    """
    :type tct:TektronixCurveTracer
    """
    n_measures = 0
    while n_measures < repeat:
        print("MEASURING IdVd WITH Vgs=", step_gen_offset, "V. Measure number ", n_measures + 1)
        tct.initialize_per_output_characteristics_measure(peakpower,
                                                          step_gen_offset,
                                                          vertical_sens,
                                                          horizontal_sens)
        tct.activate_srq()
        i_cursor = 0
        v_cursor = 0
        sleep(0.1)

        while i_cursor < max_i and v_cursor < max_v:
            tct.increase_collector_supply(1.0)
            sleep(0.5)
            i_cursor = tct.get_current_readout()
            v_cursor = tct.get_voltage_readout()
            print(v_cursor, i_cursor)

        tct.start_sweep()
        tct.wait_for_srq()
        curve = tct.get_curve()  # list of tuples [(x0, y0), (x1, y1) .... (xn-1, yn-1)]
        time.sleep(2)  # wait for instrment response
        curve_points = curve.points
        curve_points.reverse()
        print(curve_points)

        with open(results_file_name + '_' + str(n_measures + 1), 'w') as file:
            for curve_point in curve_points:
                row_text = str(curve_point[0]) + '\t' + str(curve_point[1]) + '\n'
                file.write(row_text)

        tct.concrete_tek_ct.discard_and_disable_all_events()
        n_measures = n_measures + 1


def measure_IdVgs(tct,
                  peakpower=3000,
                  collector_suplly=66.6,
                  step_gen_offset=0,
                  limit_stegen_offset=15.0,
                  vertical_sens=2.0,
                  horizontal_sens=0.5,
                  max_i=20,
                  max_v=5,
                  results_file_name="test",
                  repeat=2):
    """
    :type tct:TektronixCurveTracer
    """
    n_measures = 0
    while n_measures < repeat:
        print("MEASURING IdVGS WITH Vds=", collector_suplly, "%. Measure number ", n_measures + 1)
        tct.initialize_per_transfer_characteristics_measure(peakpower,
                                                            collector_suplly,
                                                            step_gen_offset,
                                                            vertical_sens,
                                                            horizontal_sens)
        tct.activate_srq()
        i_cursor = 0
        v_cursor = 0
        sleep(0.1)

        while i_cursor < max_i and v_cursor < max_v:
            tct.vary_stepgen_offset(delta=0.3,
                                    limit=limit_stegen_offset)
            sleep(0.5)
            i_cursor = tct.get_current_readout()
            v_cursor = tct.get_voltage_readout()
            print(v_cursor, i_cursor)

        tct.start_sweep()
        tct.wait_for_srq()
        curve = tct.get_curve()  # list of tuples [(x0, y0), (x1, y1) .... (xn-1, yn-1)]
        time.sleep(2)  # wait for instrment response
        curve_points = curve.points
        curve_points.reverse()
        print(curve_points)

        with open(results_file_name + '_' + str(n_measures + 1), 'w') as file:
            for curve_point in curve_points:
                row_text = str(curve_point[0]) + '\t' + str(curve_point[1]) + '\n'
                file.write(row_text)

        tct.concrete_tek_ct.discard_and_disable_all_events()
        n_measures = n_measures + 1


def main() -> int:
    ct371a = Tektronix371A("GPIB0::23::INSTR")
    tct = TektronixCurveTracer(ct371a)

    number_of_cycles = 0
    device_ref = "CREE_C2M0080120_1_TO247"

    # ##############################################################################################
    # ##############################################################################################
    # ##############################################################################################

    peakpower = 3000
    step_gen_offset = 0
    vertical_sens = 2.0
    horizontal_sens = 0.5
    min_i = -20
    min_v = -5
    curve_name = "ID_Vds@Vgs=0(3ERQ)"
    results_file_name = '(' + str(number_of_cycles) + 'cyles)' + device_ref + curve_name

    tct.concrete_tek_ct.initialize()
    time.sleep(1)

    measure_3Q(tct,
               peakpower,
               step_gen_offset,
               vertical_sens,
               horizontal_sens,
               min_i,
               min_v,
               results_file_name,
               repeat=2)

    # ##############################################################################################
    # ##############################################################################################
    # ##############################################################################################

    peakpower = 3000
    step_gen_offset = 5
    vertical_sens = 2.0
    horizontal_sens = 0.5
    min_i = -20
    min_v = -5
    curve_name = "ID_Vds@Vgs=-5(3ERQ)"
    results_file_name = '(' + str(number_of_cycles) + 'cyles)' + device_ref + curve_name

    tct.concrete_tek_ct.initialize()
    time.sleep(1)

    measure_3Q(tct,
               peakpower,
               step_gen_offset,
               vertical_sens,
               horizontal_sens,
               min_i,
               min_v,
               results_file_name,
               repeat=2)

    # ##############################################################################################
    # ##############################################################################################
    # ##############################################################################################

    peakpower = 3000
    step_gen_offset = 15
    vertical_sens = 2.0
    horizontal_sens = 0.5
    max_i = 20
    max_v = 5
    curve_name = "ID_Vds@Vgs=15V"
    results_file_name = '(' + str(number_of_cycles) + 'cyles)' + device_ref + curve_name

    tct.concrete_tek_ct.initialize()
    time.sleep(1)

    measure_IdVd(tct,
                 peakpower,
                 step_gen_offset,
                 vertical_sens,
                 horizontal_sens,
                 max_i,
                 max_v,
                 results_file_name,
                 repeat=2)

    ##############################################################################################
    ##############################################################################################
    ##############################################################################################

    peakpower = 3000
    collector_supply = 66.6
    step_gen_offset = 0
    limit_stegen_offset = 15.0
    vertical_sens = 2.0
    horizontal_sens = 1.0
    max_i = 20
    max_v = 10
    curve_name = "ID_Vgs@Vds=20"
    results_file_name = '(' + str(number_of_cycles) + 'cyles)' + device_ref + curve_name

    tct.concrete_tek_ct.initialize()
    time.sleep(1)

    measure_IdVgs(tct,
                  peakpower,
                  collector_supply,
                  step_gen_offset,
                  limit_stegen_offset,
                  vertical_sens,
                  horizontal_sens,
                  max_i,
                  max_v,
                  results_file_name,
                  repeat=2)


if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys
