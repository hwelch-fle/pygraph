{#
    Required: 
        {
            'sankey': {
                'node': {
                    'label':[string, ...], 
                    'color': [string, ...],
                }, 
                'link': {
                    'from_node': [id, ...], 
                    'to_node': [id, ...], 
                    'value': [number, ...], 
                    'label': [str, ...],
                }
            }
        }
#}
// ---------------- SANKEY START ----------------------
init_sankey({{ jinja.get("sankey", {}) | tojson }})

function init_sankey(fig) {

    var data = {
        type: "sankey",
        domain: { x: [0, 1], y: [0, 1] },
        orientation: "h",
        valueformat: ".0f",
        valuesuffix: "TWh",
        node: {
            pad: 15,
            thickness: 15,
            line: { color: "black", width: 0.5 },
            label: fig.node.label,
            //color: fig.node.color
        },

        link: {
            source: fig.link.from_node_idx,
            target: fig.link.to_node_idx,
            value: fig.link.value,
            //label: fig.link.label
        }
    }

    var data = [data]

    var layout = {
        title: "Sankey chart",
        width: 1118,
        height: 772,
        font: { size: 10 }
    }
    Plotly.newPlot('sankeyDiv', data, layout)
};
// ---------------- SANKEY END ----------------------