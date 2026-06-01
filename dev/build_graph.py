from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape

from pygraph.builders import DirectoryBuilder
from pygraph.builders.styles import GitRepoStyle
from pygraph.utils import to_html


def main():
    env = Environment(loader=PackageLoader('pygraph'), autoescape=select_autoescape())
    template = env.get_template('html/basic-template.html')
    builder = DirectoryBuilder(
        Path(),
        style=GitRepoStyle,
        ignores={'files': ['.gitignore'], 'patterns': ['.venv/', '.git/']},
    )
    nw = builder.web_network(host='github.com', user='hwelch-fle', branch='master')
    print(nw)
    out = Path('docs/ref/index.html')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(to_html(nw, template, jinja={'background': '#1f1f1f'}))


if __name__ == '__main__':
    main()
