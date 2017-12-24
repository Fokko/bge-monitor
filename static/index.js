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

        hourInSeconds = 60 * 60 + (Date.now() / 1000)

        expected = data.intercept + (hourInSeconds * data.slope);
        difference = expected - currentTemperature

        $("#currentTemperature").html(Math.round(currentTemperature) + "&#8451;");
        $("#currentTrend").html(Math.round(difference) + "&#8451;");

        glyph = '&#8649'
        if(difference > 0) {
          glyph = '&#8607;';
        }
        if(difference > 10) {
          glyph = '&#8648;';
        }
        if(delta < 0) {
          glyph = '&#8609;';
        }
        if(delta < 10) {
          glyph = '&#8650;';
        }
        $("#icons").append(glyph);
    });
}

$(document).ready(function() {
    drawHistogram()
});