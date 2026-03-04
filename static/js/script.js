document.getElementById('resume').addEventListener('change', function() {
    const fileName = this.files[0] ? this.files[0].name : "No file selected";
    document.getElementById('file-name').textContent = fileName;
});

document.addEventListener('DOMContentLoaded', function() {
    const startDateInput = document.querySelector('input[name="visit_start_date"]');
    const endDateInput = document.querySelector('input[name="visit_end_date"]');
    
    if (startDateInput && endDateInput) {
        startDateInput.addEventListener('change', function() {
            endDateInput.min = this.value;
            if (endDateInput.value && endDateInput.value < this.value) {
                endDateInput.value = this.value;
            }
        });
        
        endDateInput.addEventListener('change', function() {
            if (this.value < startDateInput.value) {
                this.value = startDateInput.value;
            }
        });
    }
});

