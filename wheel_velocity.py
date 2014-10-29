from math import sin, cos, tan, atan, pi, radians

# angles for top axle
CENTER_VALUE_TOP = 512.0 - 10.0  # 90 degrees
CENTER_ANGLE_TOP = radians(90.0)
MIN_VALUE_TOP = 512.0 - 110.0  # 65 degrees
MIN_ANGLE_TOP = radians(65.0)
MAX_VALUE_TOP = 512.0 + 100.0  # 115 degrees
MAX_ANGLE_TOP = radians(115.0)

# angles for bottom axle
CENTER_VALUE_BOTTOM = 512.0 + 10.0  # 90 degrees
CENTER_ANGLE_BOTTOM = radians(90.0)
MIN_VALUE_BOTTOM = 512.0 - 60.0  # 110 degrees
MIN_ANGLE_BOTTOM = radians(110.0)  # note min value gives a corresponding larger angle
MAX_VALUE_BOTTOM = 512.0 + 90.0  # 70 degrees
MAX_ANGLE_BOTTOM = radians(70.0)

# lengths of arms (mm)
ARM_TOP_LEFT = 91.0
ARM_TOP_RIGHT = 91.0
ARM_MID_LEFT = 95.0
ARM_MID_RIGHT = 95.0
ARM_BOTTOM_LEFT = 91.0
ARM_BOTTOM_RIGHT = 91.0

# lengths of spine (mm)
SPINE_TOP = 130.0
SPINE_BOTTOM = 120.0

# max velocity of any given wheel
MAX_WHEEL_VELOCITY = 1023.0

# angular limits
_topMin = atan(tan(MIN_ANGLE_BOTTOM) * SPINE_BOTTOM / SPINE_TOP)
_topMax = pi - atan(tan(pi - MAX_ANGLE_BOTTOM) * SPINE_BOTTOM / SPINE_TOP)

MIN_ANGLE = max(_topMin, MIN_ANGLE_TOP)  # largest minimum bound
MAX_ANGLE = min(_topMax, MAX_ANGLE_TOP)  # smallest maximum bound


def _interpolate(minSource, source, maxSource, minDest, maxDest):
    sourceLocation = float(source - minSource) / float(maxSource - minSource)
    return (maxDest - minDest) * sourceLocation + minDest


# Note all angles are given in terms of the angle between the right arm and the spine
def _angle_to_value(angle, top):
    if top:
        if angle < CENTER_ANGLE_TOP:
            return _interpolate(MIN_ANGLE_TOP, angle, CENTER_ANGLE_TOP, MIN_VALUE_TOP, CENTER_VALUE_TOP)
        else:
            return _interpolate(CENTER_ANGLE_TOP, angle, MAX_ANGLE_TOP, CENTER_VALUE_TOP, MAX_VALUE_TOP)
    else:  # bottom
        if angle < CENTER_ANGLE_BOTTOM:
            return _interpolate(MAX_ANGLE_BOTTOM, angle, CENTER_ANGLE_BOTTOM, MAX_VALUE_BOTTOM, CENTER_VALUE_BOTTOM)
        else:
            return _interpolate(CENTER_ANGLE_BOTTOM, angle, MIN_ANGLE_BOTTOM, CENTER_VALUE_BOTTOM, MIN_VALUE_BOTTOM)


# Converts a Dynamixel motor inclination value to an angle for the top axle
def _value_to_angle(value):
    if value < CENTER_VALUE_TOP:
        return _interpolate(MIN_VALUE_TOP, value, CENTER_VALUE_TOP, MIN_ANGLE_TOP, CENTER_ANGLE_TOP)
    else:
        return _interpolate(CENTER_VALUE_TOP, value, MAX_VALUE_TOP, CENTER_ANGLE_TOP, MAX_ANGLE_TOP)


def get_angle_value(coefficient):
    """
    :param value: A float between -1 and 1 indicating the direction and magnitude of the turn.
    :return: Returns the valid angle corresponding to the value between -1 and 1
    """
    if coefficient < 1:
        return _interpolate(-1, coefficient, 0, _angle_to_value(MIN_ANGLE, True), CENTER_VALUE_TOP)
    else:
        return _interpolate(0, coefficient, 1, CENTER_VALUE_TOP, _angle_to_value(MAX_ANGLE, True))


def calculate_angle(velocity, angleValue):
    """
    :param velocity: The average tangential velocity of the center of the vehicle, from 0 to 1023
    :param angleValue: The value of the angle that the right side is inclined at. From -1 to 1
    :rtype: a dictionary structured as follows:
    {"wheels": ((leftTop, leftMid, leftBot), (rightTop, rightMid, rightBot)),
    "joints": (front, middle, back)}
    """

    # Straight-angled case
    if abs(angleValue) - CENTER_VALUE_TOP < 10 ** -2:  # practically straight
        if abs(velocity) > MAX_WHEEL_VELOCITY:
            print("{} exceeds max velocity {} for angle {}".format(abs(velocity), MAX_WHEEL_VELOCITY, angleValue))
            print("Velocity is being set to {}".format(MAX_WHEEL_VELOCITY))
            sign = velocity / abs(velocity)
            v = sign * MAX_WHEEL_VELOCITY
        return {"wheels": ((velocity, velocity, velocity), (velocity, velocity, velocity)),
                "joints": (CENTER_VALUE_TOP, CENTER_VALUE_BOTTOM)}

    minValue = _angle_to_value(MIN_ANGLE, True)
    maxValue = _angle_to_value(MAX_ANGLE, True)

    if angleValue < minValue:
        print("Angle given {} smaller than minimum angle of {}".format(angleValue, minValue))
        print("Angle set to {}".format(minValue))
        angleValue = minValue
    elif angleValue > maxValue:
        print("Angle given {} larger than maximum angle of {}".format(angleValue, maxValue))
        print("Angle set to {}".format(maxValue))
        angleValue = maxValue

    a = _value_to_angle(angleValue)
    if a < pi / 2:
        a2 = atan(tan(a) * SPINE_TOP / SPINE_BOTTOM)
    else:
        a2 = pi - atan(tan(pi - a) * SPINE_TOP / SPINE_BOTTOM)

    print("a is {}".format(a))
    print("a2 is {}".format(a2))

    if angleValue < 0:
        maxVelocity = MAX_WHEEL_VELOCITY * (130 * tan(a) / (SPINE_BOTTOM / cos(a2) + ARM_BOTTOM_LEFT))
    else:
        maxVelocity = MAX_WHEEL_VELOCITY * (130 * tan(pi - a) / (SPINE_BOTTOM / cos(pi - a2) + ARM_BOTTOM_LEFT))
    maxVelocity -= 10  # for safety

    if abs(velocity) > maxVelocity:
        print("{} exceeds max velocity {} for angle {}".format(abs(velocity), maxVelocity, angleValue))
        print("Velocity is being set to {}".format(maxVelocity))
        sign = velocity / abs(velocity)
        v = sign * maxVelocity
    else:
        v = velocity

    tl = v * (1 / sin(a) + ARM_TOP_LEFT / (SPINE_TOP * tan(a)))
    tr = v * (1 / sin(a) - ARM_TOP_RIGHT / (SPINE_TOP * tan(a)))
    ml = v * (1 + ARM_MID_LEFT / (SPINE_TOP * tan(a)))
    mr = v * (1 - ARM_MID_RIGHT / (SPINE_TOP * tan(a)))
    bl = v * (SPINE_BOTTOM / (SPINE_TOP * tan(a) * cos(a2)) + ARM_BOTTOM_LEFT / (SPINE_TOP * tan(a)))
    br = v * (SPINE_BOTTOM / (SPINE_TOP * tan(a) * cos(a2)) - ARM_BOTTOM_RIGHT / (SPINE_TOP * tan(a)))

    tl, tr, ml, mr, bl, br, = map(int, (tl, tr, ml, mr, bl, br))
    aValue, a2Value = map(lambda angle: int(_angle_to_value(angle)), (a, a2))

    return {"wheels": ((tl, ml, bl), (tr, mr, br)),
            "joints": (aValue, a2Value)}

print(calculate_angle(300, 550))