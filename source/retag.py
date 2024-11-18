from yandex_tracker_client import TrackerClient
import configparser


def read_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    assert 'token' in config['DEFAULT']
    assert 'org' in config['DEFAULT']
    return config['DEFAULT']


def tag_issues(client, queue, tag, assignee=''):
    a = '' if assignee == '' else ''  # TODO: list to csv, and AND
    request = f'Queue: "{queue}" AND Tags:!"{tag}" {a} "Sort by":Key ASC'
    issues = client.issues.find(query=request)
    print(f'{len(issues)} issue(s) to be tagged with "{tag}".')


def main():
    cfg = read_config('sprint.ini')
    client = TrackerClient(cfg['token'], cfg['org'])
    if client.myself is None:
        raise Exception('Unable to connect Yandex Tracker.')
    print('Connected to Yandex Tracker.')
    tag_issues(client, 'MTFW', 'fw')
    tag_issues(client, 'MTHW', 'hw')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('Execution error:', e)
        input('Press any key to close...')