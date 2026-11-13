#!/usr/bin/env bash
set -e

cat /workspace/src/ros_shell_setup.sh >> /root/.bashrc
source /root/.bashrc

apt-get update
apt-get install -y ros-jazzy-joy jstest-gtk net-tools kmod iproute2

source /opt/ros/jazzy/setup.bash

colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release

echo "ROS environment ready. Keeping container alive..."
tail -f /dev/null