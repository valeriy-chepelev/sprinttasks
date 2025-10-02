import time

from yandex_tracker_client import TrackerClient
import configparser
import argparse
from alive_progress import alive_bar


def read_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    assert 'token' in config['DEFAULT']
    assert 'org' in config['DEFAULT']
    return config['DEFAULT']


def get_issues(client, queue: str, tag: str, persons: list) -> list:
    request = f'Queue: "{queue}" AND Tags:!"{tag}" "Sort by":Key ASC'
    issues = client.issues.find(query=request)
    if len(persons) > 0:
        with alive_bar(len(issues), title='Filter', theme='classic') as bar:
            res = [issue for issue in issues if bar() != 'foo'
                   and issue.assignee is not None
                   and next((p for p in persons if p.lower() in issue.assignee.display.lower()), False)]
        return res
    else:
        return issues


def tag_issues(issues, tag):
    with alive_bar(len(issues), title='Tagging', theme='classic') as bar:
        for issue in issues:
            issue.update(tags={'add': tag})
            time.sleep(1)
            bar()


def main():
    # CLI parser
    parser = argparse.ArgumentParser(description='Task tagger by VCh.')
    parser.add_argument('queue', help='queue name')
    parser.add_argument('tag', help='tag value')
    parser.add_argument('assignee', nargs='*', default=[],
                        help='assignees')
    args = parser.parse_args()

    # connection
    cfg = read_config('sprint.ini')
    client = TrackerClient(cfg['token'], cfg['org'])
    if client.myself is None:
        raise Exception('Unable to connect Yandex Tracker.')
    print('Connected to Yandex Tracker.')

    # tagging
    issues = get_issues(client, args.queue, args.tag, args.assignee)
    print(f'{len(issues)} issue(s) in {args.queue} to be tagged with "{args.tag}".')
    if len(args.assignee) > 0:
        persons = {p.assignee.display for p in issues}
        print(f'Assignees found: {", ".join(persons)}.')
    confirm = input('Enter Y to proceed:')
    assert confirm == 'Y'
    tag_issues(issues, args.tag)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('Execution error:', e)
