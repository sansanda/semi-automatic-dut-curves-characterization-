import sys

from pymeasure.instruments.validators import strict_discrete_set


def main() -> int:
    VALID_V_H_COORDINATES_SET = list(range(1024))  # 0 is the beginning
    sds = strict_discrete_set(1, VALID_V_H_COORDINATES_SET)
    print(sds)

if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys