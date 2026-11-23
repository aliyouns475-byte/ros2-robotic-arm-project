import rclpy
from rclpy.node import Node
from builtin_interfaces.msg import Duration
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

JOINTS = ['joint1', 'joint2', 'joint3', 'joint4']

POSES = [
    [0.0, 0.0, 0.0, 0.0],
    [1.0, 0.5, 0.5, 0.3],
    [-1.0, -0.5, 0.8, -0.3],
]


class TrajectoryPublisher(Node):
    def __init__(self):
        super().__init__('trajectory_publisher')
        self.pub = self.create_publisher(
            JointTrajectory, '/arm_controller/joint_trajectory', 10)
        self.index = 0
        self.timer = self.create_timer(4.0, self.send_next)
        self.get_logger().info('Trajectory publisher started')

    def send_next(self):
        msg = JointTrajectory()
        msg.joint_names = JOINTS
        point = JointTrajectoryPoint()
        point.positions = POSES[self.index]
        point.time_from_start = Duration(sec=2, nanosec=0)
        msg.points = [point]
        self.pub.publish(msg)
        self.get_logger().info(f'Sent pose {self.index}: {POSES[self.index]}')
        self.index = (self.index + 1) % len(POSES)


def main(args=None):
    rclpy.init(args=args)
    node = TrajectoryPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
