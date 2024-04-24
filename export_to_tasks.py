import copy
from pathlib import Path
import json
import click
from datetime import datetime

EXPORTS = Path('exports').glob('*.json')

class Lists:
    def __init__(self, lists) -> None:
        self._lists = lists
        self._by_id = {row['id']: row for row in lists}
        self._by_name = {row['name']: row for row in lists}
        self._inbox = self._by_name['Inbox']
    
    def get_by_id(self, id):
        return self._by_id.get(id)

    @property
    def inbox(self):
        return self._inbox

    @property
    def inbox_id(self):
        return self._inbox['id']
    
    def names(self):
        return [l['name'] for l in self._lists]
    
def to_tag(list_name):
    return list_name.lower().replace(' ', '-')


def convert_list_to_tag(lists: Lists) -> list:
    new_tags = []
    ts = int(datetime.now().timestamp() * 1000)
    for name in lists.names():
        new_tags.append({
            "id": to_tag(name),
            "date_created": ts,
            "date_modified": ts
        })

    return new_tags

def convert_task_to_tag(tasks, lists: Lists) -> list:
    tagged_tasks = []
    for task in tasks:
        if 'date_completed' in task:
            continue

        tagged = copy.deepcopy(task)
        list = lists.get_by_id(tagged['list_id'])
        tagged['tags'] = [to_tag(list['name'])]
        tagged['list_id'] = lists.inbox_id

        tagged_tasks.append(tagged)

    return tagged_tasks
        

@click.command()
@click.argument('export', type=click.File('rb'))
def cli(export):
    rtm_export = json.loads(export.read())
    rtm_import = copy.deepcopy(rtm_export)

    lists = Lists(rtm_export['lists'])
    rtm_import['tags'] = convert_list_to_tag(lists)
    rtm_import['tasks'] = convert_task_to_tag(rtm_export['tasks'], lists)

    path = f'imports/{datetime.now().isoformat()}.json'
    Path(path).write_text(json.dumps(rtm_import, indent=2))


if __name__ == '__main__':
    cli()
