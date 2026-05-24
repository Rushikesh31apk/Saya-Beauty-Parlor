// Dashboard charts and invoice calculation.
document.addEventListener('DOMContentLoaded', () => {
  const chart = (id, type = 'bar') => {
    const el = document.getElementById(id);
    if (!el || typeof Chart === 'undefined') return;
    const labels = JSON.parse(el.dataset.labels || '[]');
    const values = JSON.parse(el.dataset.values || '[]');
    new Chart(el, { type, data: { labels, datasets: [{ label: 'Total', data: values }] }, options: { responsive: true, plugins: { legend: { display: false } } } });
  };
  chart('revenueChart', 'line');
  chart('statusChart', 'doughnut');
  chart('serviceReport', 'bar');
  chart('modeReport', 'doughnut');

  const billForm = document.getElementById('billForm');
  if (billForm) {
    const fields = billForm.querySelectorAll('.bill-field');
    const output = document.getElementById('finalAmount');
    const calc = () => {
      const price = parseFloat(billForm.service_price.value || 0);
      const extra = parseFloat(billForm.extra_charges.value || 0);
      const discount = parseFloat(billForm.discount.value || 0);
      const gst = parseFloat(billForm.gst.value || 0);
      const subtotal = price + extra - discount;
      output.value = '₹' + (subtotal + (subtotal * gst / 100)).toFixed(2);
    };
    fields.forEach(f => f.addEventListener('input', calc));
    calc();
  }
});
