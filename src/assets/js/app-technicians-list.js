/**
 * Page User List
 */

'use strict';

// Datatable (jquery)
$(function () {
    var dt_tecnicos_table = $('.datatables-tecnicos')

    if (dt_tecnicos_table.length) {
        var dt_tecnicos = dt_tecnicos_table.DataTable({
            columnDefs: [
                {
                    //Nombre
                    targets: 0,
                    orderable: true,
                    searchable: true
                },
                {
                    //Email
                    targets: 1,
                    orderable: true,
                    searchable: true
                },
                {
                    //ROL
                    targets: 2,
                    orderable: false,
                    searchable: false
                },
                {
                    //Estado
                    targets: 3,
                    orderable: false,
                    searchable: false
                },
                {
                    //STAFF
                    targets: 4,
                    orderable: false,
                    searchable: false
                },
                {
                    //Actions
                    targets: 5,
                    orderable: false,
                    searchable: false
                }
            ],
            order: [[1, 'asc']],
            dom:
                '<"row mx-1"' +
                '<"col-sm-12 col-md-3 mb-n5" l>' +
                '<"col-sm-12 col-md-9"<"dt-action-buttons text-xl-end text-lg-start text-md-end text-start d-flex align-items-center justify-content-md-end justify-content-center flex-wrap me-1"<"me-4"f>B>>' +
                '>t' +
                '<"row mx-1"' +
                '<"col-sm-12 col-md-6"i>' +
                '<"col-sm-12 col-md-6"p>' +
                '>',
            language: {
                sLengthMenu: 'Show _MENU_',
                search: '',
                searchPlaceholder: 'Buscar Tecnicos',
                paginate: {
                next: '<i class="ri-arrow-right-s-line"></i>',
                previous: '<i class="ri-arrow-left-s-line"></i>'
                }
            },
            buttons: [
                {
                text: '<i class="ri-add-line me-0 me-sm-1"></i><span class="d-none d-sm-inline-block">Crear Usuarios</span>',
                className: 'btn btn-primary mb-5 mb-md-0 waves-effect waves-light',
                action: function() {
                    const url = dt_tecnicos_table.data('datatables-urls')
                    if (url) {
                    window.location.href = url
                    } else {
                    console.error("No se encontro la URL para crear usuarios")
                    }
                },
                init: function (api, node) {
                    $(node).removeClass('btn-secondary');
                }
                }
            ],
        })
    }
})