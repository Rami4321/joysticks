# Carmy Controller Stack

This project runs a ROS 2 Jazzy container for the Carmy controller and joystick stack. The setup uses Docker Compose to mount the project source folder into a ROS 2 environment and starts a container named `carmy_controller_jazzy`.

## What this repo contains

- `docker-compose.yml` — Docker configuration for the ROS2 container
- `start.bash` — convenience script to bring up the container
- `SetupCan.bash` — creates the CAN interface used by the controller stack
- `src/` — ROS 2 package source and helper scripts
  - `joy_entrypoint.sh` — installs ROS joystick support and keeps the container alive
  - `ros_shell_setup.sh` — loads ROS environment in the shell
  - `joystick_mapper.py` and `joystick_translator/` — joystick-related code
  - `carmy_motor_controller/` — motor controller ROS package

## Prerequisites

Before running anything, make sure:

- Docker is installed and running
- `docker compose` is available
- the CAN USB adapter is plugged in and visible as `/dev/ttyACM*`
- your system has permission to use the host display if you want to launch GUI tools such as `rqt`

## Start the container

From the project root:

```bash
./start.bash
```

This script does the following:

1. Runs `bash ./SetupCan.bash`
2. Starts Docker Compose in detached mode
3. Opens a shell into the running container

## Run the stack from the container

Once inside the container, you can run commands like:

```bash
source /opt/ros/jazzy/setup.bash
source /workspace/install/setup.bash
```

If the workspace has not been built yet, build the ROS workspace from `/workspace`:

```bash
cd /workspace
colcon build
source install/setup.bash
```

Then launch the appropriate nodes for your robot controller:

```bash
ros2 launch <package_name> <launch_file>
```

To run the Motor controller node

```bash
ros2 run carmy_motor_controller rs_motor_ros2_node
``` 

To run the Joystick controller node/s

```bash
ros2 launch joystick_translator joystick_launch.py
```

## GUI support (for rqt / visualization tools)

If you want to run GUI tools from inside the container, run this on the host before launching the app:

```bash
xhost +local:root
```

Then inside the container:

```bash
rqt
```

## Container shell workflow

To attach to the running container manually:

```bash
docker exec -it carmy_controller_jazzy bash -l
```

To stop the container:

```bash
docker compose down
```

## Troubleshooting

### No CAN adapter found

If `SetupCan.bash` prints:

```bash
Error: No CAN adapter found on /dev/ttyACM*. Is it plugged in?
```

then:

- verify the USB CAN adapter is connected
- check `ls /dev/ttyACM*`
- ensure the adapter is visible before starting the stack

### Container will not start

Check the logs:

```bash
docker compose logs
```

### ROS environment not set

Inside the container, run:

```bash
source /opt/ros/jazzy/setup.bash
source /workspace/install/setup.bash
```

### `rqt` cannot connect to display

Run on the host:

```bash
xhost +local:root
```

Then re-run the GUI tool from inside the container.

## Notes

This repository is set up to use a ROS 2 Jazzy desktop container and a host-side CAN configuration. The container is intended to be the working environment for code development and runtime testing, while the host machine provides access to hardware interfaces like USB CAN adapters and the display server.
