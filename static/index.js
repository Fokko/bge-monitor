function drawHistogram() {
    currentTemperature = 0.0
    $.getJSON("/hist", function(data) {
        hist = data.hist
        // Parse dates
        hist.forEach(function(item, index) {
            hist[index].date = Date.parse(item.date)
            currentTemperature = item.avg
        })
        // Draw chart
        var chart = d3_timeseries()
            .addSerie(hist, {
                x: 'date',
                y: 'avg',
                ci_up: 'max',
                ci_down: 'min'
            }, {
                interpolate: 'monotone',
                color: "#333"
            }).width(1000)

        chart('#chart');

        expected = data.intercept + (Date.now() / 1000) * data.slope;
        difference = expected - currentTemperature

        $("#currentTemperature").html(Math.round(currentTemperature) + "&#8451;");
        $("#currentTrend").html(Math.round(difference) + "&#8451;");

        delta = Math.round(difference / 10.0)

        glyph = ''
        if(delta > 0) {
          glyph = '&#8670;';
        }
        if(delta < 0) {
          glyph = '&#8671;';
        }

        console.log(delta)

        html = ''
        for (var i = 0, len = delta; i < len; i++) {
          html += glyph;
        }
        $("#icons").append(html);
    });
}

$(document).ready(function() {
    drawHistogram()
});