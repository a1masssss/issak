document.addEventListener('DOMContentLoaded', function() {
    // Prevent dropdown from closing when clicking inside it
    const dropdownMenu = document.querySelector('.dropdown-menu');
    if (dropdownMenu) {
        dropdownMenu.addEventListener('click', function(e) {
            if (!e.target.closest('form[action]') && !e.target.closest('.should-close-dropdown')) {
                e.stopPropagation(); // Prevent dropdown from closing
            }
        });
    }

    // Prevent dropdown from closing when switching tabs inside the profile dropdown
    const profileDropdownTabs = document.querySelectorAll("#profileDropdownTab button");
    profileDropdownTabs.forEach(tab => {
        tab.addEventListener("click", function(e) {
            e.preventDefault();  // Prevent default link behavior
            e.stopPropagation(); // Prevent dropdown from closing

            // Activate clicked tab
            profileDropdownTabs.forEach(t => t.classList.remove("active"));
            this.classList.add("active");

            // Hide all tab panes inside profile dropdown
            document.querySelectorAll(".tab-content .tab-pane").forEach(pane => pane.classList.remove("show", "active"));

            // Show the selected tab
            const targetPane = document.querySelector(this.getAttribute("data-bs-target"));
            if (targetPane) {
                targetPane.classList.add("show", "active");
            }
        });
    });

    // Ensure Bootstrap initializes profile dropdown tabs correctly
    let tabElements = document.querySelectorAll('#profileDropdownTab [data-bs-toggle="tab"]');
    tabElements.forEach(tab => {
        new bootstrap.Tab(tab);
    });

    // Handle profile form submission via AJAX
    const profileForm = document.getElementById('profileEditForm');
    if (profileForm) {
        profileForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch(this.action, {
                method: 'POST',
                body: new FormData(this),
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrftoken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'alert alert-success';
                    alertDiv.style.position = 'fixed';
                    alertDiv.style.top = '20px';
                    alertDiv.style.right = '20px';
                    alertDiv.style.zIndex = '9999';
                    alertDiv.style.padding = '10px 20px';
                    alertDiv.textContent = data.message || 'Profile updated successfully';
                    document.body.appendChild(alertDiv);

                    // Reload the page after a delay
                    setTimeout(() => {
                        window.location.reload();
                    }, 1500);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                // Show error alert
                const alertDiv = document.createElement('div');
                alertDiv.className = 'alert alert-danger';
                alertDiv.style.position = 'fixed';
                alertDiv.style.top = '20px';
                alertDiv.style.right = '20px';
                alertDiv.style.zIndex = '9999';
                alertDiv.textContent = 'Error updating profile';
                document.body.appendChild(alertDiv);
                setTimeout(() => alertDiv.remove(), 3000);
            });
        });
    }
});