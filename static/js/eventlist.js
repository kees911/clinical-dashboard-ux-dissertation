$(document).ready(function () {
    $('#datatable').DataTable({
      ajax: [{
          url: '../api/conditions_timeline',
          dataSrc: ''
      }],
      serverSide: true,
      columns: [
          {data: 'condition_start_date'},
          {data: 'condition_end_date'},
          {data: 'provider_id'},
          {data: 'condition_concept_label'},
          {data: 'condition_type_concept_label'},
          {data: 'condition_source_concept_label'},
          {data: 'condition_status_concept_label'}
      ],
    });
  });

  console.log();