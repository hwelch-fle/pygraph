// ---------------- NETWORK START ----------------------
const data = create_network();
data.network.has_hidden_nodes = false;


function create_network() {

    vis.Network.prototype.Zoom = function (scale_factor, duration) {
        const animationOptions = {
            scale: this.getScale() * scale_factor,
            animation: { duration: duration }
        };
        this.view.moveTo(animationOptions);
    };

    // create an array with nodes
    const ds_nodes = new vis.DataSet({{ data["nodes"]| tojson }});

// create an array with edges
const ds_edges = new vis.DataSet({{ data["edges"]| tojson }});

// create a network
const container = document.getElementById('visjsnet');

// provide the data in the vis format
const data = {
    nodes: ds_nodes,
    edges: ds_edges
};
const options = {{ data["options"]| tojson }};
const pyvisjs = {{ pyvisjs| tojson }};

return {
    network: new vis.Network(container, data, options),
    nodes: ds_nodes.get({ returnType: "Object" }),
    edges: ds_edges.get({ returnType: "Object" }),
    ds_nodes: ds_nodes, // this is needed to make changes to the nodes model through ds_nodes.update()
    pyvisjs: pyvisjs,
}
}

function hide_not_selected_nodes(event) {
    // has selected nodes or already has hidden nodes - in both cases we have work to do
    if (event.nodes.length > 0 || data.network.has_hidden_nodes === true) {
        let selectedNodes;

        // user clicked outside the nodes network - we want to unhide all the nodes
        if (event.nodes.length == 0 && data.network.has_hidden_nodes === true) {
            selectedNodes = Object.keys(data.nodes);
            data.network.has_hidden_nodes = false;
        }
        else {
            const selectedNode = event.nodes[0];
            selectedNodes = data.network.getConnectedNodes(selectedNode);
            selectedNodes.push(selectedNode);
            data.network.has_hidden_nodes = true;
        }

        changed_nodes = toggle_nodes(selectedNodes);

        //reset_all_filters(data.pyvisjs.edge_filtering_fields)
        data.ds_nodes.update(changed_nodes)
    }
}

function toggle_nodes(selectedNodes) {
    const changed_nodes = [];

    for (const key in data.nodes) {
        const node = data.nodes[key];
        const node_id = node["id"];
        // node is not hidden by default
        if (node.hasOwnProperty("_hidden") === false) node._hidden = false;

        // nodes to hide
        if (selectedNodes.includes(node_id) === false) {
            // not already hidden
            if (node._hidden === false) {
                node._hidden = true;
                if (data.pyvisjs.enable_highlighting === false) node.hidden = true;
                node._color = node.color;
                node.color = "rgba(200,200,200,0.5)";
                changed_nodes.push(node)
            }
        }
        // nodes to unhide (only if already hidden)
        else if (node._hidden === true) {
            node._hidden = false;
            if (data.pyvisjs.enable_highlighting === false) node.hidden = false;
            node.color = node._color ? node._color : "#97C2FC";
            node._color = undefined;
            changed_nodes.push(node)
        }
    }

    return changed_nodes
}
// ---------------- NETWORK END ----------------------