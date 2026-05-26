// not used anywhere
function find_heighbors_by_node_id(id) {
    for (const key in data.nodes) {
        const node = data.nodes[key];

        if (node["id"] === id) {
            const selected_node = node["id"];
            collected_nodes = data.network.getConnectedNodes(selected_node);
            collected_nodes.push(selected_node);
            return collected_nodes
        }
    }

    return null;
}
