# Arm-level target for a 2-stage continuum arm
# This message is intended for the teleop mapper and planner layer.
# It should not be used directly by the CAN driver / motor controller layer.

float64 stage_1_angle
float64 stage_2_angle
float64 gripper
uint8 mode
bool enabled
