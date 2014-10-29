import config
import dynamixel

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

    # Why don't we need this?
    # net.synchronize()

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
        print 'Velocity to %d' % vel
        for servo in config.wheels[0]:
            actuator = net[servo]
            actuator.moving_speed = vel + (1023 if reverse == 'l' else 0)
        for servo in config.wheels[1]:
            actuator = net[servo]
            actuator.moving_speed = vel + (1023 if reverse != 'r' else 0)
    elif cmd[0] == 't':
        # Turn
        degrees = int(cmd[1:])
        print 'Turning left by %d degrees' % degrees

        # Front
        actuator = net[config.joints[0]]
        actuator.moving_speed = 50 # arbitrary
        actuator.goal_position = 512 + degrees

        # Rear
        actuator = net[config.joints[2]]
        actuator.moving_speed = 50 # arbitrary
        actuator.goal_position = 512 - degrees
    elif cmd[0] == 'l':
        # Lift
        degrees = int(cmd[1:])
        print 'Lifting by %d degrees' % degrees

        actuator = net[config.joints[1]]
        actuator.moving_speed = 50 # arbitrary
        actuator.goal_position = 512 + degrees
    elif cmd[0] == 'q':
        break

print('Done')