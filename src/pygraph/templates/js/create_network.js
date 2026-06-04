const data = {
    nodes: new vis.DataSet({{ data["nodes"] | tojson }}), 
    edges: new vis.DataSet({{ data["edges"] | tojson }}),
};

const nodePipe = vis.createNewDataPipeFrom(data.nodes)
const edgePipe = vis.createNewDataPipeFrom(data.edges)

new TomSelect('#select-nodes',{
    maxItems: null,
    plugins: [
        'clear_button':{'title':'Remove all selected options'},
        'input_autogrow',
        'optgroup_columns',
    ],
    maxOptions: 100,
    valueField: 'id',
    labelField: 'title',
    searchField: 'title',
    sortField: 'title',
    options: data.nodes.concat(data.edges),
    optgroups
    create: false
});


const network = new vis.Network(
    document.getElementById('pygraph'),
    data,
    {{ data["options"] | tojson }}
);

{% for handler in pygraph["handlers"] | default ([]) %}
network.{{ handler }}
{% endfor %}