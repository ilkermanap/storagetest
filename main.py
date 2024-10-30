"""
Storage test application main file
"""
from storagetest import Storage

stest = Storage(testname="deneme", path="/tmp")
stest.test(size="10MB", bs="16k")
