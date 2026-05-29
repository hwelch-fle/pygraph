// ---------------- NETWORK START ----------------------
const data = create_network();

function create_network() {
    const container = document.getElementById('pygraph');
    const data = {
        nodes: new vis.DataSet({{ data["nodes"] | tojson }}),
        edges: new vis.DataSet({{ data["edges"] | tojson }}),
    };
    const options = {{ data["options"] | tojson }};
    const pygraph = {{ pygraph | safe | tojson }};
    const network = new vis.Network(container, data, options)

    // Event Handlers
    network.on('doubleClick', function (event) {
        const { nodes } = event;
        if (nodes.length == 0) { return; }
        const nodeId = nodes[0];
        const nodeData = network.body.data.nodes.get(nodeId);
        if ( nodeData.link ) { window.open(nodeData.link); }
    });

    return {
        network: network,
        pygraph: pygraph,
    }
}

// ---------------- NETWORK END ----------------------