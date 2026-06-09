network.on('hoverEdge', (event) => { updateEdges(getEdges([event.edge]).map(showLabel)) });
network.on('blurEdge', (event) => { updateEdges(getEdges([event.edge]).map(hideLabel)) });
network.on('hoverNode', (event) => { updateEdges(edgesAtNode(event.node).map(showLabel)) });
network.on('blurNode', (event) => { updateEdges(edgesAtNode(event.node).map(hideLabel)) });