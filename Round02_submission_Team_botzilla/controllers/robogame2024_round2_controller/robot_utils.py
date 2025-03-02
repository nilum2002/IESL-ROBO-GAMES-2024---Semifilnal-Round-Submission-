import math

class RobotUtils:
    TIME_STEP = 64           # in milliseconds
    MAX_SPEED = 7         # in rad/s
    WHEEL_RADIUS = 0.05      # in meters
    AXLE_LENGTH = 0.142      # in meters

    def __init__(self, robot):
        self.robot = robot

        # motors
        self.left_motor = self.robot.getDevice('left motor')
        self.right_motor = self.robot.getDevice('right motor')
        # self.left_motor.setPosition(0)
        # self.right_motor.setPosition(0)
        # wheel sensors
        self.left_wheel_sensor = self.robot.getDevice('left motor sensor')
        self.right_wheel_sensor = self.robot.getDevice('right motor sensor')
        self.left_wheel_sensor.enable(self.TIME_STEP)
        self.right_wheel_sensor.enable(self.TIME_STEP)
        # compass
        self.compass = self.robot.getDevice('compass')
        self.compass.enable(self.TIME_STEP)
        # gps
        self.gps = self.robot.getDevice('gps')
        self.gps.enable(self.TIME_STEP)
        # distance sensors
        self.ds_front = self.robot.getDevice('ds front')
        self.ds_right = self.robot.getDevice('ds right')
        self.ds_left = self.robot.getDevice('ds left')
        self.ds_front.enable(self.TIME_STEP)
        self.ds_right.enable(self.TIME_STEP)
        self.ds_left.enable(self.TIME_STEP)
        # cameras
        self.camera_front = self.robot.getDevice('camera front')
        self.camera_bottom = self.robot.getDevice('camera bottom')
        self.camera_front.enable(self.TIME_STEP)
        self.camera_bottom.enable(self.TIME_STEP)

        self.step()

        self.left_motor_position = self.left_wheel_sensor_value()
        self.right_motor_position = self.right_wheel_sensor_value()

    def step(self):
        return self.robot.step(self.TIME_STEP) != -1

    #----------------------------------------------
    # Methods for motors
    #----------------------------------------------

    def add_left_motor_position(self, position):
        self.left_motor_position += position
        self.left_motor.setPosition(self.left_motor_position)

    def add_right_motor_position(self, position):
        self.right_motor_position += position
        self.right_motor.setPosition(self.right_motor_position)

    def set_left_motor_speed(self, speed, percentage=True):
        if percentage:
            speed = (speed / 100) * self.MAX_SPEED
        self.left_motor.setVelocity(speed)

    def set_right_motor_speed(self, speed, percentage=True):
        if percentage:
            speed = (speed / 100) * self.MAX_SPEED
        self.right_motor.setVelocity(speed)

    def set_speed(self, speed):
        self.set_left_motor_speed(speed)
        self.set_right_motor_speed(speed)

    #----------------------------------------------
    # Methods for wheel sensors
    #----------------------------------------------

    def left_wheel_sensor_value(self):
        return self.left_wheel_sensor.getValue()
    
    def right_wheel_sensor_value(self):
        return self.right_wheel_sensor.getValue()
    
    #----------------------------------------------
    # Methods for compass
    #----------------------------------------------

    def compass_value(self):
        return self.compass.getValues()
    
    def bearing(self):
        dir = self.compass_value()
        if math.isnan(dir[0]):
            return None
        rad = math.atan2(dir[0], dir[1])
        bearing = (rad - 1.5708) / math.pi * 180.0
        if bearing < 0.0:
            bearing = bearing + 360.0
        return bearing
    
    def direction_bearing(self):
        """Round a given bearing to the nearest cardinal direction (0, 90, 180, 270)."""
        bearing = self.bearing()
        cardinal_directions = [0, 90, 180, 270, 360]
        dir = min(cardinal_directions, key=lambda x: abs(x - bearing))
        if dir == 360:
            dir = 0
        return dir
    
    #----------------------------------------------
    # Methods for gps
    #----------------------------------------------

    def current_position(self):
        x, y, z = self.gps.getValues()
        return x, y
    
    #----------------------------------------------
    # Methods for distance sensors
    #----------------------------------------------

    def ds_front_detected(self):
        return self.ds_front.getValue() < 1000
    
    def ds_right_detected(self):
        return self.ds_right.getValue() < 1000
    
    def ds_left_detected(self):
        return self.ds_left.getValue() < 1000