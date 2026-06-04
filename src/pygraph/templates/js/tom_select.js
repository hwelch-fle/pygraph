// ---------------- TOM-SELECT START ----------------------
new TomSelect('#select-nodes',{
	maxItems: null,
    plugins: [
		'clear_button':{'title':'Remove all selected options'},
        'input_autogrow'
    ],
	maxOptions: 100,
	valueField: 'id',
	labelField: 'title',
	searchField: 'title',
	sortField: 'title',
	options: network.body.nodes,
	create: false
});

new TomSelect('#select-edges',{
	maxItems: null,
    plugins: [
		'clear_button':{'title':'Remove all selected options'},
        'input_autogrow'
    ],
	maxOptions: 100,
	valueField: 'id',
	labelField: 'title',
	searchField: 'title',
	sortField: 'title',
	options: network.body.edges,
	create: false
});