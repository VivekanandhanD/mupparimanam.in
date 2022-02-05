$(document).ready(function(){
    $('#user-list').DataTable({
        ajax: {
            url: '/sunday/',
            dataSrc: 'data'
        },
        serverSide: true,
//        processing: true,
        searching: false,
//        columns: ['id', 'email', 'date_joined', 'count'],
        columns: [
          { "data": "id" },
          { "data":"email" },
          { "data":"date_joined" },
          { "data":"count" }
        ],
//        dataSrc: 'data'
    });
});