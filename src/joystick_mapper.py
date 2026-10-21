#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy

class JoystickMapper(Node):
    def __init__(self):
        super().__init__('joystick_mapper')
        
        # Subscribe to the raw joystick data from joy_node
        self.subscription = self.create_subscription(
            Joy,
            '/joy',
            self.joy_callback,
            10
        )
        self.get_logger().info("Joystick Semantic Mapper Node Started!")

    def joy_callback(self, msg):
        # Prevent crash bugs if the array isn't fully filled yet
        if len(msg.axes) < 4 or len(msg.buttons) < 1:
            return

        # --- THRUSTMASTER T.16000M SEMANTIC MAPPING ---
        
        # 1. Map Raw Axes to Named Structural Fields
        stage_1_x_axis = msg.axes[0]  # Stick X (Left / Right)
        stage_1_y_axis = msg.axes[1]  # Stick Y (Forward / Backward)
        twist_yaw      = msg.axes[2]  # Twist Stick Action
        slider_throttle= msg.axes[3]  # Linear slider at the base

        # 2. Map Raw Buttons to Named Functional Fields
        trigger_pressed = bool(msg.buttons[0])
        thumb_button_center = bool(msg.buttons[1])

        # --- LOG / EXECUTE ACTIONS ---
        # Print your clean named variables out to verify the data path works!
        self.get_logger().info(
            f"Stage 1 [X: {stage_1_x_axis:+.2f} | Y: {stage_1_y_axis:+.2f}] | Trigger: {trigger_pressed}"
        )

def main(args=None):
    rclpy.init(args=args)
    node = JoystickMapper()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
