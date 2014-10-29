import config
import dynamixel
from wheel_velocity import calculate_angle

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
curVel = 0
curAngle = 0

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

def _change_velocity(vel, reverse=''):
    # We need to know the current angle of our robot
    # and calculate the velocities of our individual wheels
    print 'Velocity to %d' % vel
    curVel = vel
    data = calculate_angle(vel, net[config.joints[0]].current_position) # Take angle from front joint

    # If any velocity is negative then abs() and + 1024

    for servo in zip(config.wheels[0], data['wheels'][0]):
        # Servo is a tuple (id, vel)
        actuator = net[servo[0]]
        actuator.moving_speed = _reverse(servo[1]) if reverse == 'l' else servo[1]
    for servo in zip(config.wheels[1], data['wheels'][1]):
        # Servo is a tuple (id, vel)
        actuator = net[servo[0]]
        actuator.moving_speed = _reverse(servo[1]) if reverse != 'r' else servo[1]

    # Write the changes
    net.synchronize()

def _change_angle(angle, speed):
    print 'Turning by %d units' % angle

    # Front
    actuator = net[config.joints[0]]
    actuator.moving_speed = speed
    actuator.goal_position = 512 + angle

    # Rear
    actuator = net[config.joints[2]]
    actuator.moving_speed = speed
    actuator.goal_position = 512 - angle

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

# Command loop
while (True):
    cmd = raw_input()
    if cmd[0] == 'v':
        # Modify velocity
        reverse = ''
        if cmd[1] in 'lr':
            reverse = cmd[1]
            vel = int(cmd[2:])
        else:
            vel = int(cmd[1:])

        # Now vel is the required tangential velocity
        _change_velocity(vel, reverse)

    elif cmd[0] == 't':
        # Turn
        angle = int(cmd[1:])
        _change_angle(angle, 50) # arbitrary
    elif cmd[0] == 'l':
        # Lift
        angle = int(cmd[1:])
        print 'Lifting by %d units' % angle

        actuator = net[config.joints[1]]
        actuator.moving_speed = 50 # arbitrary
        actuator.goal_position = 512 + angle
    elif cmd[0] == 'q':
        break

    net.synchronize()

print('Done')