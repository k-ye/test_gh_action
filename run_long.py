import time
import logging
import sys

argv = sys.argv
if len(argv) > 1:
  logging.info(argv)
for i in range(20):
  logging.info('running %d', i)
  time.sleep(5)