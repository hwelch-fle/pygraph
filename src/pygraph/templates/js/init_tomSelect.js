// ---------------- TOM-SELECT START ----------------------
const eventHandler = function (name) {
    return function () {
        const list_of_selected_values = arguments[0]
        dict = convert_field_value_list_to_dict(list_of_selected_values)
        hide_nodes_by_edge_attribute_values_intersect(dict)

        if (data.pygraph.dropdown_auto_close === true) tom_select.close();
    };
};

tom_select = new TomSelect("#select-all-fields", {
    maxItems: 10,
    maxOptions: null,
    onChange: eventHandler("onChange"),
    //create: true,
    //onItemAdd:function(){
    //    this.setTextboxValue('');
    //    this.refreshOptions();
    //},
    plugins: ['remove_button'],
});

function convert_field_value_list_to_dict(list) {
    // converts ["edge,country,LV","edge,country,GB"]
    // to
    // {country: {list: ["LV", "GB"], type="edge"}}
    dict = {}
    for (id in list) {
        const field_value_triplet = list[id].split(",")
        const type = field_value_triplet[0]
        const field = field_value_triplet[1]
        const value = field_value_triplet[2]

        if (field in dict) dict[field]["list"].push(value)
        else dict[field] = { "list": [value], "type": type }
    }
    return dict
}

function hide_nodes_by_edge_attribute_values_intersect(option_groups_dict) {

    const selected_nodes_by_field = {}

    for (field in option_groups_dict) {
        const dict = option_groups_dict[field]
        const selected_values = dict["list"]
        const node_or_edge = dict["type"]
        selected_nodes_by_field[field] = []

        for (id in selected_values) {
            let collected_nodes = []
            const value = selected_values[id];

            if (node_or_edge === "ALL" && value === "ALL") {
                collected_nodes = Object.keys(data.nodes);
                data.network.has_hidden_nodes = false;
            }
            else if (node_or_edge === "edge") {
                collected_nodes = get_nodes_by_edge_attribute_value(field, value)
                data.network.has_hidden_nodes = true;
            }
            else if (node_or_edge === "node") {
                collected_nodes = get_nodes_by_attribute_value(field, value);
                data.network.has_hidden_nodes = true;
            }

            for (id in collected_nodes) {
                node_id = collected_nodes[id]
                if (selected_nodes_by_field[field].includes(node_id) === false) selected_nodes_by_field[field].push(node_id)
            }
        }
    }

    const selected_nodes_intersection = apply_intersect(selected_nodes_by_field);
    changed_nodes = toggle_nodes(selected_nodes_intersection);

    data.ds_nodes.update(changed_nodes)
}

function hide_nodes_by_edge_attribute_values_union(option_groups_dict) {

    const selectedNodes = [];

    for (field in option_groups_dict) {
        const dict = option_groups_dict[field]
        const selected_values = dict["list"]
        const node_or_edge = dict["type"]

        for (id in selected_values) {
            let collected_nodes = []
            const value = selected_values[id];

            if (node_or_edge === "ALL" && value === "ALL") {
                collected_nodes = Object.keys(data.nodes);
                data.network.has_hidden_nodes = false;
            }
            else if (node_or_edge === "edge") {
                collected_nodes = get_nodes_by_edge_attribute_value(field, value)
                data.network.has_hidden_nodes = true;
            }
            else if (node_or_edge === "node") {
                collected_nodes = get_nodes_by_attribute_value(field, value);
                data.network.has_hidden_nodes = true;
            }

            for (id in collected_nodes) {
                node_value = collected_nodes[id]
                if (selectedNodes.includes(node_value) === false) selectedNodes.push(node_value)
            }
        }
    }

    changed_nodes = toggle_nodes(selectedNodes);

    data.ds_nodes.update(changed_nodes)
}

function get_nodes_by_edge_attribute_value(field, value) {

    const result = [];

    for (const key in data.edges) {
        const edge = data.edges[key];

        if (edge[field] == value) {
            if (result.includes(edge.from) === false) result.push(edge.from);
            if (result.includes(edge.to) === false) result.push(edge.to);
        }
    }

    return result;
}

function get_nodes_by_attribute_value(field, value) {
    const collected_nodes = [];

    for (const key in data.nodes) {
        const node = data.nodes[key];

        if (node[field] == value) {
            collected_nodes.push(node["id"]);
        }
    }

    return collected_nodes;
}

function apply_intersect(nodes_by_field_dict) {
    let field_with_shortest_list = null
    let min_list_len = 100000;

    //if nodes_by_field_dict is empty dict - return empty list
    if (nodes_by_field_dict === null || Object.keys(nodes_by_field_dict).length === 0) {
        return [];
    }

    //if nodes_by_field_dict contains only one field - just return values
    if (nodes_by_field_dict.length === 1) {
        return nodes_by_field_dict[0];
    }

    // find shortest list
    for (field_name in nodes_by_field_dict) {
        const curr_list_len = nodes_by_field_dict[field_name].length
        if (curr_list_len < min_list_len) {
            field_with_shortest_list = field_name
            min_list_len = curr_list_len
        }
    }

    // we start from the list of all node ids from the shortest list
    // our goal is to reduce it by compariong with other lists
    let intersection = nodes_by_field_dict[field_with_shortest_list]

    // pairwise comparison
    for (field_name in nodes_by_field_dict) {
        if (field_name !== field_with_shortest_list) {
            const nodes_list = nodes_by_field_dict[field_name];
            intersection = intersection.filter((node_id) => nodes_list.includes(node_id))
        }
    }

    return intersection;
}
// ---------------- TOM-SELECT END ----------------------
