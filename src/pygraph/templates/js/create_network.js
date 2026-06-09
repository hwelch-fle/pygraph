const data = {
    nodes:  new vis.DataSet({{ network.nodes|tojson() }}),
    edges: new vis.DataSet({{ network.edges|tojson() }}),
}
const options = {{ network.options|tojson(indent=2) }}
const network = new vis.Network(document.getElementById('pygraph'), data, options);