import argparse
import json
import logging
import time
import urllib.request as ur
import os

API_PREFIX = 'https://api.github.com/repos/k-ye/test_gh_action'


def make_api_url(p):
    return f'{API_PREFIX}/{p}'


def send_request(url, token=None):
    logging.debug(f'request={url}')
    hdrs = {}
    # https://docs.github.com/en/actions/configuring-and-managing-workflows/authenticating-with-the-github_token
    if token:
        hdrs = {'Authorization': f'Bearer {token}'}
    # https://stackoverflow.com/a/47029281/12003165
    req = ur.Request(url, headers=hdrs)
    return ur.urlopen(req)


def print_response(res):
    hdrs = res.getheaders()
    for p in hdrs:
        logging.info(f'  * {p}')
    logging.info('------------------')


def get_cmd_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pr', help='PR number')
    parser.add_argument('--token', help='OAuth token')
    return parser.parse_args()


def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                        level=logging.DEBUG,
                        datefmt='%Y-%m-%d %H:%M:%S')
    args = get_cmd_args()

    url = make_api_url(f'pulls/{args.pr}/commits')
    logging.debug(f'url={url}')

    logging.info('Unauthorized:')
    for i in range(3):
        logging.info(f'Run {i}')
        res = send_request(url)
        print_response(res)
        time.sleep(1)

    logging.info('')
    logging.info('Authorized:')
    for i in range(3):
        logging.info(f'Run {i}')
        res = send_request(url, args.token)
        print_response(res)
        time.sleep(1)


if __name__ == '__main__':
    main()
