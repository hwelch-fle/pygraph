network.on("doubleClick", (event) => {
  openLink(resolveLink(event))
  {% if selectors %}
  || clearFilters();
  {% endif %}
});

var clickStack = [];
network.on("click", async (event) => {
  const clickedAt = new Date().valueOf();
  clickStack.push(clickedAt);
  await new Promise((r) => setTimeout(r, 200));
  if (clickStack.pop() == clickedAt) {
    {% if selectors %}
    updateSelection(event);
    {% endif %}
  }
});
