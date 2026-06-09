// Node Transformers
let allNodes = () => network.body.data.nodes
let getNodes = (nodeIds) => allNodes().get(nodeIds)
let updateNodes = (nodeArray) => allNodes().updateOnly(nodeArray)

// Edge Transformers
let allEdges = () => network.body.data.edges
let getEdges = (edgeIds) => allEdges().get(edgeIds)
let edgesAtNode = (nodeId) => allEdges().get(network.getConnectedEdges(nodeId))
let nodesAtEdge = (edge) => [edge.to, edge.from]
let updateEdges = (edgeArray) => allEdges().updateOnly(edgeArray)

// Network Transformers
let setNetwork = (nodes, edges) => network.setData({ nodes: new vis.DataSet(nodes), edges: new vis.DataSet(edges) })
let getBaseData = () => ({ nodes: data.nodes, edges: data.edges })
let resetNetwork = () => setNetwork(data.nodes.get(), data.edges.get())

{% if hover_edge_labels %}
// Label Transformers
let setFontSize = (val, item) => { item.font.size = val; return item }
let showLabel = (item) => setFontSize({{edge_label_font_size|default(12)}}, item)
let hideLabel = (item) => setFontSize(0, item)
{% endif %}

let openLink = (item) => (item?.{{link_field|default("link")}}) && window.open(item?.{{link_field|default("link")}}) || false
let resolveLink = (event) => getNodes(event.nodes[0]) || getEdges(event.edges[0]) || undefined
