document.addEventListener('DOMContentLoaded', () => {

    function showView(viewName) {
        const container = document.getElementById('admin-content');
        container.innerHTML = '';

        switch (viewName) {
            case 'add-category':
                renderAddCategoryForm(container);
                break;
            case 'add-question':
                renderAddQuestionForm(container);
                break;
            case 'edit-categories':
                renderEditCategoriesVieW(container);
                break;
            case 'edit-questions':
                renderEditQuestionsView(container);
                break;
            default:
                container.innerHTML = '<p>Unknown view selected</p>'
        }
    }

    function renderAddCategoryForm(container) {
        const form = document.createElement('form');
        form.innerHTML = `
            <h2>Add new category</h2>
            <input type="text" id="new-category-name" placeholder="Category name" required>
            <button type="submit">Save</button>
            <p id="category-msg"></p>
        `;

        form.onsubmit = async (e) => {
            e.preventDefault();
            const name = document.getElementById('new-category-name').value.trim();
            const msg = document.getElementById('category-msg');

            if (!name) {
                msg.textContent = 'Category name can not be empty';
                msg.style.color = 'red';
                return;
            }

            try {
                const res = await fetch('/categories/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name })
                });
                const data = await res.json();

                if (!res.ok) {
                    msg.textContent = data.error || 'Category not added.'
                    msg.style.color = 'red';
                    return;
                }

                msg.textContent = `Category added: ${data.name}`
                msg.style.color = 'green';
                form.reset();

            } catch (err) {
                console.error('Error:', err)
            }
        }
        container.appendChild(form);
    }

    window.showView = showView;

})