# Current commit title
# Run ID of previous commit

import argparse
import json
import logging
import time
import urllib.request as ur
import sys

from collections import namedtuple


API_PREFIX = 'https://api.github.com/repos/k-ye/test_gh_action'
SHA = 'sha'

def make_api_url(p):
  return f'{API_PREFIX}/{p}'

def send_request(url):
  logging.debug(f'request={url}')
  return ur.urlopen(url)


def get_commits(pr):
    url = make_api_url(f'pulls/{pr}/commits')
    f = send_request(url)
    return json.loads(f.read())

def get_commit_message(commits, sha):
    for c in reversed(commits):
        if c[SHA] == sha:
            return c['commit']['message']
    return ''


def get_cmd_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pr', help='PR number')
    parser.add_argument('--sha', help='Head commit SHA in the PR')
    parser.add_argument('--out', help='Path to the output name')
    return parser.parse_args()


OutputData = namedtuple('OutputData',
                        ['head_commit_msg'],
                        defaults=(''))


def gen_output(args):
    pr = args.pr
    commits = get_commits(pr)
    num_commits = len(commits)
    logging.info(f'\nPR={pr} #commits={num_commits}')

    head_sha = args.sha
    commit_msg = get_commit_message(commits, head_sha)
    logging.info(f'HEAD commit: SHA={head_sha} message={commit_msg}')
    return OutputData(commit_msg)


def main():
    logging.basicConfig(format='%(levelname)s:%(message)s',
                        level=logging.DEBUG)
    args = get_cmd_args()
    output = gen_output(args)
    # https://docs.github.com/en/actions/reference/workflow-commands-for-github-actions#setting-an-output-parameter
    with open(args.out, 'w') as fh:
        fh.write('#!/bin/bash\n')
        for k, v in output._asdict().items():
            fh.write(f'echo ::set-output name={k}::{v}\n')

if __name__ == '__main__':
    main()
