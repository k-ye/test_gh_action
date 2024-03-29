import argparse
import json
import logging
import time
import urllib.request as ur
import sys


# API_PREFIX = 'https://api.github.com/repos/taichi-dev/taichi'
API_PREFIX = 'https://api.github.com/repos/k-ye/test_gh_action'
SHA = 'sha'

def make_api_url(p):
  return f'{API_PREFIX}/{p}'

def send_request(url):
  logging.debug(f'request={url}')
  return ur.urlopen(url)


def prettify_json(j):
  return json.dumps(j, indent=2, sort_keys=True)


def get_commits(pr):
    url = make_api_url(f'pulls/{pr}/commits')
    f = send_request(url)
    return json.loads(f.read())


def locate_previous_commit_sha(commits, head_sha):
    assert commits[-1][SHA] == head_sha
    if len(commits) < 2:
        return None
    return commits[-2][SHA]


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

def get_status_of_run(run_id):
    url = make_api_url(f'actions/runs/{run_id}')
    start = time.time()
    retries = 0
    MAX_TIMEOUT = 60 * 60  # 1 hour
    while True:
        f = send_request(url)
        j = json.loads(f.read())
        # https://developer.github.com/v3/checks/runs/#create-a-check-run
        if j['status'] == 'completed':
            return j['conclusion'] == 'success'

        if time.time() - start > MAX_TIMEOUT:
            return False
        retries += 1
        logging.info(
            f'Waiting to get the status of run={run_id} (url={url}). retries={retries}'
        )
        time.sleep(15)
    return False


def get_cmd_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pr', help='PR number')
    parser.add_argument('--sha', help='Head commit SHA in the PR')
    return parser.parse_args()


def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                        level=logging.DEBUG,
                        datefmt='%Y-%m-%d %H:%M:%S')

    args = get_cmd_args()

    pr = args.pr
    commits = get_commits(pr)
    num_commits = len(commits)
    logging.info(f'\nPR={pr} #commits={num_commits}')

    head_sha = args.sha
    prev_sha = locate_previous_commit_sha(commits, head_sha)
    logging.info(f'SHA: head={head_sha} prev={prev_sha}')
    if prev_sha is None:
        # First commit in the PR
        return 0

    run_id = locate_workflow_run_id(prev_sha)
    if not run_id:
        logging.warning(f'Could not find the workflow run for SHA={prev_sha}')
        return 0

    logging.info(f'Prev commit: SHA={prev_sha} workflow_run_id={run_id}')
    run_ok = get_status_of_run(run_id)
    logging.info(f'workflow_run_id={run_id} ok={run_ok}')
    return 0 if run_ok else 1


if __name__ == '__main__':
    sys.exit(main())
