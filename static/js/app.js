/* ==========================================================
   NeumoCRUD — JavaScript
   Buscador en vivo + modal de confirmación para eliminar
   ========================================================== */

document.addEventListener("DOMContentLoaded", () => {
  // ----------------------------------------------------------
  // Buscador en vivo
  // ----------------------------------------------------------
  const buscador = document.getElementById("buscador");
  const cuerpo = document.getElementById("cuerpo-tabla");
  const sinResultados = document.getElementById("sin-resultados");

  if (buscador && cuerpo) {
    buscador.addEventListener("input", () => {
      const texto = buscador.value.toLowerCase().trim();
      let visibles = 0;

      cuerpo.querySelectorAll("tr").forEach((fila) => {
        const coincide = fila.textContent.toLowerCase().includes(texto);
        fila.hidden = !coincide;
        if (coincide) visibles++;
      });

      if (sinResultados) sinResultados.hidden = visibles !== 0;
    });
  }

  // ----------------------------------------------------------
  // Modal de confirmación para eliminar
  // ----------------------------------------------------------
  const modal = document.getElementById("modalEliminar");
  const nombreEquipo = document.getElementById("modalNombreEquipo");
  const btnConfirmar = document.getElementById("btnConfirmarEliminar");
  const btnCancelar = document.getElementById("btnCancelarEliminar");
  let formularioPendiente = null;

  if (modal) {
    document.querySelectorAll(".form-eliminar").forEach((form) => {
      form.addEventListener("submit", (evento) => {
        evento.preventDefault();
        formularioPendiente = form;
        nombreEquipo.textContent = form.dataset.nombre || "este equipo";
        modal.hidden = false;
      });
    });

    btnConfirmar.addEventListener("click", () => {
      if (formularioPendiente) formularioPendiente.submit();
    });

    btnCancelar.addEventListener("click", () => {
      modal.hidden = true;
      formularioPendiente = null;
    });

    modal.addEventListener("click", (evento) => {
      if (evento.target === modal) {
        modal.hidden = true;
        formularioPendiente = null;
      }
    });
  }

  // ----------------------------------------------------------
  // Auto-ocultar mensajes flash tras 4 segundos
  // ----------------------------------------------------------
  document.querySelectorAll(".flash").forEach((flash) => {
    setTimeout(() => {
      flash.style.transition = "opacity 0.5s ease";
      flash.style.opacity = "0";
      setTimeout(() => flash.remove(), 500);
    }, 4000);
  });
});
