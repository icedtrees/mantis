from math import radians

# Actuator id's for the wheels
# wheels[0] gives all the left wheels
# wheels[1] gives all the right wheels
# Ordered from front to back
wheels = ((7, 12, 19), (11, 13, 14))

# Actuator id's for the joints
# Ordered from front to back
joints = (8, 16, 17)

baudRate = 1000000
port = '/dev/ttyUSB0'


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
