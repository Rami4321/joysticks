#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from carmy_motor_controller.msg import ArmTarget
from carmy_motor_controller.msg import MotorMotionControl
from carmy_motor_controller.msg import MotorFeedback
import math

# Constants
# How much to scale the arm target angles into motor commands. This is a placeholder value and should be tuned based on the actual arm mechanics.
GAIN =  math.pi * 10

STAGE_1_X_MOTOR_ID = 1
STAGE_1_Y_MOTOR_ID = 2
STAGE_2_X_MOTOR_ID = 3
STAGE_2_Y_MOTOR_ID = 4


ID_TO_MOTOR_NAME = {
    STAGE_1_X_MOTOR_ID: "stage_1_x",
    STAGE_1_Y_MOTOR_ID: "stage_1_y",
    STAGE_2_X_MOTOR_ID: "stage_2_x",
    STAGE_2_Y_MOTOR_ID: "stage_2_y"}


class ArmControllerNode(Node):
    def __init__(self):
        super().__init__('arm_controller_node')

        #subscribe to the arm target topic
        self.sub = self.create_subscription(ArmTarget, "/arm_target", self.handle_arm_target, 10)
        
        #subscript to the motor feedback topic to get the current motor positions 
        self.motor_feedback_sub = self.create_subscription(MotorFeedback, '/motor_feedback', self.handle_motor_feedback, 10)

        #publish motor commands to the custom motor message topic
        self.motor_pub = self.create_publisher(MotorMotionControl, '/motion_control', 10)
        self.timer = self.create_timer(0.1, self.publish_motor_commands)

        self.joystick_target = None  # Store the latest ArmTarget message
        self.pose = {name: [0.0, 0.0, 0.0, 0.0] for name in ID_TO_MOTOR_NAME.values()}  # Store the latest motor feedback
        

    # Callback for receiving arm target messages
    def handle_arm_target(self, msg: ArmTarget):
        # Log the received arm target for debugging
        self.get_logger().info(f"Received ArmTarget: stage_1_x_angle={msg.stage_1_x_angle}, stage_1_y_angle={msg.stage_1_y_angle}, stage_2_x_angle={msg.stage_2_x_angle}, stage_2_y_angle={msg.stage_2_y_angle}, gripper={msg.gripper}, mode={msg.mode}, enabled={msg.enabled}")
        
        self.joystick_target = msg

    
    # Callback for receiving motor feedback messages
    def handle_motor_feedback(self, msg: MotorFeedback):
        # Log the received motor feedback for debugging
        self.get_logger().info(f"Received MotorFeedback: motor_id={msg.motor_id}, position={msg.position}, velocity={msg.velocity}, torque={msg.torque}, temperature={msg.temperature}")
        
        self.pose[ID_TO_MOTOR_NAME[msg.motor_id]] = [msg.position, msg.velocity, msg.torque, msg.temperature]


    # Convert target pose/angles into MotorMotionControl messages
    def publish_motor_commands(self):
        target = self.joystick_target
        if target is None:
            return  # No target to process
        
        # Position, velocity, kp, kd, and torque 
        MotorMotions = []
        MotorMotions.append(self.build_motor_command(STAGE_2_X_MOTOR_ID, target.stage_2_x_angle * GAIN, 0.2, 1.0, 0.4, 1.0))
        MotorMotions.append(self.build_motor_command(STAGE_2_Y_MOTOR_ID, target.stage_2_y_angle * GAIN, 0.2, 1.0, 0.4, 1.0))
        MotorMotions.append(self.build_motor_command(STAGE_1_Y_MOTOR_ID, target.stage_1_y_angle * GAIN, 0.2, 1.0, 0.4, 1.0))
        MotorMotions.append(self.build_motor_command(STAGE_1_X_MOTOR_ID, target.stage_1_x_angle * GAIN, 0.2, 1.0, 0.4, 1.0))
        
        # Each motorMotion corresponds to a single motor's command. Publish each one to the motor command topic.
        for motorMotion in MotorMotions:
            self.motor_pub.publish(motorMotion)
            
        self.get_logger().info(f"Published MotorMotionControl commands for all motors based on ArmTarget: {target}")
        return 
    
    
    # Helper function to build a MotorMotionControl message for a given motor ID and parameters
    def build_motor_command(self, motor_id: int, position: float, velocity: float, kp: float, kd: float, torque: float) -> MotorMotionControl:
        if motor_id < 1 or motor_id > 4:
            self.get_logger().error(f"Invalid motor_id: {motor_id}. Must be between 1 and 4.")
            return None
        # Add other guard clauses here as needed for position, velocity, kp, kd, torque ranges.
        return MotorMotionControl(motor_id=motor_id, position=position, velocity=velocity, kp=kp, kd=kd, torque=torque)


def main(args=None):
    rclpy.init(args=args)
    node = ArmControllerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
