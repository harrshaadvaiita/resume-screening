document.addEventListener('DOMContentLoaded', function() {
    // Flash message handling - only show latest message
    const alerts = document.querySelectorAll('.alert');
    if (alerts.length > 0) {
        // Keep only the latest alert
        const latestAlert = alerts[alerts.length - 1];
        alerts.forEach(alert => {
            if (alert !== latestAlert) {
                alert.remove();
            }
        });

        // Auto-dismiss the latest alert
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(latestAlert);
            bsAlert.close();
        }, 3000);
    }

    // Form submission handling
    const candidateForm = document.getElementById('candidateForm');
    if (candidateForm) {
        candidateForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Clear any existing alerts
            document.querySelectorAll('.alert').forEach(alert => alert.remove());
            
            const fileInput = document.getElementById('resume');
            const file = fileInput.files[0];
            
            // Validate file
            if (file) {
                if (file.size > 16 * 1024 * 1024) {
                    showAlert('File size must be less than 16MB', 'danger');
                    return;
                }
                
                const allowedTypes = ['.pdf', '.docx'];
                const fileExt = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
                if (!allowedTypes.includes(fileExt)) {
                    showAlert('Please upload only PDF or DOCX files', 'danger');
                    return;
                }
            }
            
            // Disable submit button
            document.getElementById('submitBtn').disabled = true;
            
            try {
                const formData = new FormData(candidateForm);
                const response = await fetch(candidateForm.action, {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    showAlert('Application submitted successfully!', 'success');
                    candidateForm.reset();
                    setTimeout(() => {
                        window.location.href = '/';  // Redirect to home after success
                    }, 2000);
                } else {
                    throw new Error('Submission failed');
                }
            } catch (error) {
                showAlert('Error submitting application. Please try again.', 'danger');
            } finally {
                document.getElementById('submitBtn').disabled = false;
            }
        });
    }

    // Table row hover effect
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', () => {
            row.classList.add('table-hover-effect');
        });
        row.addEventListener('mouseleave', () => {
            row.classList.remove('table-hover-effect');
        });
    });

    // Score badge animation
    const scoreBadges = document.querySelectorAll('.badge');
    scoreBadges.forEach(badge => {
        badge.addEventListener('mouseenter', () => {
            badge.style.transform = 'scale(1.1)';
        });
        badge.addEventListener('mouseleave', () => {
            badge.style.transform = 'scale(1)';
        });
    });
});

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const cardBody = document.querySelector('.card-body');
    const form = document.getElementById('candidateForm');
    cardBody.insertBefore(alertDiv, form);

    if (type === 'success') {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }, 2000);
    }
}
