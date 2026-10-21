/**
 * Utils - Modals
 */

// ---------------------------------------------
// TODO: FUNCIONES GLOBALES
// ---------------------------------------------
document.addEventListener("DOMContentLoaded", function () {
  initGlobalComplementos();
  initGlobalEventListener();
  initCleanStorageFunction();
})
// ---------------------------------------------
// TODO: INICIALIZADORES GLOBLALES DE COMPLEMENTOS
// ---------------------------------------------
function initGlobalComplementos(contenedor = document) {
  let textarea = contenedor.querySelectorAll(".autosize");
  let colorPicker = contenedor.querySelectorAll('.custom-color-picker');
  let select2 = contenedor.querySelectorAll('.select2');
  let scrollBar = contenedor.querySelectorAll('.perfect-scrollbar');
  let selectPicker = $('.selectpicker')
  let cleavejs = contenedor.querySelectorAll('.cleave')
  let numerals = contenedor.querySelectorAll('.numeral');
  let flatPickrList = contenedor.querySelectorAll('.flatpickr-validation')
  let customSearcher = contenedor.querySelectorAll('.custom-searcher')
  let dropzone = contenedor.querySelectorAll('.dropzone')
  // creacion autosize
  if (textarea.length > 0) autosize(textarea);
  // creacion color picker
  if (colorPicker.length > 0) buildColorPicker(colorPicker);
  // creacion select2
  if (select2.length > 0) buildSelect2(select2);
  // creacion perfect scrollbar
  if (scrollBar.length > 0) buildPerfectScrollBar(scrollBar);
  // creacion bootstrap select
  if (selectPicker.length > 0) selectPicker.selectpicker();
  // creacion del cleave
  if (cleavejs.length > 0) buildCleave(cleavejs); 
  // creacion numeral
  if (numerals.length > 0) buildNumeral(numerals);
  // creacion picker fecha
  if (flatPickrList.length > 0) buildFlatpickr(flatPickrList);
  // creacion custom searcher
  if (customSearcher.length > 0) buildCustomSearcher(customSearcher);
  // construccion dropzone
  if (dropzone.length > 0) buildDropzone(dropzone);

  initProcesamiento(contenedor); 
};
// ---------------------------------------------
// TODO: LISTENER GLOBALES
// ---------------------------------------------
function initGlobalEventListener() {
  document.addEventListener("click", function (e) {
    const btnModal = e.target.closest(".custom-modal");
    const sendCalc = e.target.closest('.calc-campo[data-grupo][data-field]');
    const icono = e.target.closest('[data-icon]')
    
    if (sendCalc) initProcesamiento();
    if (btnModal) {
      initCustomModal(btnModal);
      e.preventDefault();
    };
    if (icono) {
      const modal = e.target.closest('.modal');
      if (!modal) return;
      bindIconPicker(icono, modal);
    }
  });

  document.addEventListener("shown.bs.modal", function (e) {
    let modal = e.target;
    showCustomModal(modal);
  });

  document.addEventListener("hidden.bs.modal", function (e) {
    let modal = e.target;
    modal.remove();
  });

  document.addEventListener("submit", function (e) {
    const formLocalStorage = e.target.closest("form[data-local-storage=true]")
    if (formLocalStorage) {
      e.preventDefault()
      initLocalStorageFunction(formLocalStorage)
    }
  })
}
// ---------------------------------------------
// TODO: API CONSULTA Y ALMACENAJE LOCALSTORAGE
// ---------------------------------------------
function initCleanStorageFunction() {
  grupos = document.querySelectorAll('[data-grupo-localstorage]')
  
  grupos.forEach((el) => {
    grupo = el.dataset.grupoLocalstorage;

    key = `grupo_${grupo}`
    console.log(key)
    clearLocalStorageKey(key)

  })
}


function initLocalStorageFunction(formulario, contenedor = document) {
  let grupo = formulario.dataset.grupoLocalstorage;
  let url = formulario.dataset.urlLocalstorage

  if (!grupo) return console.error("No hay un grupo asociado al localstorage");
  if (!url) return console.error("No hay url definida para la API");
  
  const formData = new FormData(formulario);
  
  fetch(url, { 
    method: "POST", 
    body: formData
  }).then(r => r.json())
    .then(data => buildLocalStorageFunction(data, contenedor, grupo)
    ).catch((err) => {
    console.error("Error al realizar consulta:", err);
  })
}

function buildLocalStorageFunction(data, contenedor, grupo) {
  let storageKey = `grupo_${grupo}`;
  saveToLocalStorage(storageKey, data)
  buildClonLocalStorage(contenedor, grupo)
}

function buildClonLocalStorage(contenedor, grupo) {
  const plantillas = contenedor.querySelectorAll(`[data-clone-localstorage][data-grupo-localstorage="${grupo}"]`)
  if (!plantillas) return console.error("No existe plantilla de error");
  
  const key = `grupo_${grupo}`;
  const dataGrupo = getFromLocalStorage(key);

  contenedor.querySelectorAll(`.clon-generado`).forEach(el => el.remove());

  
  plantillas.forEach(plantilla => {
    const modelo = plantilla.dataset.keyLocalstorage;
    if (!modelo || !dataGrupo[modelo]) return;

    const dataList = Array.isArray(dataGrupo[modelo]) ? dataGrupo[modelo] : [dataGrupo[modelo]];

    dataList.forEach(dataObject => {
      const yaExiste = contenedor.querySelector(`.clon-generado[data-id="${dataObject.id}"]`);
      if (yaExiste) return;
      const clon = plantilla.cloneNode(true);
      clon.classList.remove("d-none"); // por si estaba oculta
      clon.classList.add("clon-generado");
      
      clon.setAttribute("data-id", dataObject.id);
      clon.setAttribute("data-key-localstorage", modelo);
      // Insertar el clon después de la plantilla oculta
      plantilla.parentNode.insertBefore(clon, plantilla.nextSibling);
    });

    showLocalStorageFunction(key, grupo, contenedor)
  });
}

function showLocalStorageFunction(key, grupo, contenedor = document) {
  const dataGrupo = getFromLocalStorage(key);

  if (!dataGrupo || typeof dataGrupo !== 'object') {
    console.warn(`⚠️ No hay datos para el grupo: ${grupo}`);
    return;
  }

  contenedor.querySelectorAll(`.clon-generado`).forEach(clon => {
    const modelo = clon.dataset.keyLocalstorage;
    const id = clon.dataset.id;

    if (!modelo || !dataGrupo[modelo]) return;

    const dataList = Array.isArray(dataGrupo[modelo]) ? dataGrupo[modelo] : [dataGrupo[modelo]];
    const dataObject = dataList.find(d => d.id == id);
    if (!dataObject) return;

    clon.querySelectorAll('[data-bind-localstorage]').forEach(el => {
      const campo = el.dataset.bindLocalstorage;

      if (dataObject[campo] !== undefined) {
        if (el.tagName.toLowerCase() === 'a') {
          el.setAttribute("href", dataObject[campo]);
        } else if (['input', 'textarea'].includes(el.tagName.toLowerCase())) {
          el.value = dataObject[campo];
        } else {
          el.textContent = dataObject[campo];
        }
      }
    });
  });

  // 💥 AQUÍ estaba el error: el siguiente bloque estaba mal cerrado
  const inputTargets = contenedor.querySelectorAll(`[data-input-localstorage][data-grupo-localstorage="${grupo}"]`);
  inputTargets.forEach(input => {
    const subclave = input.dataset.inputLocalstorage;  // subgrupo dentro del grupo
    const campos = input.dataset.fieldsLocalstorage?.split(',').map(s => s.trim()) || []; // campos a incluir
    const dataModelo = dataGrupo[subclave];

    if (!dataModelo) {
      input.value = "[]";
      return;
    }

    const lista = Array.isArray(dataModelo) ? dataModelo : [dataModelo];

    const resultado = lista.map(item => {
      const datos = {};
      campos.forEach(campo => {
        if (item.hasOwnProperty(campo)) {
          datos[campo] = item[campo];
        }
      });
      return datos;
    });

    input.value = JSON.stringify(resultado);
  });
  
}



// ---------------------------------------------
// TODO: LOCALSTORAGE
// ---------------------------------------------
function saveToLocalStorage(storageKey, datos) {
  if (!storageKey || datos === undefined) return console.error("Faltan datos para guardar en localStorage");
  
  if (typeof datos === "object" && !Array.isArray(datos)) {
    let currentData = JSON.parse(localStorage.getItem(storageKey)) || {};

    for (let modelo in datos) {
      if (Object.prototype.hasOwnProperty.call(datos, modelo)) {
        const nuevos = Array.isArray(datos[modelo]) ? datos[modelo] : [datos[modelo]];
      
        if (!Array.isArray(currentData[modelo])) {
          currentData[modelo] = [];
        }

        nuevos.forEach(nuevo => {
          const index = currentData[modelo].findIndex(e => e.id === nuevo.id);
          if (index !== -1) {
            currentData[modelo][index] = nuevo; // actualiza si existe
          } else {
            currentData[modelo].push(nuevo); // agrega si no existe
          }
        });
      }
    }
    localStorage.setItem(storageKey, JSON.stringify(currentData));
  } else {
    localStorage.setItem(storageKey, JSON.stringify(datos));
  }
  console.log(`Datos guardados en ${storageKey}`);
}
// Obtener todos los elementos almacenados
function getFromLocalStorage(key, subclave = null) {
  const data = JSON.parse(localStorage.getItem(key)) || {};
  if (subclave) {
    return data[subclave] || [];
  }
  return data;
}

function removeFromLocalStorage(key, id, idField = 'id') {
  const storage = JSON.parse(localStorage.getItem(key)) || [];
  const updated = storage.filter(e => e[idField] !== id);
  localStorage.setItem(key, JSON.stringify(updated));
}
// Limpiar todo
function clearLocalStorageKey(key) {
  localStorage.removeItem(key);
}

// ---------------------------------------------
// TODO: API CONSULTAS BACKEND
// ---------------------------------------------
function initProcesamiento(contenedor = document) {
  const campos = contenedor.querySelectorAll('.calc-campo[data-grupo][data-field]'); //inputs

  campos.forEach(campoInput => {
    if (campoInput.dataset.initialized === 'true') { 
      console.error("Listener ya inicializado")
      return;
    }
    campoInput.dataset.initialized = "true";
    
    const buildprocesamiento = () => buildProcesamiento(contenedor, campoInput)
    
    campoInput.addEventListener("input", buildprocesamiento);
    campoInput.addEventListener("change", buildprocesamiento);

    bindEventosEspeciales(campoInput, buildprocesamiento);
  })

}
// CONSTRUCTOR PROCESAMIENTO
function buildProcesamiento(contenedor, campoInput) {
  const grupo = campoInput.dataset.grupo;
  const btnGrupo = contenedor.querySelector(`.send-calc[data-grupo="${grupo}"]`);
  const camposGrupo = contenedor.querySelectorAll(`.calc-campo[data-grupo="${grupo}"][data-field]`);
  const camposResultados = contenedor.querySelectorAll(`[data-grupo="${grupo}"][data-bind]`)
  const datos = {};
  
  if (!btnGrupo) return console.error(`Boton no encontrado para grupo ${grupo}`);
  
  const rawValor = campoInput.cleave ? campoInput.cleave.getRawValue() : campoInput.value;
  if (!rawValor || rawValor === '0') {
    return;
  }

  const urls = btnGrupo.dataset.urls;
  camposGrupo.forEach(campo => {
    if (campo.dataset.field) {
      datos[campo.dataset.field] = campo.cleave ? campo.cleave.getRawValue() : campo.value;
    }
  });

  fetch(`${urls}?${new URLSearchParams(datos)}`)
    .then((response) => response.json())
    .then((data) => showProcesamiento(contenedor, grupo, data))
  .catch((err) => {
    console.error("Error al realizar consulta:", err);
  })
}
// EJECUCION DEL PROCESAMIENTO
function showProcesamiento(contenedor, grupo, data) {
  for (const key in data) {
    const resultados = contenedor.querySelectorAll(`[data-grupo="${grupo}"][data-bind="${key}"]`);
    resultados.forEach(resultado => {
      const valor = data[key]
      if (["INPUT", "TEXTAREA", "SELECT"].includes(resultado.tagName)) {
        if ($(resultado).hasClass('select2-hidden-accessible')) {
          $(resultado).val(valor).trigger("change");
        } else {
          resultado.value = "";
          resultado.value = valor;
        }
      } else {
        resultado.textContent = ""
        resultado.textContent = valor;
      }
    });
  }
  const numerals = contenedor.querySelectorAll('.numeral');
  if (numerals.length > 0) buildNumeral(numerals);
}
// Arreglar errores
function bindEventosEspeciales(elemento, callback) {
  if (typeof $ === "undefined") return;

  const $elem = $(elemento);

  if ($elem.hasClass('select2-hidden-accessible')) {
    $elem.on('select2:select select2:unselect', callback);
  }
  if ($elem.hasClass('selectpicker')) {
    $elem.on('changed.bs.select', callback);
  }
}

// ---------------------------------------------
// TODO: CARGA Y ELIMINACION DE MODALES
// ---------------------------------------------
function initCustomModal(btnModal) {
  let urls = btnModal.getAttribute("data-urls") || btnModal.getAttribute("href");
  const options = {
    isSearch: btnModal.getAttribute("data-search") || false,
    isIcono: btnModal.getAttribute("data-icono-target") || false,
  }

  // consulta asincrona
  fetch(urls)
    .then((response) => response.json())
    .then((data) => buildCustomModal(data.html, options))
  .catch((err) => {
    console.error("Error al cargar modal:", err)
  })
}
// construye el custom modal
function buildCustomModal(data, options) {
  let contenedor = document.getElementById("custom-modal");
  contenedor.innerHTML = data;
  let customModal = contenedor.querySelector(".modal");
  if (!customModal) return console.error("El modal no fue encontrado en el DOM");
  customModal._customOptions = options;
  const modal = new bootstrap.Modal(customModal)
  modal.show()
}
// muestra el cuistom modal
function showCustomModal(modal) {
  initGlobalComplementos(modal);
  initProcesamiento(modal);
  const options = modal._customOptions || {}

  if (options.isSearch) buildSearch(modal);
}
function buildSearch(customModal) {
  let input = customModal.querySelector("#customSearchInput");
  let buscarElemento = customModal.querySelectorAll("[data-searcher-title]");
  if (input) {
    input.addEventListener("input", function () {
      let filtro = input.value.toLowerCase();

      buscarElemento.forEach((busqueda) => {
        let texto = busqueda.getAttribute("data-searcher-title") || "";
        if (texto.includes(filtro)) {
          busqueda.style.display = "";
          busqueda.classList.remove("d-none");
        } else {
          busqueda.classList.add("d-none");
        }
      });
    });
  }
}
// ---------------------------------------------
// TODO: CONSTRUCTOR MODAL ICONO
// ---------------------------------------------
function bindIconPicker(iconBtn, modal) {
  let options = modal._customOptions
  let iconoSeleccionado = iconBtn.getAttribute("data-icon");
  let grupo = options?.isIcono;

  if (!grupo) return console.error("Grupo no definido para el icono");

  const input = document.querySelector(`[data-icono-target-input="${grupo}"]`);
  const span = document.querySelector(`[data-icono-target-text="${grupo}"]`);
  const preview = document.querySelector(`[data-icono-target-preview="${grupo}"]`);

  if (input) input.value = iconoSeleccionado;
  if (span) span.textContent = iconoSeleccionado;
  if (preview) preview.className = `menu-icon tf-icons ${iconoSeleccionado} ri-22x text-primary`;

  const bsModal = bootstrap.Modal.getInstance(modal);
  bsModal.hide();
}
// ---------------------------------------------
// TODO: CONSTRUYE LOS PICKER DE COLORES
// ---------------------------------------------
function buildColorPicker(colorPicker) {
  colorPicker.forEach(function (picker) {
      let style = picker.getAttribute("data-color-picker-style");
      let grupo = picker.getAttribute("data-color-target");

      let input = document.querySelector(`[data-color-target-input="${grupo}"]`);
      let span = document.querySelector(`[data-color-target-text="${grupo}"]`);

      if (!input || !span) {
        console.error(`Faltan elementos para el grupo: ${grupo}`)
        return;
      }

      let defaultColor = picker.getAttribute("data-color-picker") || 'rgba(144, 85, 253, 1)';

      let pickrInstance = pickr.create({
        el: picker,
        theme: style || 'classic',
        default: defaultColor,
        defaultRepresentation: 'HEXA',
        swatches: [
          'rgba(144, 85, 253, 1)',
          'rgba(86, 202, 0, 1)',
          'rgba(255, 76, 81, 1)',
          'rgba(255, 180, 0, 1)',
          'rgba(22, 177, 255, 1)'
        ],
        components: {
          preview: true,
          opacity: true,
          hue: true,
          interaction: {
            hex: true,
            rgba: true,
            hsla: true,
            hsva: true,
            input: true,
            save: true
          }
        }
      });
      pickrInstance.on('save', (color) => {
        let selectedHex = color.toHEXA().toString();
        input.value = selectedHex;
        span.textContent = selectedHex;
        pickrInstance.hide();
      });
      pickrInstance.on('hide', () => {
        let selectedHex = pickrInstance.getColor().toHEXA().toString();
        input.value = selectedHex;
        span.textContent = selectedHex;
        pickrInstance.applyColor();
      });
  });
}
// ---------------------------------------------
// TODO: CONSTRUYE LOS SELECT2
// ---------------------------------------------
function buildSelect2(select2) {
  $(select2).each(function () {
    const $this = $(this);
    const placeholder = $this.attr('placeholder') || 'Seleccione un valor'
    select2Focus($this); 
    $this.wrap('<div class="position-relative"></div>').select2({
      placeholder: placeholder,
      dropdownParent: $this.parent(),
    });
  });
}
// ---------------------------------------------
// TODO: CONSTRUYE EL PERFECT SCROLLBAR
// ---------------------------------------------
function buildPerfectScrollBar(scrollBars) {
  scrollBars.forEach(scrollBar => {
    const type = scrollBar.getAttribute("data-type-scrollbar");
    if (type === 'vertical') {
      new PerfectScrollbar(scrollBar, { wheelPropagation: false });
    } else if (type === 'horizontal') {
      new PerfectScrollbar(scrollBar, { 
        wheelPropagation: false, 
        suppressScrollY: true 
      });
    } else if (type === 'both') {
      new PerfectScrollbar(scrollBar, { wheelPropagation: false });
    } else {
      new PerfectScrollbar(scrollBar, { wheelPropagation: false });
    }
  });
}
// ---------------------------------------------
// TODO: CONSTRUYE LOS CLEAVE
// ---------------------------------------------
function buildCleave(cleave) {
  cleave.forEach((c) => {
    
    const type = c.getAttribute('data-cleave-type')

    // aplica formato de descuento
    if (type === 'porcentaje') {
      c.cleave = new Cleave(c, {
        numeral: true,
        prefix: '%',
        numeralThousandsGroupStyle: 'none',
        rawValueTrimPrefix: true,
        numeralDecimalScale: 1,      // Cantidad de decimales
        numeralIntegerScale: 3       // Cantidad de dígitos antes del punto decimal
      });
      c.addEventListener('input', function () {
        let raw = c.cleave.getRawValue(); // obtiene sin el prefijo %

        let valor = parseFloat(raw);

        if (!isNaN(valor) && valor > 100) {
          c.value = '%100';
          c.cleave.setRawValue('100'); // reinicia el rawValue también
        }
      });
    }
    if (type === 'uf') {
      c.cleave = new Cleave(c, {
        prefix: 'UF ',
        numeral: true,
        numeralThousandsGroupStyle: 'thousand',
        rawValueTrimPrefix: true,
        delimiter: '.',
        numeralDecimalMark: ','
      });
    }
    if (type == 'moneda') {
      c.cleave = new Cleave(c, {
        prefix: '$',
        numeral: true,
        numeralThousandsGroupStyle: 'thousand',
        delimiter: '.',
        numeralDecimalMark: ','
      })
    }
    if (type === 'telefono') {
      const numeroActual = c.value;
      c.cleave = new Cleave(c, {
        prefix: '9',
        blocks: [1, 4, 4],   // 9 1234 5678
        delimiter: ' ',
        numericOnly: true
      });
      
      if (numeroActual) {
        c.cleave.setRawValue(numeroActual);
      }
    }
    if (type == 'fecha') {
      c.cleave = new Cleave(c, {
        date: true,
        delimiter: '-',
        datePattern: ['d', 'm', 'Y']
      })
    }
    if (type == 'codigo-postal') {
      c.cleave = new Cleave(c, {
        blocks: [7],
        numericOnly: true,
      })
    }
    if (type == 'centenas') {
      c.cleave = new Cleave(c, {
        blocks: [3],
        numericOnly: true,
      })
    }
    if (type == 'numero-casas') {
      c.cleave = new Cleave(c, {
        blocks: [7],
        numericOnly: true,
      })
    }

    if (type === 'rut') {
      c.cleave = new Cleave(c, {
        numeral: false,
        blocks: [12], // max largo aceptado, sin format
        delimiter: '',
        uppercase: true,
      });
      c.addEventListener('input', function (e) {
        const raw = e.target.value.replace(/[^\dkK]/gi, '').toUpperCase();
        e.target.value = formatRut(raw);
      });
    }
  })
}

function formatRut(rut) {
  rut = rut.replace(/^0+/, '').replace(/\./g, '').replace('-', '').toUpperCase();

  if (rut.length < 2) return rut;

  const cuerpo = rut.slice(0, -1);
  const dv = rut.slice(-1);

  let cuerpoFormateado = '';
  let count = 0;

  for (let i = cuerpo.length - 1; i >= 0; i--) {
    cuerpoFormateado = cuerpo[i] + cuerpoFormateado;
    count++;
    if (count === 3 && i !== 0) {
      cuerpoFormateado = '.' + cuerpoFormateado;
      count = 0;
    }
  }

  return `${cuerpoFormateado}-${dv}`;
}

// ---------------------------------------------
// TODO: CONSTRUYE LOS NUMERAL
// ---------------------------------------------
function buildNumeral(numerals) {
  numerals.forEach((numeral) => {
    const type = numeral.getAttribute('data-numeral-type');
    const addPrefix = numeral.getAttribute('data-prefix') !== "none";
    const raw = numeral.textContent.replace(/[^\d]/g, '');
    if (!raw) return;
    const numero = parseInt(raw);
    if (isNaN(numero)) return;

   if (type === 'moneda') {
      numeral.textContent = (addPrefix ? '$' : '') + numero.toLocaleString('es-CL');
    }  
    if (type === 'porcentaje') {
      numeral.textContent = numero.toString() + '%';
    }
    
  });
}
// ---------------------------------------------
// TODO: CONSTRUYE EL SELECTOR DE FECHA
// ---------------------------------------------
function buildFlatpickr(flatPickrList) {
  flatPickrList.forEach(flatPickr => {
    const pickerInstance = flatPickr.flatpickr({
      allowInput: true,
      dateFormat: "d-m-Y",
      minDate: "01-01-1909",
      maxDate: "today",
      locale: 'es'
    });

    flatPickr.addEventListener("input", () => {
      let val = flatPickr.value;
      let dateRegex = /^(\d{2})-(\d{2})-(\d{4})$/;
      if (dateRegex.test(val)) {
        const [_, day, month, year] = val.match(dateRegex);
        const fecha = new Date(Number(year), Number(month) - 1, Number(day));  // <-- CORREGIDO

        if (!isNaN(fecha)) {
          pickerInstance.setDate(fecha, true);
        }
      }
    });
  });
}
// ---------------------------------------------
// TODO: CONSTRUYE EL BUSCADOR
// ---------------------------------------------
function buildCustomSearcher(searchers) {
  searchers.forEach(function (searcher) {
    searcher.addEventListener('input', function () {
      const filtro = this.value.toLowerCase();
      const filas = document.querySelectorAll('table tbody tr');

      filas.forEach(fila => {
        const items = fila.querySelectorAll('[data-searcher-item]');
        let texto = '';

        items.forEach(item => {
          texto += (item.textContent || '').toLowerCase() + ' ';
        });

        fila.style.display = texto.includes(filtro) ? '' : 'none';
      });
      const contenedorScroll = document.querySelector('.perfect-scrollbar');
      if (contenedorScroll) {
        contenedorScroll.scrollTop = 0;
      }

    });
  });
}

// Dropzone.autoDiscover = false;

function buildDropzone(dropzoneList) {
  const previewTemplate = `
    <div class="dz-preview dz-file-preview">
      <div class="dz-details">
        <div class="dz-thumbnail">
          <img data-dz-thumbnail>

          <span class="dz-nopreview">
            Sin vista previa
          </span>

          <div class="dz-success-mark"></div>
          <div class="dz-error-mark"></div>

          <div class="dz-error-message">
            <span data-dz-errormessage></span>
          </div>

          <div class="progress">
            <div
              class="progress-bar progress-bar-primary"
              role="progressbar"
              aria-valuemin="0"
              aria-valuemax="100"
              data-dz-uploadprogress
            ></div>
          </div>
        </div>

        <div class="dz-filename" data-dz-name></div>
        <div class="dz-size" data-dz-size></div>
      </div>
    </div>
  `;

  dropzoneList.forEach(dropzone => {
    const formulario = dropzone.closest('form');

    const inputSelector = dropzone.getAttribute('data-dropzone-input');
    const inputFile = document.querySelector(inputSelector);

    const maxFiles = parseInt(dropzone.getAttribute('data-dropzone-max'), 10) || 1;

    const acceptedFiles = dropzone.getAttribute('data-dropzone-accepted') || 'image/*';

    const paramName = dropzone.getAttribute('data-dropzone-paramname') || 'file';

    if (!inputSelector || !inputFile) {
      console.error('Dropzone no pudo encontrar su input asociado:', inputSelector, dropzone);
      return;
    }

    const instancia = new Dropzone(dropzone, {
      url: '#',
      autoProcessQueue: true,

      previewTemplate: previewTemplate,
      maxFiles: maxFiles,
      maxFilesize: 5, // MB
      addRemoveLinks: true,
      acceptedFiles: acceptedFiles,

      parallelUploads: 1,
      paramName: paramName,

      dictRemoveFile: 'Eliminar',
      dictMaxFilesExceeded: ('Superaste el máximo de archivos permitidos.'),
      dictInvalidFileType: ('Formato de imagen no permitido.'),
      dictFileTooBig: ('La imagen no puede superar los 5 MB.'),

      init: function () {
        const dropzoneActual = this;

        function sincronizarInput() {
          const dataTransfer = new DataTransfer();

          dropzoneActual.files
            .filter(file => file.accepted !== false)
            .slice(0, maxFiles)
            .forEach(file => {
              dataTransfer.items.add(file);
            });

          inputFile.files = dataTransfer.files;
        }

        this.on('addedfile', function (file) {
        
          if (maxFiles === 1 && this.files.length > 1) {
            this.files
              .filter(item => item !== file)
              .forEach(item => {
                this.removeFile(item);
              });
          }

          queueMicrotask(sincronizarInput);
        });

        this.on('removedfile', function () {
          queueMicrotask(sincronizarInput);
        });

        this.on('error', function (file) {
          if (file.accepted === false) {
            this.removeFile(file);
          }

          queueMicrotask(sincronizarInput);
        });
      }
    });
    dropzone.dropzoneInstance = instancia;
  });
}