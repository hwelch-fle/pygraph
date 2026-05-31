from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape

from pygraph.builders import DirectoryBuilder
from pygraph.builders.styles import GitRepoStyle
from pygraph.utils import to_html

env = Environment(loader=PackageLoader('pygraph'), autoescape=select_autoescape())
builder = DirectoryBuilder(
    Path(),
    style=GitRepoStyle,
    ignores={'files': ['.gitignore'], 'patterns': ['.venv/', '.git/']},
)
nw = builder.web_network(host='github.com', user='hwelch-fle', branch='master')
print(nw)
data = nw.to_dict()
out = Path('docs/ref/index.html')
out.parent.mkdir(parents=True, exist_ok=True)
template = env.get_template('html/basic-template.html')
out.write_text(to_html(nw, template, jinja={'background': '#1f1f1f'}))
