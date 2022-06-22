import click

from .file_handler import PymonFileHandler


@click.command()
@click.argument('filename', required=1)
@click.option('--all', '-a', help='Watch all python Files in directory',
              is_flag=True)
@click.option('--force-kill', '-f', is_flag=True,
              help='Force kills the file instead of terminating it')
def main(filename: str, all: bool, force_kill: bool):
    """Executes the provided script with python
    and restarts it when changes are detected"""
    file_handler = PymonFileHandler(filename, all, force_kill)
    file_handler.start_processing()


if __name__ == '__main__':
    main()
