#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist

class DualJoystickMapper(Node):
    def __init__(self):
        super().__init__('dual_joystick_mapper')
        
        # Internal data storage (pure physical positions)
        self.stg1 = {'x': 0.0, 'y': 0.0, 'z': 0.0, 'knob': 0.0, 'trigger': False}
        self.stg2 = {'x': 0.0, 'y': 0.0, 'z': 0.0, 'knob': 0.0, 'trigger': False}

        # Subscriptions
        self.sub_stage_1 = self.create_subscription(Joy, '/stage_1/joy', self.stage_1_callback, 10)
        self.sub_stage_2 = self.create_subscription(Joy, '/stage_2/joy', self.stage_2_callback, 10)
        
        # Publishers
        self.pub_stage_1 = self.create_publisher(Twist, '/stage_1/commands', 10)
        self.pub_stage_2 = self.create_publisher(Twist, '/stage_2/commands', 10)
        
        # Dashboard display timer
        self.timer = self.create_timer(0.1, self.print_dashboard)
        self.get_logger().info("Pure Position Dual Joystick Dashboard Started!")

    def stage_1_callback(self, msg):
        if len(msg.axes) < 4 or len(msg.buttons) < 1: return
        
        # --- FIXED INDEX EXTRACTIONS ---
        self.stg1['x'] = msg.axes[0]   # Left / Right Tilt (Single Float)
        self.stg1['y'] = msg.axes[1]   # Forward / Backward Tilt (Single Float)
        self.stg1['z'] = msg.axes[2]   # Twist Action (Single Float)
        
        # Shift the raw knob index 3 (-1.0 to 1.0) into a clean percentage display (0.0 to 1.0)
        self.stg1['knob'] = (msg.axes[3] + 1.0) / 2.0
        self.stg1['trigger'] = bool(msg.buttons[0])

        # Publish the un-multiplied raw stick coordinates straight into the Twist envelope
        cmd = Twist()
        cmd.linear.x = self.stg1['y']
        cmd.linear.y = self.stg1['x']
        cmd.angular.z = self.stg1['z']
        self.pub_stage_1.publish(cmd)

    def stage_2_callback(self, msg):
        if len(msg.axes) < 4 or len(msg.buttons) < 1: return
        
        # --- FIXED INDEX EXTRACTIONS ---
        self.stg2['x'] = msg.axes[0]
        self.stg2['y'] = msg.axes[1]
        self.stg2['z'] = msg.axes[2]
        
        self.stg2['knob'] = (msg.axes[3] + 1.0) / 2.0
        self.stg2['trigger'] = bool(msg.buttons[0])

        # Publish the un-multiplied raw stick coordinates straight into the Twist envelope
        cmd = Twist()
        cmd.linear.x = self.stg2['y']
        cmd.linear.y = self.stg2['x']
        cmd.angular.z = self.stg2['z']
        self.pub_stage_2.publish(cmd)

    def print_dashboard(self):
        print("\033[H\033[J", end="") # Clear terminal cleanly
        print("=========================================================================")
        print("               THRUSTMASTER T.16000M PURE POSITION PANEL                 ")
        print("=========================================================================")
        print(f" [STAGE 1] X: {self.stg1['x']:+.2f} | Y: {self.stg1['y']:+.2f} | Z: {self.stg1['z']:+.2f} | Knob Slider: {self.stg1['knob']*100:3.0f}% | Trig: {self.stg1['trigger']}")
        print(f" [STAGE 2] X: {self.stg2['x']:+.2f} | Y: {self.stg2['y']:+.2f} | Z: {self.stg2['z']:+.2f} | Knob Slider: {self.stg2['knob']*100:3.0f}% | Trig: {self.stg2['trigger']}")
        print("=========================================================================")
        print(" Press Ctrl+C to exit safely.")

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
