import math

import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory

try:
    import serial
except ImportError:
    serial = None

JOINTS = ['joint1', 'joint2', 'joint3', 'joint4']


def rad_to_servo(rad):
    """Map -pi/2..pi/2 rad to 0..180 deg and clamp."""
    deg = (rad + math.pi / 2.0) * 180.0 / math.pi
    return int(round(max(0.0, min(180.0, deg))))


class HardwareBridge(Node):
    def __init__(self):
        super().__init__('hardware_bridge')
        self.declare_parameter('port', '/dev/ttyUSB0')
        self.declare_parameter('baud', 115200)
        port = self.get_parameter('port').value
        baud = self.get_parameter('baud').value

        self.ser = None
        if serial is None:
            self.get_logger().warn('pyserial not installed: dry-run mode')
        else:
            try:
                self.ser = serial.Serial(port, baud, timeout=0.1)
                self.get_logger().info(f'Serial open on {port} @ {baud}')
            except Exception as e:
                self.get_logger().warn(
                    f'Cannot open {port} ({e}): dry-run mode, nothing is sent')

        self.angles = {name: 90 for name in JOINTS}
        self.create_subscription(
            JointTrajectory, '/arm_controller/joint_trajectory',
            self.on_traj, 10)
        self.get_logger().info('Hardware bridge ready')

    def on_traj(self, msg):
        if not msg.points:
            return
        target = msg.points[-1].positions
        for name, pos in zip(msg.joint_names, target):
            if name in self.angles:
                self.angles[name] = rad_to_servo(pos)
        line = ','.join(str(self.angles[n]) for n in JOINTS) + '\n'
        if self.ser is not None:
            try:
                self.ser.write(line.encode())
            except Exception as e:
                self.get_logger().error(f'Serial write failed: {e}')
        self.get_logger().info(f'Servo angles (deg): {line.strip()}')


def main(args=None):
    rclpy.init(args=args)
    node = HardwareBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    if node.ser is not None:
        node.ser.close()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
