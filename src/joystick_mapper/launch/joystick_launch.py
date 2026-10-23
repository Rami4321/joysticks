import os
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    nodes = []

    if os.path.exists('/dev/input/js0'):
        nodes.append(
            Node(
                package='joy',
                executable='joy_node',
                name='joy_stage_1',
                output='log',
                parameters=[{
                    'dev': '/dev/input/js0',
                    'device_id': 0,
                    'deadzone': 0.05,
                    'autorepeat_rate': 20.0,
                }],
                remappings=[('/joy', '/stage_1/joy')],
            )
        )

    if os.path.exists('/dev/input/js1'):
        nodes.append(
            Node(
                package='joy',
                executable='joy_node',
                name='joy_stage_2',
                output='log',
                parameters=[{
                    'dev': '/dev/input/js1',
                    'device_id': 1,
                    'deadzone': 0.05,
                    'autorepeat_rate': 20.0,
                }],
                remappings=[('/joy', '/stage_2/joy')],
            )
        )

    nodes.append(
        Node(
            package='joystick_mapper',
            executable='joystick_mapper_node',
            name='dual_joystick_mapper',
            output='screen',
        )
    )

    return LaunchDescription(nodes)