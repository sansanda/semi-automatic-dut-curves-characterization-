import logging
import sys
from time import sleep
from pymeasure.instruments.tektronix.tektronix371A import Tektronix371A

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

    def __init__(self, concrete_tek_ct=Tektronix371A):
        self.concrete_tek_ct = concrete_tek_ct

    def initialize(self):
        self.concrete_tek_ct.initialize()

        # COLLECTOR SUPPLY
        self.concrete_tek_ct.cs_peakpower = 300
        self.concrete_tek_ct.cs_polarity = "POS"
        self.concrete_tek_ct.cs_collector_supply = 0
        # STEP GEN
        self.concrete_tek_ct.stepgen_step_source_and_size = ("VOLTAGE", 5.0)
        self.concrete_tek_ct.stepgen_number_steps = 0
        self.concrete_tek_ct.set_stepgen_offset(0)
        # DISPLAY
        self.concrete_tek_ct.diplay_store_mode = "STO"
        self.concrete_tek_ct.display_horizontal_source_sensitivity = ("COLLECT", 1.0E-1)
        self.concrete_tek_ct.display_vertical_source_sensitivity = ("COLLECT", 500.0E-3)
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

    def vary_collector_supply(self, variation):
        """
        changes the actual value of the collector supply
        :param variation: is the variation or delta or increment (in %) we want to vary the collector supply. Min
        allowed increments of 0.1%
        :return: None
        """
        actual_cs = self.concrete_tek_ct.cs_collector_supply
        self.set_collector_suplly(actual_cs + variation)

    def increase_collector_supply(self):
        cs = self.get_collector_suplly()
        self.set_collector_suplly(cs + 0.1)

    def decrease_collector_supply(self):
        cs = self.get_collector_suplly()
        self.set_collector_suplly(cs - 0.1)

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
            HORIZONTAL_DISPLAY_SENSITIVITY_VALID_SELECTIONS_VS_PEAKPOWER_FOR_SOURCE[horizontal_source][pp]

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
            VERTICAL_DISPLAY_SENSITIVITY_VALID_SELECTIONS_VS_PEAKPOWER_FOR_SOURCE[vertical_source][pp]

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
        self.concrete_tek_ct.set_stepgen_offset(offset)

    def get_stepgen_offset(self):
        return self.concrete_tek_ct.get_stepgen_offset()

    def change_stepgen_offset(self, increase=True):
        pass

    def increase_stepgen_offset(self):
        offset = self.get_stepgen_offset()
        print(offset)
        self.set_stepgen_offset(offset + 0.01)
        # a solucionar: cuando nos encontramos en step size = 5v (ver tb si pasa con otras sizes) el incremento de 0.01
        # no tiene efecto sobre el offset. Ver electrical specifications del manual del equipo

    def decrease_stepgen_offset(self):
        offset = self.get_stepgen_offset()
        print(offset)
        self.set_stepgen_offset(offset - 0.01)
        # a solucionar: cuando nos encontramos en step size = 5v (ver tb si pasa con otras sizes) el decremento de 0.01
        # no tiene efecto sobre el offset. Ver electrical specifications del manual del equipo

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
        pass

    def increase_stepgen_step_size(self):
        stepgen_size = self.get_stepgen_step_size()
        stepgen_sizes = self.get_valid_stepgen_step_sizes()
        index = stepgen_sizes.index(stepgen_size)
        if not (index == (len(stepgen_sizes) - 1)):
            index = index + 1
        try:
            self.set_stepgen_step_size(stepgen_sizes[index])
        except (Exception,):
            pass

    def decrease_stepgen_step_size(self):
        stepgen_size = self.get_stepgen_step_size()
        stepgen_sizes = self.get_valid_stepgen_step_sizes()
        index = stepgen_sizes.index(stepgen_size)
        if not (index == (len(stepgen_sizes) - 1)):
            index = index - 1
        try:
            self.set_stepgen_step_size(stepgen_sizes[index])
        except (Exception,):
            pass

    def get_valid_stepgen_step_sizes(self):
        stepgen_source = self.get_stepgen_source()
        pp = self.get_peak_power()
        return self.concrete_tek_ct. \
            HORIZONTAL_DISPLAY_SENSITIVITY_VALID_SELECTIONS_VS_PEAKPOWER_FOR_STEPGEN_SOURCE[stepgen_source][pp]

    def set_stepgen_source(self, stepgen_source):
        stepgen_sizes = self.get_valid_stepgen_step_sizes()
        self.concrete_tek_ct.stepgen_step_source_and_size = (stepgen_source, stepgen_sizes[0])

    def get_stepgen_source(self):
        return self.concrete_tek_ct.stepgen_step_source_and_size[0]

    def get_current_readout(self):
        return self.concrete_tek_ct.crt_readout_v

    def get_voltage_readout(self):
        return self.concrete_tek_ct.crt_readout_h

    def t(self):
        print(self.concrete_tek_ct.display_horizontal_source_sensitivity)
        print(self.concrete_tek_ct.display_vertical_source_sensitivity)


def main() -> int:
    ct371A = Tektronix371A("GPIB0::23::INSTR")
    tct = TektronixCurveTracer(ct371A)
    tct.initialize()

    i_max = 2
    v_max = 5
    power_supply_increment = 0.1

    tct.set_collector_suplly(0.0)
    sleep(0.5)  # da tiempo al crt para actualizarse, esto debe cambiarse por opc

    i_cursor = tct.get_current_readout()
    v_cursor = tct.get_voltage_readout()

    sleep(0.5)
    print(v_cursor, i_cursor)

    while i_cursor < i_max and v_cursor < v_max:

        # tct.increase_horizontal_range()
        #
        # tct.vary_collector_supply(power_supply_increment)
        # sleep(0.5)
        # i_cursor = tct.get_current_readout()
        # v_cursor = tct.get_voltage_readout()
        #
        # if tct.get_vertical_range() < i_cursor < i_max:
        #     tct.increase_vertical_range()
        #
        # if tct.get_horizontal_range() < v_cursor < v_max:
        #     tct.increase_horizontal_range()
        #
        # print(v_cursor, i_cursor)

        sleep(0.2)
        tct.reset_stepgen_offset()
        tct.reset_stepgen_step_size()
        tct.set_stepgen_step_size(5.0)
        while True:
            sleep(0.5)
            tct.increase_stepgen_offset()


if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys
