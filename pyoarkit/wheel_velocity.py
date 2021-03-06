from math import sin, cos, tan, atan, pi

from config import (
    CENTER_VALUE_TOP,
    CENTER_ANGLE_TOP,
    MIN_VALUE_TOP,
    MIN_ANGLE_TOP,
    MAX_VALUE_TOP,
    MAX_ANGLE_TOP,
    CENTER_VALUE_BOTTOM,
    CENTER_ANGLE_BOTTOM,
    MIN_VALUE_BOTTOM,
    MIN_ANGLE_BOTTOM,
    MAX_VALUE_BOTTOM,
    MAX_ANGLE_BOTTOM,
    ARM_TOP_LEFT,
    ARM_TOP_RIGHT,
    ARM_MID_LEFT,
    ARM_MID_RIGHT,
    ARM_BOTTOM_LEFT,
    ARM_BOTTOM_RIGHT,
    SPINE_TOP,
    SPINE_BOTTOM,
    MAX_WHEEL_VELOCITY,
)

# angular limits
_topMin = atan(tan(MAX_ANGLE_BOTTOM) * SPINE_BOTTOM / SPINE_TOP)
_topMax = pi - atan(tan(pi - MIN_ANGLE_BOTTOM) * SPINE_BOTTOM / SPINE_TOP)

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
    if coefficient > 1:
        raise ValueError("Coefficient given for angle is higher than 1")
    elif coefficient < -1:
        raise ValueError("Coefficient given for angle is lower than -1")
    if coefficient < 0:
        return int(_interpolate(-1, coefficient, 0, _angle_to_value(MIN_ANGLE, True), CENTER_VALUE_TOP))
    else:
        return int(_interpolate(0, coefficient, 1, CENTER_VALUE_TOP, _angle_to_value(MAX_ANGLE, True)))


def calculate_angle(velocity, angleValue):
    """
    :param velocity: The average tangential velocity of the center of the vehicle, from 0 to 1023
    :param angleValue: The value of the angle that the right side is inclined at. From -1 to 1
    :rtype: a dictionary structured as follows:
    {"wheels": ((leftTop, leftMid, leftBot), (rightTop, rightMid, rightBot)),
    "joints": (front, middle, back)}
    """

    # Straight-angled case
    if abs(angleValue - CENTER_VALUE_TOP) < 10 ** -2:  # practically straight
        if abs(velocity) > MAX_WHEEL_VELOCITY:
            print("{} exceeds max velocity {} for angle {}".format(abs(velocity), MAX_WHEEL_VELOCITY, angleValue))
            print("Velocity is being set to {}".format(MAX_WHEEL_VELOCITY))
            sign = velocity / abs(velocity)
            v = sign * MAX_WHEEL_VELOCITY
            velocity = int(velocity)
        return {"wheels": ((velocity, velocity, velocity), (velocity, velocity, velocity)),
                "joints": (int(CENTER_VALUE_TOP), int(CENTER_VALUE_BOTTOM))}

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

    if angleValue < 0:
        maxVelocity = MAX_WHEEL_VELOCITY * (130 * tan(a) / (SPINE_BOTTOM / cos(a2) + ARM_BOTTOM_LEFT))
    else:
        maxVelocity = MAX_WHEEL_VELOCITY * (130 * tan(pi - a) / (SPINE_BOTTOM / cos(pi - a2) + ARM_BOTTOM_LEFT))
    maxVelocity -= 10  # for safety

    if abs(velocity) > maxVelocity:
        raise ValueError("{} exceeds max velocity {} for angle {}".format(abs(velocity), maxVelocity, angleValue))
    else:
        v = velocity

    tl = v * (1 / sin(a) + ARM_TOP_LEFT / (SPINE_TOP * tan(a)))
    tr = v * (1 / sin(a) - ARM_TOP_RIGHT / (SPINE_TOP * tan(a)))
    ml = v * (1 + ARM_MID_LEFT / (SPINE_TOP * tan(a)))
    mr = v * (1 - ARM_MID_RIGHT / (SPINE_TOP * tan(a)))
    bl = v * (SPINE_BOTTOM / (SPINE_TOP * tan(a) * cos(a2)) + ARM_BOTTOM_LEFT / (SPINE_TOP * tan(a)))
    br = v * (SPINE_BOTTOM / (SPINE_TOP * tan(a) * cos(a2)) - ARM_BOTTOM_RIGHT / (SPINE_TOP * tan(a)))

    tl, tr, ml, mr, bl, br, = map(int, (tl, tr, ml, mr, bl, br))
    aValue, a2Value = map(lambda angle: int(_angle_to_value(angle, angle == a)), (a, a2))

    return {"wheels": ((tl, ml, bl), (tr, mr, br)),
            "joints": (aValue, a2Value)}
