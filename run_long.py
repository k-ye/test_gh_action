import time
import logging
import sys

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                    level=logging.DEBUG,
                    datefmt='%Y-%m-%d %H:%M:%S')
argv = sys.argv
if len(argv) > 1:
  logging.info(argv)
for i in range(20):
  logging.info('running %d', i)
  time.sleep(5)