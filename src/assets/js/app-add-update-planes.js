/**
 * Add Update Plan - Planes
 */

'use strict';

// repeater (jquery)
$(function () {
  var formRepeater = $('.form-repeater');
  if (formRepeater.length) {
    var row = 2;
    var col = 1;
    formRepeater.on('submit', function (e) {
      e.preventDefault();
    });
    formRepeater.repeater({
      defaultValues: {
        'nombre': '',
        'descripcion': '',
        'estado': '1' // o el valor por defecto si lo deseas
      },
      show: function () {
        let textarea = $(this).find('.autosize');
        let selects = $(this).find('select.selectpicker');
        // Carga el segmento duplicado
        selects.each(function () {
          if ($(this).parent().hasClass('bootstrap-select')) {
            const wrapper = $(this).parent('.bootstrap-select');
            wrapper.before($(this));
            wrapper.remove();
          }
        });
        $(this).hide().fadeIn('fast', function() {
          selects.selectpicker();
          if (textarea.length) autosize(textarea);
        });
      },
      hide: function (e) {
        $(this).fadeOut(200, function () {
          $(this).remove();
        });
      }
    });
  }
});