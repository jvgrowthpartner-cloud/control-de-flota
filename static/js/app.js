// Auto-uppercase patente input
document.querySelectorAll('input[name="patente"]').forEach(el => {
  el.addEventListener('input', function () {
    this.value = this.value.toUpperCase();
  });
});
