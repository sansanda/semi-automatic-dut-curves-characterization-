import sys

from pymeasure.instruments.validators import strict_discrete_set


def main() -> int:
    ADC_NBITS = 10
    VALID_V_H_COORDINATES_SET = [0, pow(2, ADC_NBITS) - 1]  # 0 is the beginning
    sds = strict_discrete_set(1024, VALID_V_H_COORDINATES_SET)
    print(sds)

if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys