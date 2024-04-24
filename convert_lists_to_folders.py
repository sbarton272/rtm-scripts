import click

from remember_the_milk import RTMClient, RTMMethod   
from config import API_KEY, SECRET


@click.command()
def cli():
    client = RTMClient(
        api_key=API_KEY,
        secret=SECRET,
    )
    prompt = lambda: click.prompt('Please enter the frob', type=str)
    client.authenticate(prompt)
    client.get(RTMMethod.TASKS__GET_LIST, {})

if __name__ == '__main__':
    cli()
