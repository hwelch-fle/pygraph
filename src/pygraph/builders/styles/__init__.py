"""Default configs for different builders"""

from types import MappingProxyType

from .gitrepo import GitRepoStyle as GitRepoStyle
from .models import DirectoryBuilderOpts

GitRepoStyle: DirectoryBuilderOpts = MappingProxyType(GitRepoStyle)  # type: ignore
