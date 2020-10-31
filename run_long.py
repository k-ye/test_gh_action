import logging
import time

for i in range(32):
  print(f'running {i}')
  logging.info(f'running {i}')
  time.sleep(10)