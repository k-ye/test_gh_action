import argparse
import urllib.request as ur
import json
import logging

# API_PREFIX = 'https://api.github.com/repos/taichi-dev/taichi'
API_PREFIX = 'https://api.github.com/repos/k-ye/test_gh_action'

def make_api_url(p):
  return f'{API_PREFIX}/{p}'

def send_request(url):
  logging.debug(f'request={url}')
  return ur.urlopen(url)

def get_commits(pr):
  url = make_api_url(f'pulls/{pr}/commits')
  f = send_request(url)
  return json.loads(f.read())

def get_workflow_runs(page_id):
  url = make_api_url(f'actions/runs?page={page_id}')
  f = send_request(url)
  return json.loads(f.read())

def get_cmd_args():
  parser = argparse.ArgumentParser()
  parser.add_argument("--pr", help="PR number")
  return parser.parse_args()

def prettify_json(j):
  return json.dumps(j, indent=2, sort_keys=True)
  
def main():
  logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

  args = get_cmd_args()

  pr = args.pr
  commits = get_commits(pr)
  logging.info(f'\nPR={pr} #commits={len(commits)}')
  print(prettify_json(commits))
  print('-----------------------------------')

  runs = get_workflow_runs(0)
  print(prettify_json(runs))
  print('-----------------------------------')

if __name__ == '__main__':
  main()
