from storagetest import Storage, sample

stest = Storage(testname="deneme", path="/tmp")

stest.parse(sample)


#stest.test(size="10MB", bs="16k")