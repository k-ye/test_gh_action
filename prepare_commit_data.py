# Current commit title
# Run ID of previous commit

import argparse
import json
import logging
from collections import namedtuple
import time

from shared import make_api_url, send_request

SHA = 'sha'


def get_commits(pr):
    url = make_api_url(f'pulls/{pr}/commits')
    f = send_request(url)
    return json.loads(f.read())


def locate_previous_commit_sha(commits, head_sha):
    assert commits[-1][SHA] == head_sha
    if len(commits) < 2:
        return None
    return commits[-2][SHA]


def get_commit_message(commits, sha):
    for c in reversed(commits):
        if c[SHA] == sha:
            return c['commit']['message']
    return ''


def get_workflow_runs(page_id):
    url = make_api_url(f'actions/runs?page={page_id}')
    f = send_request(url)
    return json.loads(f.read())


def locate_workflow_run_id(sha):
    done = False
    page_id = 0
    while not done:
        runs = get_workflow_runs(page_id)['workflow_runs']
        for r in runs:
            if r['head_sha'] == sha:
                return r['id']
        page_id += 1
    return ''


def get_cmd_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pr', help='PR number')
    parser.add_argument('--sha', help='Head commit SHA in the PR')
    parser.add_argument('--out', help='Path to the output name')
    return parser.parse_args()


OutputData = namedtuple('OutputData',
                        ['num_commits', 'head_commit_msg', 'prev_run_id'],
                        defaults=(0, '', ''))


def gen_output(args):
    pr = args.pr
    commits = get_commits(pr)
    num_commits = len(commits)
    logging.info(f'\nPR={pr} #commits={num_commits}')

    head_sha = args.sha
    commit_msg = get_commit_message(commits, head_sha)
    logging.info(f'HEAD commit: SHA={head_sha} message={commit_msg}')

    prev_sha = locate_previous_commit_sha(commits, head_sha)
    logging.info(f'SHA: head={head_sha} prev={prev_sha}')
    if prev_sha is None:
        # First commit in the PR
        return OutputData(num_commits, commit_msg, '')

    run_id = locate_workflow_run_id(prev_sha)
    logging.info(f'Prev commit: SHA={prev_sha} workflow_run_id={run_id}')
    return OutputData(num_commits, commit_msg, run_id)


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
