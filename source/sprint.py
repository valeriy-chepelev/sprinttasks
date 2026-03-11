from yandex_tracker_client import TrackerClient
import configparser
import argparse
from prettytable import PrettyTable, TableStyle
import pyperclip

import requests


def projects(token, org):
    """Return list of project names, up to 1000 projects
    token, org is OAuth credentials"""
    session = requests.Session()
    headers = {"Host": "api.tracker.yandex.net",
               "Authorization": f"OAuth {token}"}
    if len(org) < 15:
        headers.update({"X-Org-ID": org})
    else:
        headers.update({"X-Cloud-Org-ID": org})
    request = 'https://api.tracker.yandex.net/v2/entities/project/_search'

    params = {'fields': 'summary,entityRank', 'perPage': '1000'}
    response = session.post(url=request, headers=headers, params=params, data={})
    response.raise_for_status()
    data = response.json()

    return {project['fields']['summary']: project['fields']['entityRank'] for project in data['values']}


def read_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    assert 'token' in config['DEFAULT']
    assert 'org' in config['DEFAULT']
    return config['DEFAULT']


def dupe_sprint(client, sprint_name, ranks):
    request = f'Sprint: "{sprint_name}" "Sort by":Project ASC'
    issues = client.issues.find(query=request)
    print(sprint_name)
    table = PrettyTable()
    table.field_names = ['Project', 'Rank', 'Issue', 'Summary', 'Assignee', 'Report']
    rows = []
    for issue in issues:
        pname = issue.project.name if issue.project is not None else '-'
        prank = 0 if pname not in ranks or ranks[pname] is None else ranks[pname]
        rows.append([pname, prank,
                     issue.key, issue.summary, issue.assignee.display,
                     ''])
    table.add_rows(rows)
    table.align = 'l'
    table.sortby = 'Rank'
    table.reversesort = True
    table.set_style(TableStyle.MARKDOWN)
    pyperclip.copy(f'# {sprint_name}\n' + table.get_formatted_string(
        fields=['Project', 'Issue', 'Summary', 'Assignee', 'Report']))
    table.set_style(TableStyle.DEFAULT)
    print(table)


def main():
    creds = read_config('sprint.ini')
    if len(creds['org']) < 15:  # Yes, a magic number! cloud_org_id usually have length 20
        client = TrackerClient(token=creds['token'], org_id=creds['org'])
    else:
        client = TrackerClient(token=creds['token'], cloud_org_id=creds['org'])
    if client.myself is None:
        raise Exception('Unable to connect Yandex Tracker.')
    parser = argparse.ArgumentParser(description='Sprint task dumper by VCh.')
    parser.add_argument('sprint',
                        help='sprint name')
    args = parser.parse_args()

    ranks = projects(creds['token'], creds['org'])

    dupe_sprint(client, args.sprint, ranks)
    print('Markdown copied to system clipboard.')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('Execution error:', e)
        input('Press any key to close...')
