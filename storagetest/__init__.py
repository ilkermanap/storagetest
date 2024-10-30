
"""
fio --filename=/root/testfile 
    --size=500MB 
    --direct=1 
    --rw=randrw 
    --bs=512k 
    --ioengine=libaio 
    --iodepth=256 
    --runtime=8 
    --numjobs=4 
    --time_based 
    --group_reporting 
    --name=iops-test-job 
    --eta-newline=1 


fio --filename=/root/testfile --size=500MB --direct=1  --rw=randrw  --bs=512k --ioengine=libaio --iodepth=256 --runtime=8   --numjobs=4  --time_based  --group_reporting  --name=iops-test-job  --eta-newline=1

"""

import socket
import subprocess
from datetime import datetime
import json

class Storage:
    def __init__(self, testname="StorageTest", path=None) -> None:
        self.path = path
        self.testname = testname
        self.hostname = socket.gethostname()
        self.prefix = self.testname + "_" + self.hostname
        self.readings = {"read": {"bw": {}, "iops": {}},
                         "write": {"bw": {}, "iops": {}}}
        self.timestamp = None
    def parse(self, output):
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

            if (found_write == True):
                if line.find("bw") > -1:
                    parts = line.split(":")[1].split(",")
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

            if (found_read == True):
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

        self.timestamp = str(datetime.now()).replace(" ","T").replace(":","").split(".")[0]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output, errors = process.communicate()
        self.parse(output)
        self.save(size, bs)

    def save(self, size, bs):
        out = {"host" : self.hostname, "timestamp": self.timestamp, "filesize": size, "blocksize": bs, "results": self.readings}
        with open(f"{self.hostname}_{bs}_{self.timestamp}", "w") as outfile:
            json.dump(out, outfile)

sample ="""
fio-3.33
Starting 4 processes
storage_test_job: Laying out IO file (1 file / 10MiB)

storage_test_job: (groupid=0, jobs=4): err= 0: pid=118156: Wed Oct 30 11:22:41 2024
  read: IOPS=63.5k, BW=993MiB/s (1041MB/s)(7947MiB/8005msec)
    slat (usec): min=3, max=9413, avg= 8.88, stdev=63.02
    clat (usec): min=37, max=33235, avg=6753.65, stdev=4447.87
     lat (usec): min=95, max=33240, avg=6762.54, stdev=4448.16
    clat percentiles (usec):
     |  1.00th=[  506],  5.00th=[ 1139], 10.00th=[ 1663], 20.00th=[ 2737],
     | 30.00th=[ 3818], 40.00th=[ 4817], 50.00th=[ 5932], 60.00th=[ 7177],
     | 70.00th=[ 8586], 80.00th=[10290], 90.00th=[12911], 95.00th=[15139],
     | 99.00th=[19792], 99.50th=[21103], 99.90th=[25297], 99.95th=[26870],
     | 99.99th=[29754]
   bw (  KiB/s): min=915712, max=1124224, per=100.00%, avg=1017180.93, stdev=14246.72, samples=60
   iops        : min=57232, max=70264, avg=63573.73, stdev=890.41, samples=60
  write: IOPS=63.7k, BW=995MiB/s (1043MB/s)(7964MiB/8005msec); 0 zone resets
    slat (usec): min=3, max=11357, avg= 9.95, stdev=69.61
    clat (usec): min=1012, max=34687, avg=9314.74, stdev=4546.43
     lat (usec): min=1419, max=34700, avg=9324.68, stdev=4546.36
    clat percentiles (usec):
     |  1.00th=[ 3064],  5.00th=[ 3490], 10.00th=[ 4080], 20.00th=[ 5211],
     | 30.00th=[ 6325], 40.00th=[ 7373], 50.00th=[ 8455], 60.00th=[ 9765],
     | 70.00th=[11207], 80.00th=[13042], 90.00th=[15533], 95.00th=[17957],
     | 99.00th=[22414], 99.50th=[24511], 99.90th=[28967], 99.95th=[30278],
     | 99.99th=[32637]
   bw (  KiB/s): min=921632, max=1135488, per=99.92%, avg=1018014.60, stdev=14115.70, samples=60
   iops        : min=57602, max=70968, avg=63625.73, stdev=882.22, samples=60
  lat (usec)   : 50=0.01%, 100=0.01%, 250=0.08%, 500=0.41%, 750=0.67%
  lat (usec)   : 1000=0.83%
  lat (msec)   : 2=4.66%, 4=13.93%, 10=49.54%, 20=28.16%, 50=1.72%
  cpu          : usr=7.85%, sys=20.19%, ctx=714260, majf=0, minf=47
  IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=0.1%, 16=0.1%, 32=0.1%, >=64=100.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.1%
     issued rwts: total=508597,509710,0,0 short=0,0,0,0 dropped=0,0,0,0
     latency   : target=0, window=0, percentile=100.00%, depth=256

Run status group 0 (all jobs):
   READ: bw=993MiB/s (1041MB/s), 993MiB/s-993MiB/s (1041MB/s-1041MB/s), io=7947MiB (8333MB), run=8005-8005msec
  WRITE: bw=995MiB/s (1043MB/s), 995MiB/s-995MiB/s (1043MB/s-1043MB/s), io=7964MiB (8351MB), run=8005-8005msec

Disk stats (read/write):
  nvme1n1: ios=499669/500373, merge=0/60, ticks=3044640/4275391, in_queue=7320034, util=84.15%
"""