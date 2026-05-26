// ---------------- DRAW TITLE START ----------------------
{% if "title" in jinja -%}
data.network.on("beforeDrawing", function (ctx) {
    const central_focus = data.network.getViewPosition();
    const scale = data.network.getScale();

    div = document.getElementById("visjsnet").getElementsByClassName("vis-network")[0];
    const height = div.clientHeight;
    const width = div.clientWidth;

    const dx = width / 2 - width * 0.05;
    const dy = height / 2 - height * 0.05;
    const x = central_focus.x - dx / scale;
    const y = central_focus.y - dy / scale;
    //const font_size = Math.round(30.0 / scale)
    const font_size = 30.0 / scale;

    ctx.font = "" + font_size + "px JetBrains Mono";
    //ctx.font = "30px JetBrains Mono";
    ctx.fillStyle = "#D0D0D0";
    ctx.fillText('{{ jinja["title"] }}', x, y);
});
{% endif %}
// ---------------- DRAW TITLE END ----------------------