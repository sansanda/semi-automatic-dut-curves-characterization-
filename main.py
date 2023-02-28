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
        actual_cs = self.concrete_tek_ct.cs_collector_supply
        self.set_collector_suplly(actual_cs + variation)

    def reset_collector_supply(self):
        self.set_collector_suplly(0.0)

    def set_horizontal_sensitivity(self, sensitivity):
        actual_source = self.concrete_tek_ct.display_horizontal_source_sensitivity[0]
        self.concrete_tek_ct.display_horizontal_source_sensitivity = (actual_source, sensitivity)

    def get_horizontal_sensitivity(self):
        return self.concrete_tek_ct.display_horizontal_source_sensitivity[1]

    def get_horizontal_range(self):
        return self.get_horizontal_sensitivity() * self.N_HORIZONTAL_DIVS

    def reset_horizontal_range(self):
        h_source = self.concrete_tek_ct.display_horizontal_source_sensitivity[0]
        pp = self.get_peak_power()
        horizontal_sensitivities = \
            self.concrete_tek_ct.HORIZONTAL_DISPLAY_SENSITIVITY_VALID_SELECTIONS_VS_PEAKPOWER_FOR_SOURCE[h_source][pp]
        self.set_horizontal_sensitivity(horizontal_sensitivities[0])

    def increase_horizontal_range(self):
        h_source = self.concrete_tek_ct.display_horizontal_source_sensitivity[0]
        h_sensitivity = self.concrete_tek_ct.display_horizontal_source_sensitivity[1]
        pp = self.get_peak_power()
        horizontal_sensitivities = \
            self.concrete_tek_ct.HORIZONTAL_DISPLAY_SENSITIVITY_VALID_SELECTIONS_VS_PEAKPOWER_FOR_SOURCE[h_source][pp]
        index = horizontal_sensitivities.index(h_sensitivity)
        new_index = index + 1

        try:
            self.set_horizontal_sensitivity(horizontal_sensitivities[new_index])
        except (Exception, ):
            pass

    def decrease_horizontal_range(self):
        h_source = self.concrete_tek_ct.display_horizontal_source_sensitivity[0]
        h_sensitivity = self.concrete_tek_ct.display_horizontal_source_sensitivity[1]
        pp = self.get_peak_power()
        horizontal_sensitivities = \
            self.concrete_tek_ct.HORIZONTAL_DISPLAY_SENSITIVITY_VALID_SELECTIONS_VS_PEAKPOWER_FOR_SOURCE[h_source][pp]
        index = horizontal_sensitivities.index(h_sensitivity)
        new_index = index - 1

        try:
            self.set_horizontal_sensitivity(horizontal_sensitivities[new_index])
        except (Exception, ):
            pass

    def set_vertical_sensitivity(self, sensitivity):
        actual_source = self.concrete_tek_ct.display_vertical_source_sensitivity[0]
        self.concrete_tek_ct.display_vertical_source_sensitivity = (actual_source, sensitivity)

    def get_vertical_sensitivity(self):
        return self.concrete_tek_ct.display_vertical_source_sensitivity[1]

    def get_vertical_range(self):
        return self.get_vertical_sensitivity() * self.N_VERTICAL_DIVS

    def reset_vertical_range(self):
        v_source = self.concrete_tek_ct.display_vertical_source_sensitivity[0]
        pp = self.get_peak_power()
        vertical_sensitivities = \
            self.concrete_tek_ct.VERTICAL_DISPLAY_SENSITIVITY_VALID_SELECTIONS_VS_PEAKPOWER_FOR_SOURCE[v_source][pp]
        self.set_vertical_sensitivity(vertical_sensitivities[0])

    def increase_vertical_range(self):
        v_source = self.concrete_tek_ct.display_vertical_source_sensitivity[0]
        v_sensitivity = self.concrete_tek_ct.display_vertical_source_sensitivity[1]
        pp = self.get_peak_power()
        vertical_sensitivities = \
            self.concrete_tek_ct.VERTICAL_DISPLAY_SENSITIVITY_VALID_SELECTIONS_VS_PEAKPOWER_FOR_SOURCE[v_source][pp]
        index = vertical_sensitivities.index(v_sensitivity)
        if not (index == (len(vertical_sensitivities) - 1)):
            index = index + 1
        try:
            self.set_vertical_sensitivity(vertical_sensitivities[index])
        except (Exception, ):
            pass

    def decrease_vertical_range(self):
        v_source = self.concrete_tek_ct.display_vertical_source_sensitivity[0]
        v_sensitivity = self.concrete_tek_ct.display_vertical_source_sensitivity[1]
        pp = self.get_peak_power()
        vertical_sensitivities = \
            self.concrete_tek_ct.VERTICAL_DISPLAY_SENSITIVITY_VALID_SELECTIONS_VS_PEAKPOWER_FOR_SOURCE[v_source][pp]
        index = vertical_sensitivities.index(v_sensitivity)
        if not (index == 0):
            index = index - 1
        try:
            self.set_vertical_sensitivity(vertical_sensitivities[index])
        except (Exception, ):
            pass

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
        # if i_cursor > tct.get_vertical_range() and i_cursor < i_max:
        #     tct.increase_vertical_range()
        #
        # if v_cursor > tct.get_horizontal_range() and v_cursor < v_max:
        #     tct.increase_horizontal_range()
        #
        # print(v_cursor, i_cursor)

        # sleep(1)
        # tct.reset_horizontal_range()
        # sleep(1)
        # tct.increase_horizontal_range()
        # sleep(1)
        # tct.increase_horizontal_range()
        # sleep(1)
        # tct.increase_horizontal_range()
        # sleep(1)
        # tct.increase_horizontal_range()
        # sleep(1)
        # tct.increase_horizontal_range()
        # sleep(1)
        # tct.decrease_horizontal_range()
        # sleep(1)
        # tct.decrease_horizontal_range()
        # sleep(1)
        # tct.decrease_horizontal_range()
        # sleep(1)
        # tct.decrease_horizontal_range()
        # sleep(1)
        # tct.decrease_horizontal_range()
        tct.increase_peak_power()
        sleep(1)
        tct.reset_vertical_range()
        while True:
            sleep(1)
            print(tct.get_vertical_range())
            tct.increase_vertical_range()


if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys
