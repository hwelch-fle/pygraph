{# Schema
    selectors.node: 
        enabled: bool (default: True)
        placeholder_text: str (default: 'Filter Nodes')
        max_items: int | None (default: None)
        max_options: int | None (default: 100)
        value_field: str (default: "id")
        label_field: str (default: '"label"')
        search_field: str (default: '"label"')
        sort_field: str (default: '"label"')
        unique: bool (default: False)
        reset_on_clear: bool (default: True)
    selectors.edge: 
        enabled: bool (default: True)
        placeholder_text: str (default: 'Filter Edges')
        max_items: int | None (default: None)
        max_options: int | None (default: 100)
        value_field: str (default: '"label"')
        label_field: str (default: '"label"')
        search_field: str (default: '"label"')
        sort_field: str (default: '"label"')
        unique: bool (default: False)
        reset_on_clear: bool (default: True)
#}

{% set node = selectors.node or {} %}
{% set edge = selectors.edge or {} %}

{% if node.enabled|default(True) %}
let changeNodes = (selection) => {
    if (selection.length == 0) { resetNetwork(); return; }
    {% if edge.enabled|default(True) %}
    tomSelectEdges.clear()
    {% endif %}
    var { nodes, edges } = getBaseData()
    edges = edges.get({
        filter: (edge) =>
        selection.includes(edge.to) || selection.includes(edge.from),
    })
    const nodeIds = [
        ...new Set(edges.map((edge) => [edge.to, edge.from]).flat()),
    ]
    nodes = nodes.get(nodeIds)
    setNetwork(nodes, edges)
};
{% endif %}

{% if edge.enabled|default(True) %}
let changeEdges = (selection) => {
    if (selection.length == 0) { resetNetwork(); return; }
    tomSelectNodes.clear()
    var { nodes, edges } = getBaseData()
    edges = edges.get({ filter: (edge) => selection.includes(edge.{{edge.value_field|default("label")}}) })
    nodes = getNodes([...new Set(edges.map(nodesAtEdge).flat())])
    setNetwork(nodes, edges)
};
{% endif %}

const collator = new Intl.Collator(undefined, {
  numeric: true,
  sensitivity: "base",
});

{% if node.enabled|default(True) %}
const tomSelectNodes = new TomSelect("#tom-select-nodes", {
  maxItems: {{node.max_items|default("null")}},
  maxOptions: {{node.max_options|default(100)}},
  valueField: "id",
  labelField: "{{node.label_field|default('label')}}",
  searchField: "{{node.search_field|string|default('label')}}",
  sortField: "{{node.sort_field|default('label')}}",
  options: allNodes()
    {% if node.unique|default(False) %}
    .distinct("{{node.value_field|default('id')}}")
    .map((val) => ({ {{node.value_field|default('id')}}: val }))
    .sort(collator.compare),
    {% else %}
    .get(),
    {% endif %}
  create: false,
  onChange: changeNodes,
  {% if node.reset_on_clear|default("true") %}
  onClear: resetNetwork,
  {% endif %}
  plugins: {{node.plugins|default(["remove_button", "clear_button", "input_autogrow"])}},
});
{% endif %}

{% if edge.enabled|default(True) %}
const tomSelectEdges = new TomSelect("#tom-select-edges", {
  maxItems: {{edge.max_items|default("null")}},
  maxOptions: {{edge.max_options|default(100)}},
  valueField: "{{edge.value_field|default('label')}}",
  labelField: "{{edge.label_field|default('label')}}",
  searchField: "{{edge.search_field|default('label')}}",
  sortField: "{{node.sort_field|default('label')}}",
  options: allEdges()
    {% if edge.unique|default(False) %}
    .distinct("{{edge.value_field|default('label')}}")
    .map((val) => ({ {{edge.value_field|default('label')}}: val }))
    .sort(collator.compare),
    {% else %}
    .get(),
    {% endif %}
  create: false,
  onChange: changeEdges,
  {% if edge.reset_on_clear|default("true") %}
  onClear: resetNetwork,
  {% endif %}
  plugins: {{edge.plugins|default(["remove_button", "clear_button", "input_autogrow"])}},
});
{% endif %}

// Selection Transformers
let addItem = (selector, item) => item ? selector.addItem(item, false) || true : false
let addNodeSelection = (item) => {% if node.enabled|default(True) %}addItem(tomSelectNodes, item?.{{node.value_field|default("id")}}){% else %} undefined {% endif %}
let addEdgeSelection = (item) => {% if edge.enabled|default(True) %}addItem(tomSelectEdges, item?.{{node.value_field|default("label")}}){% else %} undefined {% endif %}
let updateSelection = (event) => addNodeSelection(getNodes(event.nodes[0])) || addEdgeSelection(getEdges(event.edges[0]))
let clearFilters = () => {
  {% if edge.enabled|default(True) %}tomSelectEdges.clear(false);{% endif %}
  {% if node.enabled|default(True) %}tomSelectNodes.clear(false);{% endif %}
}