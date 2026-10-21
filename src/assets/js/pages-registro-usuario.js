/**
 *  Page auth register multi-steps
 */

'use strict';
// Multi Steps Validation
// --------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', function (e) {
  (function () {
    // INICIO STEP VALIDATION
    const stepsValidation = document.querySelector('#multiStepsValidation');
    if (typeof stepsValidation !== undefined && stepsValidation !== null) {
      // Multi Steps form
      const stepsValidationForm = stepsValidation.querySelector('#multiStepsForm');
      // Form steps
      const stepsValidationFormStep1 = stepsValidationForm.querySelector('#detallesCuentaValidacion');
      const stepsValidationFormStep2 = stepsValidationForm.querySelector('#informacionPersonalValidacion');
      const stepsValidationFormStep3 = stepsValidationForm.querySelector('#informacionHogarValidacion');

      // Multi steps next prev button
      const stepsValidationNext = [].slice.call(stepsValidationForm.querySelectorAll('.btn-next'));
      const stepsValidationPrev = [].slice.call(stepsValidationForm.querySelectorAll('.btn-prev'));

      let validationStepper = new Stepper(stepsValidation, {
        linear: true
      });

      // ------------------------------------------------
      // TODO: Validacion Detalle Cuenta
      // ------------------------------------------------
      const multiSteps1 = FormValidation.formValidation(stepsValidationFormStep1, {
        fields: {
          email: {
            validators: {
              notEmpty: {
                message: 'Favor ingrese un email'
              },
              emailAddress: {
                message: 'Email no valido'
              }
            }
          },
          password: {
            validators: {
              notEmpty: {
                message: 'Favor ingrese una contraseña'
              }
            }
          },
          password2: {
            validators: {
              notEmpty: {
                message: 'Contraseñas no compatbiles'
              },
              identical: {
                compare: function () {
                  return stepsValidationFormStep1.querySelector('[name="password"]').value;
                },
                message: 'La contraseña es incorrecta'
              }
            }
          }
        },
        plugins: {
          trigger: new FormValidation.plugins.Trigger(),
          bootstrap5: new FormValidation.plugins.Bootstrap5({
            // eleInvalidClass: '',
            eleValidClass: '',
          }),
          autoFocus: new FormValidation.plugins.AutoFocus(),
          submitButton: new FormValidation.plugins.SubmitButton()
        },
        init: instance => {
          instance.on('plugins.message.placed', function (e) {
            if (e.element.parentElement.classList.contains('input-group')) {
              e.element.parentElement.insertAdjacentElement('afterend', e.messageElement);
            }
          });
        }
      }).on('core.form.valid', function () {
        // Jump to the next step when all fields in the current step are valid
        validationStepper.next();
      });

      // Personal info
      const multiSteps2 = FormValidation.formValidation(stepsValidationFormStep2, {
        fields: {
          nombre: {
            validators: {
              notEmpty: {
                message: 'Favor ingrese su nombre'
              },
              regexp: {
                regexp: /^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]{2,}$/,
                message: 'El nombre debe tener al menos 2 letras y no contener números'
              }
            }
          },
          apellido: {
            validators: {
              notEmpty: {
                message: 'Favor ingrese su apellido'
              },
              regexp: {
                regexp: /^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]{2,}$/,
                message: 'El apellido debe tener al menos 2 letras y no contener números'
              }
            }
          },
          rut: {
            validators: {
              notEmpty: {
                message: 'Debe ingresar su RUT'
              },
              stringLength: {
                min: 11,
                max: 12,
                message: 'Ingrese su RUT'
              }
            }
          },
          ahorro_habitacional_uf: {
            validators: {
              notEmpty: {
                message: 'Ingrese su Ahorro Habitacional'
              },
              stringLength: {
                min: 3,
                message: 'Ingrese su Ahorro Habitacional'
              }
            }
          },
          telefono: {
            validators: {
              notEmpty: {
                message: 'Favor ingrese su numero'
              },
              stringLength: {
                min: 11,
                max: 11,
                message: 'Ingrese su numero de Telefono'
              }
            }
          },
          codigo_postal: {
            validators: {
              notEmpty: {
                message: 'Favor ingrese su codigo postal'
              },
              stringLength: {
                min: 7,
                max: 7,
                message: 'Ingrese su codigo Postal'
              }
            }
          },
          direccion: {
            validators: {
              notEmpty: {
                message: 'Favor ingrese su direccion'
              }
            }
          },
          numero_casa: {
            validators: {
              notEmpty: {
                message: 'Favor ingrese su numero de casa'
              },
              stringLength: {
                min: 4,
                max: 7,
                message: 'Ingrese su numero de Casa'
              }
            }
          },
          comuna: {
            validators: {
              notEmpty: {
                message: 'Favor ingrese una comuna'
              }
            }
          },
          provincia: {
            validators: {
              notEmpty: {
                message: 'Favor ingrese su provincia'
              }
            }
          },
          region: {
            validators: {
              notEmpty: {
                message: 'Favor ingrese una region'
              }
            }
          },
          fecha_nacimiento: {
            validators: {
              notEmpty: {
                message: 'Favor ingrese su fecha de nacimiento'
              }
            }
          },
        },
        plugins: {
          trigger: new FormValidation.plugins.Trigger(),
          bootstrap5: new FormValidation.plugins.Bootstrap5({
            // eleInvalidClass: '',
            eleValidClass: '',
          }),
          autoFocus: new FormValidation.plugins.AutoFocus(),
          submitButton: new FormValidation.plugins.SubmitButton()
        }
      }).on('core.form.valid', function () {
        // Jump to the next step when all fields in the current step are valid
        validationStepper.next();
      });

      // Social links
      const multiSteps3 = FormValidation.formValidation(stepsValidationFormStep3, {
        fields: {
          cantidad_integrantes: {
            validators: {
              notEmpty: {
                message: 'Favor ingrese la cantidad de integrantes'
              }
            }
          },
          sueldo_hogar: {
            validators: {
              notEmpty: {
                message: 'Favor ingrese el sueldo total del hogar'
              },
              stringLength: {
                min: 2,
                message: 'Ingrese su numero de Casa'
              }
            }
          },
          tramo_rsh: {
            validators: {
              notEmpty: {
                message: 'Favor ingrese el tramo de su RSH'
              }
            }
          },
          ahorro_habitacional: {
            validators: {
              notEmpty: {
                message: 'Favor ingrese su ahorro habitacional'
              }
            }
          },
          condicion_habitacional: {
            validators: {
              notEmpty: {
                message: 'Favor ingrese su condicion habitacional'
              }
            }
          },
          situacion_previsional: {
            validators: {
              notEmpty: {
                message: 'Ingrese su situacion previsional'
              }
            }
          },
          postulaciones_previas: {
            validators: {
              notEmpty: {
                message: 'Ingrese si tuvo postulaciones previas'
              }
            }
          }
        },
        plugins: {
          trigger: new FormValidation.plugins.Trigger(),
          bootstrap5: new FormValidation.plugins.Bootstrap5({
            // Use this for enabling/changing valid/invalid class
            // eleInvalidClass: '',
            eleValidClass: '',
          }),
          autoFocus: new FormValidation.plugins.AutoFocus(),
          submitButton: new FormValidation.plugins.SubmitButton()
        },
        init: instance => {
          instance.on('plugins.message.placed', function (e) {
            if (e.element.parentElement.classList.contains('input-group')) {
              e.element.parentElement.insertAdjacentElement('afterend', e.messageElement);
            }
          });
        }
      })
      stepsValidationNext.forEach(item => {
        item.addEventListener('click', event => {
          // When click the Next button, we will validate the current step
          switch (validationStepper._currentIndex) {
            case 0:
              multiSteps1.validate();
              break;

            case 1:
              multiSteps2.validate();
              break;

            case 2:
              multiSteps3.validate();
              break;

            default:
              break;
          }
        });
      });

      stepsValidationPrev.forEach(item => {
        item.addEventListener('click', event => {
          switch (validationStepper._currentIndex) {
            case 2:
              validationStepper.previous();
              break;

            case 1:
              validationStepper.previous();
              break;

            case 0:

            default:
              break;
          }
        });
      });
    }
  })();
});
