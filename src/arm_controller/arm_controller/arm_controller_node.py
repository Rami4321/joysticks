#!/usr/bin/env python3

import rclpy
from rclpy.node import Node


class ArmControllerNode(Node):
    def __init__(self):
        super().__init__('arm_controller_node')

        # TODO: subscribe to the arm target topic
        # self.sub = self.create_subscription(...)

        # TODO: publish motor commands to the custom motor message topic
        # self.pub = self.create_publisher(...)

        self.get_logger().info('Arm controller node initialized.')
        self.get_logger().info('TODO: implement arm target -> motor command conversion here.')

    # TODO: implement callback for target topic
    # def target_callback(self, msg):
    #     pass

    # TODO: implement helper to convert target pose/angles into MotorMotionControl messages
    # def build_motor_command(self, motor_id, position, velocity, kp, kd, torque):
    #     return MotorMotionControl(...)


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
