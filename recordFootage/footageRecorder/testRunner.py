import os
import time

import sendSteps as ss
import recorder as rec
import math


def simple_directions(speed=10, dist=100, delay=2):
    """
    Return some simple directions

    move to 100 mm at the speed of mm_per_s and wait two seconds
    return to home and  wait two seconds
    repeat 5 times

    :param speed:
    Speed with which to run this test
    :param dist:
    distance to move
    :param delay:
    time to wait
    :return:
    """
    params = []

    for i in range(20):
        params.append((dist, speed, delay))
        params.append((0, speed, delay))

    return params


class TestRunner:

    def __init__(self, name="a_test"):
        """
        Class for executing a series of moves on the test setup and recording the resulting images/video
        :param name:
        Name of this test setup
        """
        self.rootPath = "./"

        # how many fps to use in the recording
        self.fps = 30

        self.mm_per_step = 92.5 / 2048

    def run_test(self, directions, prefix="some_params"):
        """

        :param directions:
        A vector of coordinates to drive to at a specified Speed
        :type directions: list of (position,speed,delay)

        :param prefix:
        A prefix to the name describing the directions/parameters used
        :type prefix: str
        """

        # path = os.path.join()

        pos = 0
        for d in directions:
            aim_position = self.mm_to_step(d[0])
            speed = d[1]
            delay = d[2]

            ss.set_speed(self.mm_per_sec_to_mikros(speed))

            dir = 0 if aim_position == pos else 1 if aim_position > pos else -1
            dist = abs(aim_position - pos)
            print(dir, dist)
            ss.do_cardinal(dir, dir, dist)

            time.sleep(delay)

            pos = aim_position

        ss.wait_for_finish()

    def mm_to_step(self, dist):
        """
        Convert a distance from millimeters to a number of steps for the stepper motor
        :param dist: distance in mm
        :type dist: float
        :return:
        :rtype:int
        number of steps
        """
        return int(math.floor(dist / self.mm_per_step))

    def mm_per_sec_to_mikros(self, mm_per_sec):
        """
            Convert a speed from mm per second to a time intervll in microseconds to wait between steps

            Throw an error if the speed is faster than the current setup can manage
            :param mm_per_sec: Speed
            :type mm_per_sec: float
            :return:
            :rtype:int
            Length of the interval in microseconds
        """
        intervall = int(math.floor((1 / self.mm_to_step(mm_per_sec) * 1e6)))
        if intervall < 600:
            raise Exception("Speed to great for setup: " + str(intervall) + " mirkos")
        return intervall

    def params_to_file(self, path, directions=None):
        """
        A function to save all relevant Parameters of a test setup to a text file for later review
        :param path:
        The path to save to
        :type path: str

        :param directions:
        """
        pass


if __name__ == "__main__":
    myTestRunner = TestRunner()
    recorder = rec.Recorder(save_name="motor_test_7")
    directions = simple_directions(speed=60, dist=30, delay=0)
    for d in directions:
        print(d)
    recorder.start_recording()
    #myTestRunner.run_test(directions)
    time.sleep(20)
    recorder.stop_recording()
    print("finished test")
