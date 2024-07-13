// jQuery call
$.getJSON("http://127.0.0.1:5000/api/tlapi").done(function(data){
    
//turn 'index' col into 'id'
    var container = document.getElementById('p1-timeline');
    for (let i = 0; i < data.length; i++){
        data[i].id = data[i].index;
        delete data[i].index
    };
//turn str 'null' into null value
    for (let i = 0; i < data.length; i++){
        if (data[i].end=="null") data[i].end=null;
    };

    
    
    //debug
    //console.log(data);

    /*var dataset= {
        start: data.start,
        end: data.end,
        content: data.content,
        style: data.style
    };*/

    //console.log(dataset)

    // Create a DataSet (allows two way data-binding)
    // Timeline item list   
    
    var items = new vis.DataSet(data);
    //items.add([data])
    //console.log(items)

    var groups = [
        {
            id: 'condition occurrence',
            groupName: 'condition occurrence',
            content: 'Condition Occurrences',
            style: 'background-color: #f1aeb5;',
        }, {
            id: 'drug exposure',
            groupName: 'drug exposure',
            content: 'Drug Exposures',
            style: 'background-color: #a3cfbb;',
        }, {
            id: 'measurement',
            groupName: 'measurement',
            content: 'Measurements',
            style: 'background-color: #9ec5fe;',
        }, {
            id: 'procedure',
            groupName: 'procedure',
            content: 'Procedures',
            style: 'background-color: #c5b3e6;',
        }

    ]
    
    // Configuration for the Timeline
    var options = {
        //width: '1625px',
        //height: '540px',
        min: '2008-01-01',
        max: '2010-12-12',
        showCurrentTime: false,
        horizontalScroll: true,
        zoomable: false,
        zoomMax: 5000000000,
        zoomMin: 100000,
        moveable: true,
        timeAxis: {scale: 'day', step: 1},
        minHeight: '100%',
        maxHeight: '100%'
    };

    // Create a Timeline
    // DOM element where the Timeline will be attached
    var timeline = new vis.Timeline(container, items, options, groups);
});








