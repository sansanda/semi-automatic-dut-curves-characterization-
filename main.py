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

    def __init__(self, concrete_tek_ct=Tektronix371A):
        self.concrete_tek_ct = concrete_tek_ct

    def initialize(self):
        self.concrete_tek_ct.initialize()

        #COLLECTOR SUPPLY
        self.concrete_tek_ct.cs_peakpower = 300
        self.concrete_tek_ct.cs_polarity = "POS"
        self.concrete_tek_ct.cs_collector_supply = 0
        #STEP GEN
        self.concrete_tek_ct.stepgen_step_source_and_size = ("VOLTAGE", 5.0)
        self.concrete_tek_ct.stepgen_number_steps = 0
        self.concrete_tek_ct.set_stepgen_offset(0)
        #DISPLAY
        self.concrete_tek_ct.diplay_store_mode = "STO"
        self.concrete_tek_ct.display_horizontal_source_sensitivity = ("COLLECT", 1.0E-1)
        self.concrete_tek_ct.display_vertical_source_sensitivity = ("COLLECT", 500.0E-3)
        self.concrete_tek_ct.set_cursor_mode("DOT", 1)
        #MEASUREMENT
        self.concrete_tek_ct.measure_mode = "REP"

    def set_collector_suplly(self, value):
        self.concrete_tek_ct.cs_collector_supply = value

    def vary_collector_supply(self, variation):
        actual_cs = self.concrete_tek_ct.cs_collector_supply
        self.concrete_tek_ct.cs_collector_supply = actual_cs + variation

    def set_horizontal_sensitivity(self, sensitivity):
        actual_source = self.concrete_tek_ct.display_horizontal_source_sensitivity[0]
        self.concrete_tek_ct.display_horizontal_source_sensitivity = (actual_source, sensitivity)

    def set_vertical_sensitivity(self, sensitivity):
        actual_source = self.concrete_tek_ct.display_vertical_source_sensitivity[0]
        self.concrete_tek_ct.display_vertical_source_sensitivity = (actual_source, sensitivity)

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
    tct.set_collector_suplly(0)
    sleep(0.5) #da tiempo al crt para actualizarse, esto debe cambiarse por opc

    i_max = 2
    v_max = 5
    i_cursor = tct.get_current_readout()
    v_cursor = tct.get_voltage_readout()
    print(v_cursor, i_cursor)

if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys
