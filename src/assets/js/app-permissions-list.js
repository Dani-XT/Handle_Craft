/**
 * App user list (jquery)
 */

'use strict';

$(function () {
  var dt_entidades_table = $('.datatables-modelos'),
    dt_modelos_excluidos_table = $('.datatables-modelos-excluidos')

  // Users List datatable
  if (dt_entidades_table.length) {
    var dt_entidades = dt_entidades_table.DataTable({
      
      columnDefs: [
        {
          // NOMBRE
          targets: 0,
        },
        {
          // ASIGNADO A
          targets: 1,
        },
        {
          // Permisos
          targets: 2,
        },
        {
          // ACCIONES
          targets: 3,
        },
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
        searchPlaceholder: 'Search Permissions',
        paginate: {
          next: '<i class="ri-arrow-right-s-line"></i>',
          previous: '<i class="ri-arrow-left-s-line"></i>'
        }
      },
      // Buttons for modal
      buttons: [
        {
          text: '<i class="ri-add-line me-0 me-sm-1"></i><span class="d-none d-sm-inline-block">Add Permission</span>',
          className: 'btn btn-primary mb-5 mb-md-0 waves-effect waves-light',
          attr: {
            'data-bs-toggle': 'modal',
            'data-bs-target': '#addPermissionModal'
          },
          init: function (api, node, config) {
            $(node).removeClass('btn-secondary');
          }
        }
      ],
    });
  }

  // Users List datatable
  if (dt_modelos_excluidos_table.length) {
    var dt_modelos_excluidos = dt_modelos_excluidos_table.DataTable({
      
      columnDefs: [
        {
          // NOMBRE
          targets: 0,
        },
        {
          // ASIGNADO A
          targets: 1,
        },
        {
          // Permisos
          targets: 2,
        },
        {
          // ACCIONES
          targets: 3,
        },
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
        searchPlaceholder: 'Search Permissions',
        paginate: {
          next: '<i class="ri-arrow-right-s-line"></i>',
          previous: '<i class="ri-arrow-left-s-line"></i>'
        }
      },
      // Buttons for modal
      buttons: [
        {
          text: '<i class="ri-add-line me-0 me-sm-1"></i><span class="d-none d-sm-inline-block">Add Permission</span>',
          className: 'btn btn-primary mb-5 mb-md-0 waves-effect waves-light',
          attr: {
            'data-bs-toggle': 'modal',
            'data-bs-target': '#addPermissionModal'
          },
          init: function (api, node, config) {
            $(node).removeClass('btn-secondary');
          }
        }
      ],
    });
  }
});
