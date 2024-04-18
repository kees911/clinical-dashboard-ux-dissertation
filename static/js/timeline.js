//json url
const url = "http://127.0.0.1:5000/api/drugs_timeline"
$.getJSON(url, function(myData) {
    // JSON result in `myData` variable
    //console.log(myData);
    console.log(myData);
    //Should print 50 as there are 50 entries for this patient in this dataset
    console.log(Object.keys(myData).length);

    console.log(Object.keys(myData))

    console.log(Object.values(myData))

    var myArray = [];
    myArray.push(Object.values(myData));
    console.log(myArray[0].length);
 
    var str = "";
    var arr;
    var emp;

    function appt(){
    for(var i = 0; i<myArray[0].length; i++) {
        var theArray = myArray[0][i];
        var visit_id = theArray.visit_occurrence_id
        var start_date = theArray.drug_exposure_start_date
        var end_date = theArray.drug_exposure_end_date
        var drug_name = theArray.drug_source_concept_label
        //console.log(visit_id + start_date + end_date + drug_name)
        str+=("{id:" + i + ", content:'" + drug_name + "', start:'" +
        start_date + "', end:'" + end_date + "'},\n");
    }
    str=str+"{id:50, content:'today', start: '2009-06-06'}"
    return str;
}

var test = appt();
console.log(test);
console.log(typeof(test));
//Varaibles to populate the timeline content with 
/*var visit_id = myDat.visit_occurrence_id;
var start_date = myDat.drug_exposure_start_date;
var end_date = myDat.drug_exposure_end_date;
var drug_name = myDat.drug_source_concept_label;
console.log(drug_name);*/

//iterate through each entry until all entries with this patient
//have been entered (50 occurrences in original dataset)



/*function appts(){
    for (let i=0; i<Object.keys(myData).length; i++){ 
        console.log("{id: '" + jsarr[i].visit_id + "', content: '" + jsarr[i].drug_name + "', start: '" +
        jsarr[i].start_date + "', end: '" + jsarr[i].end_date + "'},");
        str+=appointments;
        
    }
};*/

// DOM element where the Timeline will be attached
var container = document.getElementById('visualization');

// Create a DataSet (allows two way data-binding)
var items = new vis.DataSet([{id:0, content:'No Info', start:'2008-07-26', end:'2008-08-25'},
{id:1, content:'No Info', start:'2008-02-11', end:'2008-03-11'},
{id:2, content:'No Info', start:'2009-12-06', end:'2010-01-04'},
{id:3, content:'No Info', start:'2008-08-14', end:'2008-09-12'},
{id:4, content:'No Info', start:'2009-09-21', end:'2009-10-20'},
{id:5, content:'Metformin hydrochloride 850 MG Oral Tablet [Glucophage]', start:'2008-04-21', end:'2008-05-20'},
{id:6, content:'No Info', start:'2009-06-02', end:'2009-07-01'},
{id:7, content:'No Info', start:'2010-06-13', end:'2010-07-12'},
{id:8, content:'No Info', start:'2009-12-10', end:'2010-01-08'},
{id:9, content:'No Info', start:'2009-06-23', end:'2009-07-22'},
{id:10, content:'No Info', start:'2009-06-29', end:'2009-08-27'},
{id:11, content:'No Info', start:'2010-02-11', end:'2010-02-20'},
{id:12, content:'No Info', start:'2009-05-11', end:'2009-06-09'},
{id:13, content:'Lisinopril 10 MG Oral Tablet', start:'2008-10-16', end:'2009-01-13'},
{id:14, content:'No Info', start:'2009-12-25', end:'2010-01-23'},
{id:15, content:'No Info', start:'2009-08-08', end:'2009-11-05'},
{id:16, content:'olanzapine 5 MG Oral Tablet [Zyprexa]', start:'2009-08-20', end:'2009-09-18'},
{id:17, content:'No Info', start:'2008-08-20', end:'2008-09-18'},
{id:18, content:'No Info', start:'2008-04-27', end:'2008-05-26'},
{id:19, content:'No Info', start:'2008-05-10', end:'2008-06-08'},
{id:20, content:'No Info', start:'2008-11-23', end:'2008-12-22'},
{id:21, content:'No Info', start:'2010-05-28', end:'2010-06-26'},
{id:22, content:'Riluzole 50 MG Oral Tablet [Rilutek]', start:'2008-10-05', end:'2008-10-24'},
{id:23, content:'No Info', start:'2009-03-04', end:'2009-04-02'},
{id:24, content:'No Info', start:'2008-01-17', end:'2008-02-15'},
{id:25, content:'No Info', start:'2009-04-30', end:'2009-05-19'},
{id:26, content:'Hydrochlorothiazide 50 MG / Methyldopa 500 MG Oral Tablet', start:'2009-09-25', end:'2009-10-24'},
{id:27, content:'No Info', start:'2008-10-03', end:'2008-10-12'},
{id:28, content:'glyburide 1.25 MG Oral Tablet', start:'2010-07-19', end:'2010-08-17'},
{id:29, content:'No Info', start:'2009-06-10', end:'2009-07-09'},
{id:30, content:'No Info', start:'2010-01-30', end:'2010-02-28'},
{id:31, content:'methimazole 5 MG Oral Tablet', start:'2008-06-14', end:'2008-07-13'},
{id:32, content:'No Info', start:'2009-04-03', end:'2009-05-02'},
{id:33, content:'No Info', start:'2008-08-07', end:'2008-09-05'},
{id:34, content:'No Info', start:'2009-09-08', end:'2009-10-07'},
{id:35, content:'No Info', start:'2009-04-28', end:'2009-07-26'},
{id:36, content:'Glipizide 10 MG Oral Tablet', start:'2009-07-12', end:'2009-08-10'},
{id:37, content:'Injection, granisetron hydrochloride, 100 mcg', start:'2008-01-04', end:'2008-02-03'},
{id:38, content:'atorvastatin 20 MG Oral Tablet [Lipitor]', start:'2008-01-15', end:'2008-02-13'},
{id:39, content:'Injection, enoxaparin sodium, 10 mg', start:'2010-02-22', end:'2010-03-24'},
{id:40, content:'No Info', start:'2009-10-31', end:'2009-11-29'},
{id:41, content:'Metformin hydrochloride 1000 MG Oral Tablet', start:'2009-02-18', end:'2009-03-19'},
{id:42, content:'No Info', start:'2009-03-12', end:'2009-03-31'},
{id:43, content:'No Info', start:'2009-02-24', end:'2009-03-25'},
{id:44, content:'No Info', start:'2009-04-23', end:'2009-05-12'},
{id:45, content:'No Info', start:'2009-01-31', end:'2009-02-19'},
{id:46, content:'No Info', start:'2008-11-11', end:'2009-02-08'},
{id:47, content:'No Info', start:'2010-03-12', end:'2010-04-10'},
{id:48, content:'No Info', start:'2009-05-14', end:'2009-06-12'},
{id:49, content:'No Info', start:'2009-02-12', end:'2009-05-12'},
{id:50, content:'today', start: '2009-07-07'}]);

// Configuration for the Timeline
var options = {
    width: '100%',
    height: '540px',
    showCurrentTime: true,
    horizontalScroll: true,
    zoomable: true,
    moveable: true,
    timeAxis: {scale: 'month', step: 1}
};

// Create a Timeline
var timeline = new vis.Timeline(container, items, options);
});