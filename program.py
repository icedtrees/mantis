import config
import dynamixel
from wheel_velocity import calculate_angle, get_angle_value

# Establish a serial connection to the dynamixel network.
# This usually requires a USB2Dynamixel
serial = dynamixel.SerialStream(port=config.port,
                                baudrate=config.baudRate,
                                timeout=1)

# Instantiate our network object
net = dynamixel.DynamixelNetwork(serial)

# Populate our network with dynamixel objects
for servoId in config.wheels[0] + config.wheels[1] + config.joints:
    newDynamixel = dynamixel.Dynamixel(servoId, net)
    net._dynamixel_map[servoId] = newDynamixel

# TODO Move this to a saner place. Random global vars
data = calculate_angle(0, get_angle_value(0))
curVel = 0
curAngle = data['joints'][0]

# TODO better name pls
# Make negative velocities into correct corresponding positive one
def _fix_vel(vel):
    if vel <= -2048:
        return _fix_vel(vel + 2048)
    elif vel <= -1024:
        return abs(vel + 1024)
    elif vel < 0:
        return abs(vel) + 1024
    elif vel >= 2048:
        return vel - 2048
    else:
        return vel

def _reverse(vel):
    vel = _fix_vel(vel)
    if vel < 1024:
        return vel + 1024
    elif vel >= 1024:
        return vel - 1024

def _change_velocity(vel, spin=False):
    # We need to know the current angle of our robot
    # and calculate the velocities of our individual wheels
    print 'Velocity to {}'.format(vel)
    data = calculate_angle(vel, net[config.joints[0]].current_position) # Take angle from front joint

    # If any velocity is negative then abs() and + 1024

    for servo in zip(config.wheels[0], data['wheels'][0]):
        # Servo is a tuple (id, vel)
        actuator = net[servo[0]]
        if spin:
            actuator.moving_speed += _fix_vel(servo[1])
        else:
            actuator.moving_speed = _fix_vel(servo[1])
    for servo in zip(config.wheels[1], data['wheels'][1]):
        # Servo is a tuple (id, vel)
        actuator = net[servo[0]]
        if spin:
            actuator.moving_speed += _reverse(servo[1])
        else:
            actuator.moving_speed = _fix_vel(servo[1])

    # Write the changes
    net.synchronize()

    curVel = actuator.moving_speed

def _change_angle(angle, speed, relative=False):
    print 'Turning {} units (small)'.format(angle)
    global curAngle
    if relative:
        curAngle += angle
    else:
        curAngle = angle
    data = calculate_angle(curVel, curAngle) # TODO poll and update as we turn
    curAngle = data['joints'][0]
    print 'Apparently joints are {}'.format(data['joints'])

    # Front
    actuator = net[config.joints[0]]
    actuator.moving_speed = speed
    actuator.goal_position = data['joints'][0]

    # Rear
    actuator = net[config.joints[2]]
    actuator.moving_speed = speed
    actuator.goal_position = data['joints'][1]

    net.synchronize()

# Initial read in
for actuator in net.get_dynamixels():
    print 'Currently on motor %d' % actuator.id
    actuator.read_all()
    if actuator.id in config.wheels[0]:
        print '    Left wheel'
        actuator.cw_angle_limit = 0
        actuator.ccw_angle_limit = 0
        # actuator.moving_speed = 200
    elif actuator.id in config.wheels[1]:
        print '    Right wheel'
        actuator.cw_angle_limit = 0
        actuator.ccw_angle_limit = 0
        # actuator.moving_speed = 1223
    elif actuator.id in config.joints:
        print '    Joint'
        actuator.cw_angle_limit = 0
        actuator.ccw_angle_limit = 1023
        # actuator.moving_speed = 100
        # actuator.torque_enable = True
        # actuator.torque_limit = 800 
        # actuator.max_torque = 800
        # actuator.goal_position = 512
    else:
        print '    Something is wrong'

    # Initial speed and angles
    _change_velocity(curVel) # 0 default
    _change_angle(curAngle, 50)  # 0 default


def execute_command(cmd):
    if cmd[0] == 'v':
        # Modify velocity
        vel = int(cmd[1:])

        # Now vel is the required tangential velocity
        _change_velocity(vel)
    elif cmd[0] == 's':
        # Spin
        vel = int(cmd[1:])

        _change_velocity(vel, True)

    elif cmd[0] == 't':
        # Turn
        angle = float(cmd[1:])
        print 'Read in user input angle {}'.format(angle)
        _change_angle(angle, 50, True) # arbitrary
    elif cmd[0] == 'l':
        # Lift
        angle = int(cmd[1:])
        print 'Lifting by %d units' % angle

        actuator = net[config.joints[1]]
        actuator.moving_speed = 50 # arbitrary
        actuator.goal_position += angle

        net.synchronize()
    elif cmd[0] == 'h':
        for actuator in net.get_dynamixels():
            actuator.stop()

        net.synchronize()
    elif cmd[0] == 'q':
        exit

if __name__ == "__main__":
    # Command loop
    while True:
        cmd = raw_input()
        execute_command(cmd)
