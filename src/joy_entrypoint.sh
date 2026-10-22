#!/usr/bin/env bash
set -e

cat /workspace/src/ros_shell_setup.sh >> /root/.bashrc
source /root/.bashrc

apt-get update
apt-get install -y ros-jazzy-joy

echo "ROS environment ready. Keeping container alive..."
tail -f /dev/null