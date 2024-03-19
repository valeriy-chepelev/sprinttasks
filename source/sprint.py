from yandex_tracker_client import TrackerClient
import configparser
import argparse


def read_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    assert 'token' in config['DEFAULT']
    assert 'org' in config['DEFAULT']
    return config['DEFAULT']


def dupe_sprint(client, sprint_name):
    request = f'Sprint: "{sprint_name}" "Sort by":Project ASC'
    issues = client.issues.find(query=request)
    print(f'{sprint_name}')

    for issue in issues:
        print(issue.key, issue.project.name if issue.project is not None else '-')


def main():
    cfg = read_config('sprint.ini')
    client = TrackerClient(cfg['token'], cfg['org'])
    if client.myself is None:
        raise Exception('Unable to connect Yandex Tracker.')
    parser = argparse.ArgumentParser(description='Sprint task dumper by VCh.')
    parser.add_argument('sprint',
                        help='sprint name')
    args = parser.parse_args()
    dupe_sprint(client, args.sprint)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('Execution error:', e)
        input('Press any key to close...')