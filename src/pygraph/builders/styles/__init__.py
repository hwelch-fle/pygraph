"""Default configs for different builders"""

from types import MappingProxyType

from .gitrepo import GitRepoStyle
from .github_issue import GitHubIssueStyle
from .models import DirectoryBuilderOpts
from .models import GitHubIssueBuilderOpts

GitRepoStyle: DirectoryBuilderOpts = MappingProxyType(GitRepoStyle)  # type: ignore
GitHubIssueStyle: GitHubIssueBuilderOpts = MappingProxyType(GitHubIssueStyle)  # type: ignore
