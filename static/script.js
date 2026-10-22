/**
 * Student Task Management System - Client-side Interactive Logic
 */

document.addEventListener('DOMContentLoaded', function () {
    // ==========================================
    // 1. Mobile Sidebar Drawer Logic
    // ==========================================
    const sidebar = document.getElementById('sidebar');
    const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
    const sidebarCloseBtn = document.getElementById('sidebarCloseBtn');
    const sidebarOverlay = document.getElementById('sidebarOverlay');

    function openSidebar() {
        if (sidebar && sidebarOverlay) {
            sidebar.classList.add('open');
            sidebarOverlay.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    }

    function closeSidebar() {
        if (sidebar && sidebarOverlay) {
            sidebar.classList.remove('open');
            sidebarOverlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    if (sidebarToggleBtn) {
        sidebarToggleBtn.addEventListener('click', openSidebar);
    }

    if (sidebarCloseBtn) {
        sidebarCloseBtn.addEventListener('click', closeSidebar);
    }

    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', closeSidebar);
    }

    // ==========================================
    // 2. Delete Confirmation Modal
    // ==========================================
    const deleteModal = document.getElementById('deleteModal');
    const deleteTaskForm = document.getElementById('deleteTaskForm');
    const deleteTaskTitle = document.getElementById('deleteTaskTitle');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');

    // Attach click event to all delete buttons
    const deleteButtons = document.querySelectorAll('.open-delete-modal');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const taskId = this.getAttribute('data-task-id');
            const taskTitle = this.getAttribute('data-task-title') || 'this task';

            if (deleteTaskForm && deleteTaskTitle && deleteModal) {
                // Set the form submission URL for deleting this specific task
                deleteTaskForm.action = `/tasks/delete/${taskId}`;
                deleteTaskTitle.textContent = `"${taskTitle}"`;
                deleteModal.classList.add('show');
                deleteModal.setAttribute('aria-hidden', 'false');
            }
        });
    });

    function closeDeleteModal() {
        if (deleteModal) {
            deleteModal.classList.remove('show');
            deleteModal.setAttribute('aria-hidden', 'true');
        }
    }

    if (cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener('click', closeDeleteModal);
    }

    // Close modal when clicking outside of modal card
    if (deleteModal) {
        deleteModal.addEventListener('click', function (e) {
            if (e.target === deleteModal) {
                closeDeleteModal();
            }
        });
    }

    // Close modal on Escape key press
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && deleteModal && deleteModal.classList.contains('show')) {
            closeDeleteModal();
        }
    });

    // ==========================================
    // 3. Flash Alerts Auto-Dismiss (after 5 seconds)
    // ==========================================
    const flashAlerts = document.querySelectorAll('.flash-alert');
    flashAlerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-6px)';
            setTimeout(() => {
                alert.remove();
            }, 400);
        }, 5000);
    });

    // ==========================================
    // 4. Client-side Form Validation
    // ==========================================
    const forms = document.querySelectorAll('form.task-form');
    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            const titleInput = form.querySelector('input[name="title"]');
            const dateInput = form.querySelector('input[name="due_date"]');

            let isValid = true;

            if (titleInput && titleInput.value.trim() === '') {
                isValid = false;
                titleInput.focus();
                titleInput.style.borderColor = 'var(--danger)';
            } else if (titleInput) {
                titleInput.style.borderColor = '';
            }

            if (dateInput && dateInput.value.trim() === '') {
                if (isValid) {
                    dateInput.focus();
                }
                isValid = false;
                dateInput.style.borderColor = 'var(--danger)';
            } else if (dateInput) {
                dateInput.style.borderColor = '';
            }

            if (!isValid) {
                e.preventDefault();
            }
        });
    });
});
