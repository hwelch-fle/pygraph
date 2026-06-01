const network = new vis.Network(
    document.getElementById('pygraph'),
    {
        nodes: new vis.DataSet({{ data["nodes"] | tojson }}), 
        edges: new vis.DataSet({{ data["edges"] | tojson }}),
    }, 
    {{ data["options"] | tojson }}
);

{% for handler in pygraph.get('handlers', []) %}
network.{{ handler }}
{% endfor %}