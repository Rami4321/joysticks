#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy

# TODO: replace this with the actual arm goal message you define for the arm-controller layer.
# from carmy_motor_controller.msg import ArmTarget


class DualJoystickMapper(Node):
    def __init__(self):
        super().__init__('dual_joystick_mapper')

        # TODO: define the real arm target state here
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

        # Subscriptions
        self.sub_stage_1 = self.create_subscription(Joy, '/stage_1/joy', self.stage_1_callback, 10)
        self.sub_stage_2 = self.create_subscription(Joy, '/stage_2/joy', self.stage_2_callback, 10)

        # TODO: publish to the arm target topic instead of raw Twist messages
        # self.arm_target_pub = self.create_publisher(ArmTarget, '/arm_target', 10)

        # Optional dashboard timer for debugging
        self.timer = self.create_timer(1.0, self.print_dashboard)
        self.get_logger().info('Dual joystick mapper initialized.')
        self.get_logger().info('TODO: map joystick inputs into arm target commands.')

    def stage_1_callback(self, msg):
        if len(msg.axes) < 4 or len(msg.buttons) < 1:
            return

        # TODO: map axes/buttons for stage 1 to arm target fields
        self.stage_1['x'] = msg.axes[0]
        self.stage_1['y'] = msg.axes[1]
        self.stage_1['z'] = msg.axes[2]
        self.stage_1['knob'] = (msg.axes[3] + 1.0) / 2.0
        self.stage_1['trigger'] = bool(msg.buttons[0])

        # TODO: publish an ArmTarget message here
        # arm_target = ArmTarget()
        # arm_target.stage_1_angle = ...
        # arm_target.stage_2_angle = ...
        # arm_target.gripper = ...
        # arm_target.mode = ...
        # arm_target.enabled = ...
        # self.arm_target_pub.publish(arm_target)

    def stage_2_callback(self, msg):
        if len(msg.axes) < 4 or len(msg.buttons) < 1:
            return

        # TODO: map axes/buttons for stage 2 to arm target fields
        self.stage_2['x'] = msg.axes[0]
        self.stage_2['y'] = msg.axes[1]
        self.stage_2['z'] = msg.axes[2]
        self.stage_2['knob'] = (msg.axes[3] + 1.0) / 2.0
        self.stage_2['trigger'] = bool(msg.buttons[0])

        # TODO: publish an ArmTarget message here
        # arm_target = ArmTarget()
        # arm_target.stage_1_angle = ...
        # arm_target.stage_2_angle = ...
        # arm_target.gripper = ...
        # arm_target.mode = ...
        # arm_target.enabled = ...
        # self.arm_target_pub.publish(arm_target)

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
