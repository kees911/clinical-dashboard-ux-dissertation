/*$('#p1panda').DataTable(
    {info: false,
    paging: false,
    scrollCollapse: true,
    scrollY: '225px',
    scrollX: '800px',
    "searching": true,
    scroller: true
  });*/

  /*$(document).ready(function(){
    $('#p1panda').append(
      $('<tfoot/>').append($('#p1panda thead tr').clone())
    );
    var table = $('#p1panda').DataTable();
  });*/

//var table=$('#p1panda').DataTable();

new DataTable('#p1panda', {
    info: false,
    paging: false,
    scrollCollapse: true,
    scrollY: '15vh',
    //scrollX: '955px',
    "searching": true,
    scroller: true,
    columns:[{width:'3%'},{width:'10%'}, {width:'10%'}, {width:'35%'}, {width:'10%'}, {width:'16%'}, {width:'16%'}],

  initComplete: function(){

    this.api().columns([6]).every(function(){
      let column = this;

      //create select element
      let select = document.createElement('select')
      $(select).appendTo($(column.header()));
      select.add(new Option(''))
      $(select).click(function(e){
        e.stopPropagation();
      });
      

      //apply listener for user change in value
      select.addEventListener('change', function(){
        column.search(select.value, {exact: true}).draw();
      });

      //add list of options
      column.data().unique().sort().each(function(d,j){
        select.add(new Option(d));
      });
    });

    setTimeout(function(){
      this.columns.adjust();
    }, 500);
  }

  
  });
  


//$(document).ready( function () {
  //$('#panda').DataTable();
//} );*/