import argparse
from shared import make_api_url, send_request
import json
import logging
import time

def get_status_of_run(run_id):
  url = make_api_url(f'actions/runs/{run_id}')
  start = time.time()
  retries = 0
  WAIT_DURATION_SECS = 15
  MAX_TIMEOUT = 30 * 60 # 30 minutes
  while True:
    f = send_request(url)
    j = json.loads(f.read())
    # https://developer.github.com/v3/checks/runs/#create-a-check-run
    if j['status'] == 'completed':
      return j['conclusion'] == 'success'
    
    if time.time() - start > MAX_TIMEOUT:
      return False
    retries += 1
    logging.info(f'Waiting to get the status of run={run_id} (url={url}). retries={retries}')
    time.sleep(WAIT_DURATION_SECS)
  return False


def get_cmd_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('--run', help='Workflow run ID')
  return parser.parse_args()

def main():
  logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

  args = get_cmd_args()

  run_id = args.run_id
  if not run_id:
    return 0
  
  run_ok = get_status_of_run(run_id)
  logging.info(f'workflow_run_id={run_id} ok={run_ok}')
  return 0 if run_ok else 1

if __name__ == '__main__':
  main()
