# Robotic Arm: URDF, Simulation and Hardware Control (ROS 2 Jazzy)

**Course:** Robotics, Advanced ROS 2 Assignment
**ROS 2 distribution:** Jazzy (Ubuntu 24.04), Gazebo Sim (Harmonic)

## Team Members

| ID | Name |
|----|------|
| 2304173 | Ali Abdelhamid Ali Younis (علي عبد الحميد علي يونس) |
| 2304178 | Mohamed Ahmed Hamed (محمد أحمد حامد) |
| 2304175 | Moataz Mohamed Abdelaty (معتز محمد عبد العاطي) |

## Overview

A 4-joint robotic arm is modelled in URDF (xacro), simulated in Gazebo and visualized in RViz2. A single command published on `/arm_controller/joint_trajectory` moves the arm in Gazebo and RViz2 at the same time, and the same command is forwarded by a hardware bridge node to an Arduino Uno that drives servo motors.

```
                              /arm_controller/joint_trajectory
 trajectory_publisher  ─┐              (JointTrajectory)
 arm_gui (sliders)     ─┴──────────────────┬───────────────────────────┐
                                           │                           │
                                           ▼                           ▼
                          Gazebo (arm_controller,            hardware_bridge
                          gz_ros2_control)                   (rad → 0..180 deg)
                                           │                           │ USB serial
                                           ▼                           ▼
                                    /joint_states               Arduino Uno firmware
                                           │                           │ PWM
                                           ▼                           ▼
                                  robot_state_publisher           Servo motors
                                           │
                                           ▼
                                         RViz2
```

## Repository Structure

```
.
├── README.md
├── arm_description/     # URDF (xacro) and a RViz display launch file
├── arm_simulation/      # Gazebo launch file and ros2_control controllers config
├── arm_control/         # Python nodes: trajectory publisher, slider GUI, hardware bridge
└── arm_firmware/        # Arduino sketch (arm_firmware.ino)
```

## Package Descriptions

### `arm_description`
- `urdf/arm.urdf.xacro`: the arm model.
- `launch/display.launch.py`: shows the arm in RViz2 with `joint_state_publisher_gui` (model check only).

**Kinematic chain:** `base_link → joint1 → L1 → joint2 → L2 → joint3 → L3 → joint4 → end_effector`

| Link | Length |
|------|--------|
| base_link | 8 cm |
| L1 | 12 cm |
| L2 | 15 cm |
| L3 | 9 cm |
| end_effector (gripper) | 6 cm |

| Joint | Type | Axis | Limits |
|-------|------|------|--------|
| joint1 | revolute | Z | -1.57 to 1.57 rad |
| joint2 | revolute | Y | -1.57 to 1.57 rad |
| joint3 | revolute | Y | -1.57 to 1.57 rad |
| joint4 | revolute | Y | -1.57 to 1.57 rad |

Every link has `<visual>`, `<collision>` and `<inertial>`. The arm is attached to a `world` link so it stays fixed to the ground in Gazebo. The `ros2_control` block (`gz_ros2_control/GazeboSimSystem`) exposes position command interfaces for the four joints.

### `arm_simulation`
- `launch/sim.launch.py`: starts the Gazebo server (`empty.sdf`) and GUI, publishes the robot description, spawns the arm, bridges `/clock`, starts `joint_state_broadcaster` and `arm_controller` (a `JointTrajectoryController`) and opens RViz2.
- `config/controllers.yaml`: controller manager and controller parameters.

The Gazebo GUI is started separately from the server with `QT_QPA_PLATFORM=xcb` and the `ogre` render engine, because the default combined start froze on our machine (Ubuntu with Wayland and hybrid graphics).

### `arm_control`

| Executable | Description |
|------------|-------------|
| `trajectory_publisher` | Publishes `JointTrajectory` messages to `/arm_controller/joint_trajectory`, cycling through 3 poses every 4 seconds. |
| `arm_gui` | Tkinter window with one slider per joint (and a Zero button). Moving a slider publishes a `JointTrajectory` message on the same topic. |
| `hardware_bridge` | Subscribes to `/arm_controller/joint_trajectory`, converts angles to servo degrees and sends them over USB serial to the Arduino. |

### `arm_firmware`
`arm_firmware.ino`: Arduino Uno sketch that reads angle lines from the serial port and drives the servos with the `Servo` library.

## Dependencies

```bash
sudo apt update
sudo apt install -y ros-jazzy-desktop ros-jazzy-ros-gz ros-jazzy-xacro \
  ros-jazzy-joint-state-publisher-gui ros-jazzy-ros2-control \
  ros-jazzy-ros2-controllers ros-jazzy-gz-ros2-control \
  python3-tk python3-serial
```

For the firmware: Arduino IDE (the `Servo` library is included with it).

## Build Steps

```bash
mkdir -p ~/arm_ws/src
cd ~/arm_ws/src
git clone <REPO_URL> .
cd ~/arm_ws
colcon build
source install/setup.bash
```

Every new terminal must run `source ~/arm_ws/install/setup.bash` first.

## How to Run

Use three terminals.

**Terminal 1: simulation (Gazebo + RViz2)**

```bash
source ~/arm_ws/install/setup.bash && ros2 launch arm_simulation sim.launch.py
```

In RViz2, set **Fixed Frame** to `base_link`, click **Add**, choose **RobotModel** and set **Description Topic** to `/robot_description`.

**Terminal 2: hardware bridge**

```bash
source ~/arm_ws/install/setup.bash && ros2 run arm_control hardware_bridge
```

If no board is connected, the node prints a warning and runs in dry-run mode: it prints the servo angles it would send, without sending anything. With a board connected:

```bash
ros2 run arm_control hardware_bridge --ros-args -p port:=/dev/ttyACM0
```

**Terminal 3: slider GUI**

```bash
source ~/arm_ws/install/setup.bash && ros2 run arm_control arm_gui
```

Move the sliders: the arm moves in Gazebo and RViz2 at the same time, and the bridge prints the servo angles. Close the GUI window with the X button.

Instead of the GUI, the automatic publisher can be used (do not run both together):

```bash
source ~/arm_ws/install/setup.bash && ros2 run arm_control trajectory_publisher
```

## Commands to Try Each Requirement

**URDF in RViz2 only** (no Gazebo):

```bash
ros2 launch arm_description display.launch.py
```

**Check the arm description converts without errors:**

```bash
xacro ~/arm_ws/src/arm_description/urdf/arm.urdf.xacro > /dev/null && echo XACRO_OK
```

**Controllers are active:**

```bash
ros2 control list_controllers
```

**Joint states come back from Gazebo:**

```bash
ros2 topic echo /joint_states --once
```

**Send one command by hand** (moves Gazebo and RViz2 together):

```bash
ros2 topic pub --once /arm_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory "{joint_names: ['joint1','joint2','joint3','joint4'], points: [{positions: [1.0, 0.5, 0.5, 0.3], time_from_start: {sec: 2, nanosec: 0}}]}"
```

## Hardware Communication

### Transport
USB serial (pyserial on the PC side, `Serial` on the Arduino side) at **115200 baud**. The default port in the bridge is `/dev/ttyUSB0` and can be changed with the `port` parameter (an Arduino Uno usually appears as `/dev/ttyACM0`).

### Message format
One plain-text line per command, terminated by a newline:

```
a1,a2,a3,a4\n
```

Each value is an integer servo angle in degrees (0 to 180), in the order joint1 to joint4. Example: `90,65,90,90`.

### Angle conversion
The bridge takes the last point of each `JointTrajectory` message and converts each joint angle from radians to the servo range, then clamps it:

```
servo_deg = clamp( (rad + π/2) * 180 / π , 0 , 180 )
```

So -1.57 rad maps to 0°, 0 rad maps to 90° and +1.57 rad maps to 180°. The firmware clamps each received value to 0..180 again before writing it to the servo.

### Wiring (Arduino Uno)

| Board pin | Connects to |
|-----------|-------------|
| 9 | Servo 1 signal wire (joint1, base rotation) |
| 10 | Servo 2 signal wire (joint2) |
| 11 | Servo 3 signal wire (joint3) |
| 6 | Servo 4 signal wire (joint4) |
| GND | Servo GND, shared with the external supply ground |

Power the servos from a suitable external supply (about 5 V, with enough current for the servos) and connect its ground to the Arduino GND. With only two servos, use pins 9 and 10.

### Uploading the firmware
1. Open `arm_firmware/arm_firmware.ino` in the Arduino IDE.
2. Select **Tools > Board > Arduino Uno** and the correct **Port**.
3. Click **Upload**.

### Testing status
The simulation, the slider GUI and the bridge (in dry-run mode, printing the angles) were tested together. The firmware was not yet tested on a physical board at the time of writing.
