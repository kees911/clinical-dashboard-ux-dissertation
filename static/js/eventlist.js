$(document).ready( function () {
  $('#p1panda').DataTable();
} );

new DataTable('#p1panda', {
  info: false,
  paging: false,
  scrollCollapse: true,
  scrollY: '225px'
});