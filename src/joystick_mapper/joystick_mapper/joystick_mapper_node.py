#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from carmy_motor_controller.msg import ArmTarget


class DualJoystickMapper(Node):
    def __init__(self):
        super().__init__('dual_joystick_mapper')

        # Arm target state: two variables per stage, for two stages.
        self.stage_1 = {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0,
            'knob': 0.0,
            'trigger': False,
        }
        self.stage_2 = {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0,
            'knob': 0.0,
            'trigger': False,
        }
        self.enabled = False
        self.mode = 0

        # Subscriptions
        self.sub_stage_1 = self.create_subscription(Joy, '/stage_1/joy', self.stage_1_callback, 10)
        self.sub_stage_2 = self.create_subscription(Joy, '/stage_2/joy', self.stage_2_callback, 10)

        # publish to the arm target topic instead of raw Twist messages
        self.arm_target_pub = self.create_publisher(ArmTarget, '/arm_target', 10)
        
        #callback so that the arm target is published at a regular interval, even if no new joystick messages are received
        self.timer = self.create_timer(0.1, self.publish_arm_target)

        # Optional dashboard timer for debugging
        self.timer = self.create_timer(1.0, self.print_dashboard)
        self.get_logger().info('Dual joystick mapper initialized.')
        self.get_logger().info('Mapping joystick inputs into the 2D-per-stage arm target format.')

    def publish_arm_target(self):
        arm_target = ArmTarget()
        arm_target.stage_1_x_angle = self.stage_1['x']
        arm_target.stage_1_y_angle = self.stage_1['y']
        arm_target.stage_2_x_angle = self.stage_2['x']
        arm_target.stage_2_y_angle = self.stage_2['y']
        arm_target.gripper = 0.0
        arm_target.mode = self.mode
        arm_target.enabled = self.enabled
        self.arm_target_pub.publish(arm_target)

    def stage_1_callback(self, msg):
        if len(msg.axes) < 4 or len(msg.buttons) < 1:
            return

        # map axes/buttons for stage 1 to arm target fields
        self.stage_1['x'] = msg.axes[0]
        self.stage_1['y'] = msg.axes[1]
        self.stage_1['z'] = msg.axes[2]
        self.stage_1['knob'] = (msg.axes[3] + 1.0) / 2.0
        self.stage_1['trigger'] = bool(msg.buttons[0])
        self.enabled = self.stage_1['trigger'] or self.stage_2['trigger']

    def stage_2_callback(self, msg):
        if len(msg.axes) < 4 or len(msg.buttons) < 1:
            return

        self.stage_2['x'] = msg.axes[0]
        self.stage_2['y'] = msg.axes[1]
        self.stage_2['z'] = msg.axes[2]
        self.stage_2['knob'] = (msg.axes[3] + 1.0) / 2.0
        self.stage_2['trigger'] = bool(msg.buttons[0])
        self.enabled = self.stage_1['trigger'] or self.stage_2['trigger']

    def print_dashboard(self):
        message = (
            f"[STAGE 1] X: {self.stage_1['x']:+.2f} | Y: {self.stage_1['y']:+.2f} | Z: {self.stage_1['z']:+.2f} | "
            f"Knob: {self.stage_1['knob'] * 100:3.0f}% | Trigger: {self.stage_1['trigger']} | "
            f"[STAGE 2] X: {self.stage_2['x']:+.2f} | Y: {self.stage_2['y']:+.2f} | Z: {self.stage_2['z']:+.2f} | "
            f"Knob: {self.stage_2['knob'] * 100:3.0f}% | Trigger: {self.stage_2['trigger']}"
        )
        self.get_logger().info(message)


def main(args=None):
    rclpy.init(args=args)
    node = DualJoystickMapper()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
