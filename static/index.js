
function drawHistogram() {
    $.getJSON( "/hist", function( data ) {
        data.forEach(function(item, index) {
            data[index].date = Date.parse(item.date)
        })
        console.log(data)
        var chart = d3_timeseries()
                      .addSerie(data,{x:'date',y:'avg',diff:'max'},{interpolate:'monotone',color:"#333"})

        chart('#chart')
    });
}

$( document ).ready(function() {
    drawHistogram()
});