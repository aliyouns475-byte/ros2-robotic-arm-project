import tkinter as tk

import rclpy
from rclpy.node import Node
from builtin_interfaces.msg import Duration
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

JOINTS = ['joint1', 'joint2', 'joint3', 'joint4']
LIMIT = 1.57


class GuiNode(Node):
    def __init__(self):
        super().__init__('arm_gui')
        self.pub = self.create_publisher(
            JointTrajectory, '/arm_controller/joint_trajectory', 10)

    def send(self, positions):
        msg = JointTrajectory()
        msg.joint_names = JOINTS
        point = JointTrajectoryPoint()
        point.positions = [float(p) for p in positions]
        point.time_from_start = Duration(sec=0, nanosec=500000000)
        msg.points = [point]
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = GuiNode()

    root = tk.Tk()
    root.title('Arm Control')
    sliders = []

    def on_change(_value=None):
        node.send([s.get() for s in sliders])

    def zero():
        for s in sliders:
            s.set(0.0)
        on_change()

    for name in JOINTS:
        tk.Label(root, text=name).pack(padx=10, pady=(8, 0))
        s = tk.Scale(root, from_=-LIMIT, to=LIMIT, resolution=0.01,
                     orient=tk.HORIZONTAL, length=400)
        s.set(0.0)
        s.config(command=on_change)
        s.pack(padx=10)
        sliders.append(s)

    tk.Button(root, text='Zero', command=zero).pack(pady=10)

    def on_close():
        node.destroy_node()
        rclpy.shutdown()
        root.destroy()

    root.protocol('WM_DELETE_WINDOW', on_close)
    root.mainloop()


if __name__ == '__main__':
    main()
