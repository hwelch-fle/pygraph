"""A Builder for creating graphs of GitHub issues"""

from collections.abc import Iterator
from typing import Any, Unpack

from pygraph import Edge, Network, Node
from pygraph.utils import deep_update
from pygraph.vis.network import NetworkOptions
from .base import BuilderProto
from .styles import GitHubIssueStyle, GitHubIssueBuilderOpts


# Overview:
# 1) Pull issues from GH API 
#   https://api.github.com/repos/{user}/{repo}/issues/{issue}
# 2) Traverse all issues checking each timeline for `cross-referenced` events
#   https://api.github.com/repos/{user}/{repo}/issues/{issue}/timeline 
# 3) Get all `blocking` and `blocked-by` relations
# 4) Add each issue to the graph as a node with id=issue-number
# 5) If an issue is cross referenced outside the repo, stop traversal there and 
#   add that ref as `repo:issue-num` and terminate search
# 6) Associate URLs with all nodes
# 7) Nodes are colored (Font Awesome Icons):
#    green-dot:    open issue
#    purple-check: closed issue
#    green-merge:  open PR
#    purple-merge: merged PR
#    grey-merge:   draft PR
#    red-merge:    closed PR
# 8) Edges between:
#    cross-reference: Directional from originator (transparent yellow w/ low influence)
#    blocking/blocked-by: Arrow with X at end of blocked node (red with strong influence)
#    fixes: Arrow with check at fixed end (colored based on PR color)
# 9) Filtering:
#    TBD: Probably on issue/status? Maybe label?
#    Definite: All filtered nodes need to show their immediate children/parents


class GitHubIssueBuilder(BuilderProto[GitHubIssueBuilderOpts]):
    def __init__(
            self, 
            repo_url: str, 
            *,
            style: GitHubIssueBuilderOpts = GitHubIssueStyle, 
            **options: Unpack[GitHubIssueBuilderOpts]
        ) -> None:
        self.repo_url = repo_url
        self._data: tuple[list[Node], list[Edge]] | None = None
        style = deep_update(style, options) # type: ignore
        self.__dict__.update(style)

    def _issues(self) -> Iterator[dict[str, Any]]:
        """Iterate through all issues/PRs on a repo"""
        ...

    def _issue_refs(self, issue_number: int) -> Iterator[dict[str, Any]]:
        """Iterate through an issue timeline finding cross-reference/connected events"""
        ...

    def _gather_issues(self) -> Iterator[tuple[Node, list[Edge]]]:
        """Yield issue/PR nodes and OUTGOING edges"""
        ...

    def _cross_ref_node(self, node: Node, edge: Edge) -> Node:
        """Generate an nodes for edge endpoints that are outside the repo (cross-ref)"""
        ...

    @property
    def data(self) -> tuple[list[Node], list[Edge]]:
        if self._data:
            return self._data
        
        nodes = list[Node]()
        edges = list[Edge]()
        for node, edges in self._gather_issues():
            nodes.append(node)
            edges.extend(edges)
        self._data = (nodes, edges)
        return self._data
    
    @property
    def nodes(self) -> list[Node]:
        return self.data[0]
    
    @property
    def edges(self) -> list[Edge]:
        return self.data[1]
    
    def network(self, **options: Unpack[NetworkOptions]) -> Network:
        nx = Network(**options)
        nx.add_nodes_from(self.nodes)
        for edge in self.edges:
            t,f = edge['to'], edge['from']
            if t not in nx:
                nx.add_node(self._cross_ref_node(t, edge))
            if f not in nx:
                nx.add_node(self._cross_ref_node(f, edge))
        nx.add_edges_from(self.edges)
        return nx
