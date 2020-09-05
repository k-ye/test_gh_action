import urllib.request as ur
import logging
import json

# API_PREFIX = 'https://api.github.com/repos/taichi-dev/taichi'
API_PREFIX = 'https://api.github.com/repos/k-ye/test_gh_action'

def make_api_url(p):
  return f'{API_PREFIX}/{p}'

def send_request(url):
  logging.debug(f'request={url}')
  return ur.urlopen(url)


def prettify_json(j):
  return json.dumps(j, indent=2, sort_keys=True)
