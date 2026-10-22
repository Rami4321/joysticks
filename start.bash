#!/bin/bash

echo "Starting ROS2 environment..."
# First setup the CAN interface
bash ./SetupCan.bash

# This should start the ROS2 enviroment, then run the motor controller node
CONTAINER_NAME="carmy_controller_jazzy"

xhost +local:root

sudo docker compose up -d
docker exec -it $CONTAINER_NAME bash -l