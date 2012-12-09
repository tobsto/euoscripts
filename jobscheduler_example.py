#!/usr/bin/python

import jobscheduler as js

q=js.queue('qfile')
q.clear()
q.add('sleep 1')
q.remove()
q.add('sleep 1')
q.add('sleep 2')
q.list()
print q.get()

jobsched=js.jobscheduler(timeout=1, queue_config='qfile')
jobsched.start()
