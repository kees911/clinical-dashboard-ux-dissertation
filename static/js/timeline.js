//json url
const url = "http://127.0.0.1:5000/api/drugs_timeline"
$.getJSON(url, function(myData) {
    // JSON result in `myData` variable
    //console.log(myData);
    //console.log(myData);
    //Should print 64 as there are 64 entries for this patient in this dataset
    //console.log(Object.keys(myData).length);

    //console.log(Object.keys(myData))

    //console.log(Object.values(myData))

    var myArray = [];
    myArray.push(Object.values(myData));
    //console.log(myArray[0].length);
 
    var str = "";
    var arr;
    var emp;

    function appt(){
    for(var i = 0; i<myArray[0].length; i++) {
        var theArray = myArray[0][i];
        var visit_id = theArray.visit_occurrence_id
        var start_date = theArray.drug_exposure_start_date
        var end_date = theArray.drug_exposure_end_date
        var drug_name = theArray.drug_concept_label
        //console.log(visit_id + start_date + end_date + drug_name)
        str+=("{id:" + i + ", content:'" + drug_name + "', start:'" +
        start_date + "', end:'" + end_date + "'},\n");
    }
    str=str+"{id:65, content:'today', start: '2011-01-01'}"
    return str;
}

var test = appt();
/* !!! Copy This!
console.log(test); */

//console.log(typeof(test));
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
var container = document.getElementById('timeline-visualization');

// Create a DataSet (allows two way data-binding)
var items = new vis.DataSet([{id:0, content:'metformin hydrochloride 500 MG Oral Tablet', start:'2008-03-21', end:'2008-04-19'},
{id:1, content:'No matching concept', start:'2008-10-28', end:'2008-11-26'},
{id:2, content:'metformin hydrochloride 850 MG Oral Tablet', start:'2010-02-19', end:'2010-03-10'},
{id:3, content:'candesartan cilexetil 16 MG Oral Tablet', start:'2008-08-31', end:'2008-09-29'},
{id:4, content:'No matching concept', start:'2008-08-27', end:'2008-09-15'},
{id:5, content:'carisoprodol 350 MG Oral Tablet', start:'2008-07-29', end:'2008-08-27'},
{id:6, content:'oxygen 99 % Gas for Inhalation', start:'2010-01-01', end:'2010-01-30'},
{id:7, content:'ciprofloxacin 750 MG Oral Tablet', start:'2010-02-07', end:'2010-03-08'},
{id:8, content:'eszopiclone 2 MG Oral Tablet', start:'2008-07-05', end:'2008-08-03'},
{id:9, content:'ketoprofen 75 MG Oral Capsule', start:'2009-01-28', end:'2009-02-26'},
{id:10, content:'albuterol 4 MG Oral Tablet', start:'2009-12-15', end:'2010-01-13'},
{id:11, content:'ibuprofen 800 MG Oral Tablet', start:'2008-11-06', end:'2008-12-05'},
{id:12, content:'ampicillin 250 MG Oral Capsule', start:'2008-03-23', end:'2008-04-21'},
{id:13, content:'24 HR naproxen 500 MG Extended Release Oral Tablet [Naprelan]', start:'2009-05-23', end:'2009-08-20'},
{id:14, content:'meclizine hydrochloride 25 MG Oral Tablet', start:'2008-10-24', end:'2008-11-22'},
{id:15, content:'chondroitin sulfates 400 MG / glucosamine hydrochloride 500 MG Oral Capsule', start:'2009-09-22', end:'2009-10-21'},
{id:16, content:'No Label', start:'2009-04-06', end:'2009-06-04'},
{id:17, content:'epoetin alfa', start:'2010-01-04', end:'2010-02-03'},
{id:18, content:'No Label', start:'2009-03-10', end:'2009-04-08'},
{id:19, content:'cetirizine hydrochloride 10 MG Oral Tablet [Zyrtec]', start:'2009-03-23', end:'2009-04-21'},
{id:20, content:'amlodipine 10 MG Oral Tablet', start:'2008-08-19', end:'2008-09-17'},
{id:21, content:'phenobarbital 16 MG Oral Tablet', start:'2008-12-10', end:'2009-01-08'},
{id:22, content:'doxepin 25 MG Oral Capsule', start:'2009-10-01', end:'2009-10-30'},
{id:23, content:'24 HR nifedipine 30 MG Extended Release Oral Tablet', start:'2008-01-09', end:'2008-02-07'},
{id:24, content:'amitriptyline hydrochloride 10 MG / perphenazine 2 MG Oral Tablet', start:'2008-11-29', end:'2008-12-28'},
{id:25, content:'ibuprofen 600 MG Oral Tablet', start:'2008-09-02', end:'2008-10-01'},
{id:26, content:'tolazamide 250 MG Oral Tablet', start:'2008-05-02', end:'2008-05-31'},
{id:27, content:'guaifenesin 90 MG / theophylline 150 MG Oral Capsule', start:'2009-05-15', end:'2009-08-12'},
{id:28, content:'omeprazole 20 MG Delayed Release Oral Capsule', start:'2008-02-18', end:'2008-03-18'},
{id:29, content:'chlorthalidone 25 MG Oral Tablet', start:'2008-02-02', end:'2008-03-02'},
{id:30, content:'paricalcitol Injectable Solution', start:'2010-01-04', end:'2010-02-03'},
{id:31, content:'paricalcitol Injectable Solution', start:'2010-01-04', end:'2010-02-03'},
{id:32, content:'hydroxyzine pamoate 25 MG Oral Capsule', start:'2008-08-26', end:'2008-09-24'},
{id:33, content:'losartan potassium 50 MG Oral Tablet [Cozaar]', start:'2008-02-24', end:'2008-03-24'},
{id:34, content:'risperidone 1 MG Oral Tablet [Risperdal]', start:'2008-07-16', end:'2008-08-14'},
{id:35, content:'trazodone hydrochloride 50 MG Oral Tablet', start:'2009-04-18', end:'2009-05-17'},
{id:36, content:'No Label', start:'2008-07-22', end:'2008-08-10'},
{id:37, content:'acetaminophen 325 MG / butalbital 50 MG / caffeine 40 MG Oral Tablet', start:'2010-01-16', end:'2010-02-04'},
{id:38, content:'iodine 70 MG/ML Topical Solution', start:'2009-12-04', end:'2010-01-02'},
{id:39, content:'tacrolimus 1 MG Oral Capsule', start:'2009-03-28', end:'2009-04-26'},
{id:40, content:'nefazodone hydrochloride 200 MG Oral Tablet', start:'2008-01-14', end:'2008-02-12'},
{id:41, content:'No Label', start:'2008-12-09', end:'2009-01-07'},
{id:42, content:'pergolide 1 MG Oral Tablet', start:'2009-01-28', end:'2009-02-26'},
{id:43, content:'dimenhydrinate 50 MG/ML Injectable Solution', start:'2009-07-13', end:'2009-10-10'},
{id:44, content:'metronidazole 250 MG Oral Tablet', start:'2010-02-05', end:'2010-02-14'},
{id:45, content:'colestipol hydrochloride 5000 MG Granules for Oral Suspension [Colestid]', start:'2009-08-29', end:'2009-09-27'},
{id:46, content:'No Label', start:'2009-06-27', end:'2009-09-24'},
{id:47, content:'warfarin sodium 6 MG Oral Tablet', start:'2008-09-14', end:'2008-10-13'},
{id:48, content:'oxygen 99 % Gas for Inhalation', start:'2009-08-06', end:'2009-09-04'},
{id:49, content:'lovastatin 10 MG Oral Tablet', start:'2010-01-24', end:'2010-02-22'},
{id:50, content:'No Label', start:'2009-01-19', end:'2009-01-28'},
{id:51, content:'bisoprolol fumarate 10 MG Oral Tablet', start:'2008-08-23', end:'2008-09-21'},
{id:52, content:'fluoxetine 10 MG Oral Capsule', start:'2010-02-12', end:'2010-03-13'},
{id:53, content:'isosorbide dinitrate 20 MG Oral Tablet', start:'2008-10-29', end:'2008-11-27'},
{id:54, content:'dicyclomine hydrochloride 20 MG Oral Tablet', start:'2009-10-02', end:'2009-10-31'},
{id:55, content:'cyclophosphamide', start:'2008-11-21', end:'2008-12-21'},
{id:56, content:'warfarin sodium 5 MG Oral Tablet', start:'2009-08-07', end:'2009-08-16'},
{id:57, content:'dexamethasone phosphate 1 MG/ML Ophthalmic Solution', start:'2008-12-02', end:'2008-12-31'},
{id:58, content:'metformin hydrochloride 850 MG Oral Tablet', start:'2009-01-16', end:'2009-04-15'},
{id:59, content:'azithromycin 250 MG Oral Tablet', start:'2009-04-26', end:'2009-05-25'},
{id:60, content:'propranolol hydrochloride 10 MG Oral Tablet', start:'2009-10-21', end:'2009-11-19'},
{id:61, content:'omeprazole 40 MG Delayed Release Oral Capsule', start:'2009-11-06', end:'2009-11-15'},
{id:62, content:'chlorothiazide 500 MG Oral Tablet', start:'2009-05-18', end:'2009-06-16'},
{id:63, content:'simvastatin 10 MG Oral Tablet', start:'2009-07-06', end:'2009-08-04'},
{id:64, content:'metronidazole 500 MG Oral Tablet', start:'2009-06-28', end:'2009-07-07'}]);

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