import unittest
import numpy as np
from drivecycle import trajectory
# import pickle


class TestDrivecycle(unittest.TestCase):

    def test_trajectory(self):

        test_data = np.array([[0., 0., 0.], [10., 10., 50.],[20., 0., 100.]])

        traj = trajectory.const_accel(vi=0, v_target=12, di=0, df=100, step=10)

        self.assertTrue(np.allclose(traj.get_trajectory(), test_data))
    

