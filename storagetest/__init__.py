"""
Storage test module
"""
import socket
import subprocess
from datetime import datetime
import json


class Storage:
    """This module provides a wrapper to fio command"""
    def __init__(self, testname="StorageTest", path=None) -> None:
        self.path = path
        self.testname = testname
        self.hostname = socket.gethostname()
        self.prefix = self.testname + "_" + self.hostname
        self.readings = {"read": {"bw": {}, "iops": {}},
                         "write": {"bw": {}, "iops": {}}}
        self.timestamp = None

    def parse(self, output):
        """

        :param output: Test command output to parse
        :return: Updates the class variable self.readings.
        """
        lines = output.splitlines()
        found_write = False
        found_read = False
        for line in lines:
            if line.find("IO depths") > -1:
                break
            if line.find("read:") > -1:
                found_read = True

            if line.find("write:") > -1:
                found_write = True
                found_read = False

            if found_write:
                if line.find("bw") > -1:
                    parts = line.split(":", maxsplit=1)[1].split(",")
                    for part in parts:
                        name, value = part.strip().split("=")
                        if name != "per":
                            value = float(value)
                            self.readings["write"]["bw"][name] = value
                if line.find("iops") > -1:
                    parts = line.split(":")[1].split(",")
                    for part in parts:
                        name, value = part.strip().split("=")
                        value = float(value)
                        self.readings["write"]["iops"][name] = value

            if found_read:
                if line.find("bw") > -1:
                    parts = line.split(":")[1].split(",")
                    for part in parts:
                        name, value = part.strip().split("=")
                        if name != "per":
                            value = float(value)
                            self.readings["read"]["bw"][name] = value
                if line.find("iops") > -1:
                    parts = line.split(":")[1].split(",")
                    for part in parts:
                        name, value = part.strip().split("=")
                        value = float(value)
                        self.readings["read"]["iops"][name] = value

    def test(self, size="500MB", bs="2k", runtime=8, numjobs=4):
        """
        Runs a test using fio command with provided parameters
        After the test, performance metrics are parsed and saved into a
        json file as well as the full output in a text file.
        :param size:
        :param bs:
        :param runtime:
        :param numjobs:
        :return:
        """
        cmd = ["fio",
               f"--filename={self.path}/testfile",
               f"--size={size}",
               "--direct=1",
               "--rw=randrw",
               f"--bs={bs}",
               "--ioengine=libaio",
               "--iodepth=256",
               f"--runtime={runtime}",
               f"--numjobs={numjobs}",
               "--time_based",
               "--group_reporting",
               "--name=storage_test_job",
               "--eta-newline=1"
               ]

        self.timestamp = str(datetime.now()).replace(" ", "T").replace(":", "").split(".",
                                                                                      maxsplit=1)[0]
        output = None
        with subprocess.Popen(cmd, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, text=True) as process:
            output, _ = process.communicate()
        self.parse(output)
        self.save(size, bs)
        with open(f"{self.hostname}_{bs}_{self.timestamp}.txt", "w", encoding="utf-8") as outfile:
            outfile.write(output)

    def save(self, size, bs):
        """
        :param size: File size used in test
        :param bs: Block size used in the test
        :return: None, creates a json file
        """
        out = {"host": self.hostname,
               "timestamp": self.timestamp,
               "filesize": size,
               "blocksize": bs,
               "results": self.readings}
        with open(f"{self.hostname}_{bs}_{self.timestamp}.json", "w", encoding="utf-8") as outfile:
            json.dump(out, outfile)
