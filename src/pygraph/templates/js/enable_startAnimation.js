// ---------------- START ANIMATION START ----------------------
{% with startAnimation = jinja.get("startAnimation", None) %}
{% if "zoom_factor" in startAnimation and "duration_ms" in startAnimation %}
data.network.once("afterDrawing",
    function (ctx) {
        data.network.Zoom({{ startAnimation["zoom_factor"] }}, {{ startAnimation["duration_ms"] }})
    }
);
{% endif %}
{% endwith %}
// ---------------- START ANIMATION END ----------------------