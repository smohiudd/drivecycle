import unittest
import numpy as np

# from drivecycle.trajectory import Trajectory
from drivecycle import trajectory
from drivecycle import utils


class TestDrivecycle(unittest.TestCase):

    def test_trajectory(self):

        test_data = np.array([[0., 0., 0.], [0., 0., 0.], [10., 10., 50.],
                              [20., 0., 100.]])

        traj = trajectory.Trajectory(vi=0, v_target=20, di=0, df=100, step=10)
        traj.const_accel()

        self.assertTrue(np.allclose(traj.get_trajectory(), test_data))
