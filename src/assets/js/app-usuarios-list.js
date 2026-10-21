/**
 * Page User List
 */

'use strict';

// Datatable (jquery)
$(function () {

  let borderColor, bodyBg, headingColor;

  if (isDarkStyle) {
    borderColor = config.colors_dark.borderColor;
    bodyBg = config.colors_dark.bodyBg;
    headingColor = config.colors_dark.headingColor;
  } else {
    borderColor = config.colors.borderColor;
    bodyBg = config.colors.bodyBg;
    headingColor = config.colors.headingColor;
  }

  // Variable declaration for table
  var dt_facultad_table = $('.datatables-facultades'),
    dt_area_table = $('.datatables-areas'),
    dt_cargo_table = $('.datatables-cargos'),
    dt_user_table = $('.datatables-usuarios')

  // TODO: Facultades datatable
  if (dt_facultad_table.length) {
    var dt_facultad = dt_facultad_table.DataTable({
      pageLength: 3,
      columnDefs: [
        {
          // Avatar - Nombre facultad
          targets: 0,
          orderable: true,
          searchable: true
        },
        {
          // Acciones
          targets: 1,
          orderable: false,
          searchable: false
        }
      ],
      order: [[0, 'asc']],
      dom:
        '<"row px-3 d-flex align-items-center"' +
        '<"col-sm-12 col-md-6 mb-2"f>' +
        '<"col-sm-12 col-md-6 text-end mb-2"B>' +
        '>t' +
        '<"row mx-1"' +
        '<"col-sm-12 col-md-6"i>' +
        '<"col-sm-12 col-md-6"p>' +
        '>',
      language: {
        sLengthMenu: 'Show _MENU_',
        search: '',
        searchPlaceholder: 'Buscar Facultades',
        paginate: {
          next: '<i class="ri-arrow-right-s-line"></i>',
          previous: '<i class="ri-arrow-left-s-line"></i>'
        }
      },
      // Buttons for modal
      buttons: [
        {
          text: '<i class="ri-add-line me-0 me-sm-1"></i><span class="d-none d-sm-inline-block">Crear</span>',
          className: 'btn btn-primary mb-5 mb-md-0 waves-effect waves-light custom-modal',
          attr: {
            'data-urls': dt_facultad_table.data('datatables-urls')
          },
          
          init: function (api, node) {
            $(node).removeClass('btn-secondary');
          }
        }
      ],
    })
  }

  if (dt_area_table.length) {
    var dt_area = dt_area_table.DataTable({
      columnDefs: [
        {
          // Avatar y nombre
          targets: 0,
          orderable: true,
          searchable: true 
        },
        {
          // Nombre completo
          targets: 1,
          orderable: true,
          searchable: true
        },
        {
          // Acciones
          targets: 2,
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
        searchPlaceholder: 'Buscar Areas',
        paginate: {
          next: '<i class="ri-arrow-right-s-line"></i>',
          previous: '<i class="ri-arrow-left-s-line"></i>'
        }
      },
      // Buttons for modal
      buttons: [
        {
          text: '<i class="ri-add-line me-0 me-sm-1"></i><span class="d-none d-sm-inline-block">Crear</span>',
          className: 'btn btn-primary mb-5 mb-md-0 waves-effect waves-light custom-modal',
          attr: {
            'data-urls': dt_area_table.data('datatables-urls')
          },
          init: function (api, node) {
            $(node).removeClass('btn-secondary');
          }
        }
      ],
    })
  }

  if (dt_cargo_table.length) {
    var dt_cargo = dt_cargo_table.DataTable({
      columnDefs: [
        {
          // Nombre
          targets: 0,
          orderable: true,
          searchable: true
        },
        {
          // Acciones
          targets: 1,
          orderable: false,
          searchable: false
        }
      ],
      order: [[0, 'asc']],
      dom:
        '<"row px-3 d-flex align-items-center"' +
        '<"col-sm-12 col-md-6 mb-2"f>' +
        '<"col-sm-12 col-md-6 text-end mb-2"B>' +
        '>t' +
        '<"row mx-1"' +
        '<"col-sm-12 col-md-6"i>' +
        '<"col-sm-12 col-md-6"p>' +
        '>',
      language: {
        sLengthMenu: 'Show _MENU_',
        search: '',
        searchPlaceholder: 'Buscar Cargos',
        paginate: {
          next: '<i class="ri-arrow-right-s-line"></i>',
          previous: '<i class="ri-arrow-left-s-line"></i>'
        }
      },
      // Buttons for modal
      buttons: [
        {
          text: '<i class="ri-add-line me-0 me-sm-1"></i><span class="d-none d-sm-inline-block">Crear</span>',
          className: 'btn btn-primary mb-5 mb-md-0 waves-effect waves-light custom-modal',
          attr: {
            'data-urls': dt_cargo_table.data('datatables-urls')
          },
          init: function (api, node) {
            $(node).removeClass('btn-secondary');
          }
        }
      ],
    })
  }

  // TODO: Usuarios datatable
  if (dt_user_table.length) {
    var dt_user = dt_user_table.DataTable({
      columnDefs: [
        {
          // Avatar - Nombre - email
          targets: 0,
          orderable: true,
          searchable: true
        },
        {
          // Cargo
          targets: 1,
          searchable: true
        },
        {
          // Direccion
          targets: 2,
          orderable: false,
          searchable: true
        },
        {
          // Modalidad
          targets: 3,
          orderable: false,
          searchable: true
        },
        {
          // Actiosn
          targets: 4,
          orderable: false,
          searchable: false
        },
      ],
      order: [[2, 'desc']],
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
        searchPlaceholder: 'Buscar Usuarios',
        paginate: {
          next: '<i class="ri-arrow-right-s-line"></i>',
          previous: '<i class="ri-arrow-left-s-line"></i>'
        }
      },
      // Buttons for modal
      buttons: [
        {
          text: '<i class="ri-add-line me-0 me-sm-1"></i><span class="d-none d-sm-inline-block">Crear Usuarios</span>',
          className: 'btn btn-primary mb-5 mb-md-0 waves-effect waves-light',
          action: function() {
            const url = dt_user_table.data('datatables-urls')
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
    });
  }
});