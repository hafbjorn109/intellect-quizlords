document.addEventListener('DOMContentLoaded', async () => {

    const token = localStorage.getItem('adminToken');

    if (!token) {
        window.location.href = '/admin-login';
    } else {
        try {
            const res = await fetch('/admin/auth/verify', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!res.ok) {
                window.location.href = '/admin-login';
            }
        } catch (err) {
            console.error('Token verification error:', err);
        }
    }

    // Handles switching between admin views and rendering the appropriate form/view.
    async function showView(viewName) {
        const container = document.getElementById('admin-content');
        container.innerHTML = '';

        switch (viewName) {
            case 'add-category':
                await renderAddCategoryForm(container);
                break;
            case 'add-question':
                await renderAddQuestionForm(container);
                break;
            case 'edit-categories':
                await renderEditCategoriesView(container);
                break;
            case 'edit-questions':
                await renderEditQuestionsView(container);
                break;
            default:
                container.innerHTML = '<p>Unknown view selected</p>'
        }
    }

    // Renders the form for adding a new category.
    async function renderAddCategoryForm(container) {
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
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + localStorage.getItem('adminToken')
                    },
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

    // Renders the form for adding a new question and associated answers.
    async function renderAddQuestionForm(container) {
        const form = document.createElement('form');
        form.innerHTML = `
            <h2>Add new question</h2>
            <input type="text" id="question-text" placeholder="Question" required class="block">
    
            <label for="question-category">Category:</label>
            <select id="question-category" required class="block">
                <option value="">-- choose --</option>
            </select>
    
            <div id="answers-container" class="block">
                <h4>Answers:</h4>
            </div>
    
            <button type="button" id="add-answer-btn"> Add answer</button>
            <br><br>
            <button type="submit">Save Question</button>
            <p id="question-msg"></p>
        `;

        container.appendChild(form);

        await loadCategoriesToSelect(document.getElementById('question-category'));

        document.getElementById('add-answer-btn').onclick = () => {
            addAnswerInput(document.getElementById('answers-container'));
        }

        addAnswerInput(document.getElementById('answers-container'));
        addAnswerInput(document.getElementById('answers-container'));

        form.onsubmit = async (e) => {
            e.preventDefault();
            const msg = document.getElementById('question-msg');
            msg.textContent = '';
            msg.style.color = 'red';

            const text = document.getElementById('question-text').value.trim();
            const categoryId = document.getElementById('question-category').value;
            const answers = Array.from(document.querySelectorAll('.answer-entry')).map(entry => {
                return {
                    text: entry.querySelector('.answer-text').value.trim(),
                    is_correct: entry.querySelector('.answer-correct').checked
                };
            });

            if (!text || !categoryId) {
                msg.textContent = 'Question and category are required.';
                return;
            }

            const validAnswers = answers.filter(a => a.text);
            const correctAnswers = validAnswers.filter(a => a.is_correct);

            if (validAnswers.length < 2) {
                msg.textContent = 'At least 2 answers are required.';
                return;
            }

            if(correctAnswers.length !== 1) {
                msg.textContent = 'Check exactly one answer as correct.';
                return;
            }

            try {
                const questionRes = await fetch('/questions/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + localStorage.getItem('adminToken')
                    },
                    body: JSON.stringify({ text, category_id: categoryId})
                });

                const questionData = await questionRes.json();
                if (!questionRes.ok) {
                    msg.textContent = questionData.error || 'Question not added.';
                    return;
                }

                const questionId = questionData.id;

                for (let answer of validAnswers) {
                    await fetch('/answers', {
                        method: 'POST',
                        headers: {
                                'Content-Type': 'application/json',
                                'Authorization': 'Bearer ' + localStorage.getItem('adminToken')
                            },
                        body: JSON.stringify({
                            text: answer.text,
                            is_correct: answer.is_correct,
                            question_id: questionId
                        })
                    });
                }

                msg.textContent = 'Question and answers added.';
                msg.style.color = 'green';
                form.reset();

                document.getElementById('answers-container').innerHTML = '';
                addAnswerInput(document.getElementById('answers-container'));
                addAnswerInput(document.getElementById('answers-container'));

            } catch (err) {
                console.error('Error', err)
            }
        }
    }

    // Loads available categories into a given <select> element.
    async function loadCategoriesToSelect(selectElement) {
        const res = await fetch('/categories/');
        const data = await res.json();

        selectElement.innerHTML = '<option value=""> -- choose -- </option>';
        data.forEach(cat => {
            const opt = document.createElement('option');
            opt.value = cat.id;
            opt.textContent = cat.name;
            selectElement.appendChild(opt);
        });
    }

    // Adds a new answer input row (text field + correct checkbox) to the given container.
    function addAnswerInput(container) {
        const div = document.createElement('div');
        div.classList.add('answer-entry');

        div.innerHTML = `
            <input type="text" class="answer-text" placeholder="Answer">
            <label><input type="checkbox" class="answer-correct"> Correct</label>
            <button type="button" onclick="this.parentElement.remove()"> Delete </button>
        `;

        container.appendChild(div);
    }

    // Renders the view for editing existing categories (rename and delete).
    async function renderEditCategoriesView(container) {
        const heading = document.createElement('h2');
        container.appendChild(heading);

        const list = document.createElement('ul');
        list.id = 'edit-category-list';
        container.appendChild(list);

        try {
            const res = await fetch('/categories/');
            const categories = await res.json();

            if (!Array.isArray(categories)) {
                list.innerHTML = '<li>Categories not loaded.</li>'
                return;
            }

            categories.forEach(cat => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <span class='category-name'> ${cat.name} </span>
                    <button class='edit-btn'> Edit </button>
                    <button class='delete-btn'> Delete </button>
                `;

                li.querySelector('.edit-btn').onclick = () => {
                    const span = li.querySelector('.category-name');
                    const oldName = span.textContent.trim();

                    const input = document.createElement('input');
                    input.value = oldName;
                    input.classList.add('category-input');

                    const saveBtn = document.createElement('button');
                    saveBtn.textContent = 'Save';

                    span.replaceWith(input);

                    const editBtn = li.querySelector('.edit-btn');
                    editBtn.replaceWith(saveBtn);

                    saveBtn.onclick = async () => {
                        const newName = input.value.trim();
                        if (!newName) return alert('Name can not be empty!');

                        const response = await fetch(`/categories/${cat.id}`, {
                            method: 'PUT',
                            headers: {
                                'Content-Type': 'application/json',
                                'Authorization': 'Bearer ' + localStorage.getItem('adminToken')
                            },
                            body: JSON.stringify({ name: newName })
                        });

                        if (response.ok) {
                            await showView('edit-categories');
                        } else {
                            alert('Edit failed.');
                        }
                    };
                };

                li.querySelector('.delete-btn').onclick = async () => {
                    if (!confirm(`Are you sure you want to delete category ${cat.name}?`)) return;

                    const response = await fetch(`/categories/${cat.id}`, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': 'Bearer ' + localStorage.getItem('adminToken')
                        },
                    });

                    if (response.ok) {
                        li.remove();
                    } else {
                        alert ('Category not deleted correctly.');
                    }
                };

                list.appendChild(li);
            });

            if (categories.length === 0){
                list.innerHTML = '<li>No categories</li>'
            }

        } catch (err) {
            console.error('Error:', err);
        }
    }

    // Renders the view for editing existing questions and their answers.
    async function renderEditQuestionsView(container) {
        const heading = document.createElement('h2');
        heading.textContent = 'Edit questions';
        container.appendChild(heading);

        const categorySelect = document.createElement('select');
        categorySelect.innerHTML = '<option value=""> -- choose category -- </option>';
        container.appendChild(categorySelect);

        const questionList = document.createElement('ul');
        container.appendChild(questionList);

        const res = await fetch('/categories/');
        const categories = await res.json();

        categories.forEach(cat => {
            const opt = document.createElement('option');
            opt.value = cat.id;
            opt.textContent = cat.name;
            categorySelect.appendChild(opt);
        });

        categorySelect.onchange = async () => {
            const selectedId = parseInt(categorySelect.value);
            questionList.innerHTML = '';

            if (!selectedId) return;

            try {
                const res = await fetch('/questions/');
                const questions = await res.json();

                const filtered = questions.filter(q => q.category_id === selectedId);

                if (filtered.length === 0) {
                    questionList.innerHTML = '<li> No questions in this category </li>';
                    return;
                }

                filtered.forEach(q => {
                    const li = document.createElement('li');
                    li.innerHTML = `
                        <span class='question-text'>${q.text}</span>
                        <button class='edit-btn'>Edit</button>
                        <button class='delete-btn'>Delete</button>
                    `;

                    li.querySelector('.edit-btn').onclick = async () => {
                        const span = li.querySelector('.question-text');
                        const oldText = span.textContent.trim();


                        const input = document.createElement('input');
                        input.value = oldText;
                        span.replaceWith(input);

                        const saveBtn = document.createElement('button');
                        saveBtn.textContent = 'Save';

                        li.querySelector('.edit-btn').replaceWith(saveBtn);


                        const answerList = document.createElement('ul');
                        li.appendChild(answerList);


                        const res = await fetch('/answers/');
                        const allAnswers = await res.json();
                        const answers = allAnswers.filter(a => parseInt(a.question_id) === q.id);


                        const answerInputs = [];

                        answers.forEach(ans => {
                            const ansLi = document.createElement('li');
                            const ansInput = document.createElement('input');
                            ansInput.value = ans.text;

                            const ansCheck = document.createElement('input');
                            ansCheck.type = 'checkbox';
                            ansCheck.checked = ans.is_correct;

                            const deleteBtn = document.createElement('button');
                            deleteBtn.textContent = 'Delete';

                            ansLi.appendChild(ansInput);
                            ansLi.appendChild(ansCheck);
                            ansLi.appendChild(deleteBtn);
                            answerList.appendChild(ansLi);

                            answerInputs.push({
                                id: ans.id,
                                input: ansInput,
                                checkbox: ansCheck,
                                deleted: false
                            });

                            deleteBtn.onclick = () => {
                                ansLi.remove();
                                const target = answerInputs.find(a => a.id === ans.id);
                                if (target) target.deleted = true;
                            };
                        });


                        const newAnswerInput = document.createElement('input');
                        const newAnswerCheckbox = document.createElement('input');
                        newAnswerCheckbox.type = 'checkbox';
                        const addNewBtn = document.createElement('button');
                        addNewBtn.textContent = 'Add';

                        const newAnsLi = document.createElement('li');
                        newAnsLi.appendChild(newAnswerInput);
                        newAnsLi.appendChild(newAnswerCheckbox);
                        newAnsLi.appendChild(addNewBtn);
                        answerList.appendChild(newAnsLi);

                        const newAnswers = [];

                        addNewBtn.onclick = () => {
                            const text = newAnswerInput.value.trim();
                            const isCorrect = newAnswerCheckbox.checked;
                            if (!text) return alert('New answer text is empty.');


                            newAnswers.push({ text, is_correct: isCorrect });
                            const staticLi = document.createElement('li');
                            staticLi.textContent = `${text} ${isCorrect ? '(✓)' : ''}`;
                            answerList.insertBefore(staticLi, newAnsLi);


                            newAnswerInput.value = '';
                            newAnswerCheckbox.checked = false;
                        };


                        saveBtn.onclick = async () => {
                            const newText = input.value.trim();
                            if (!newText) return alert('Question text can not be empty.');

                            const correctCount =
                                answerInputs.filter(a => !a.deleted && a.checkbox.checked).length +
                                newAnswers.filter(a => a.is_correct).length;

                            if (correctCount !== 1) {
                                return alert('Pick one correct answer.');
                            }


                            await fetch(`/questions/${q.id}`, {
                                method: 'PUT',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'Authorization': 'Bearer ' + localStorage.getItem('adminToken')
                                },
                                body: JSON.stringify({ text: newText, category_id: selectedId })
                            });


                            for (let a of answerInputs) {
                                if (a.deleted) {
                                    await fetch(`/answers/${a.id}`, {
                                        method: 'DELETE' ,
                                        headers: {
                                            'Content-Type': 'application/json',
                                            'Authorization': 'Bearer ' + localStorage.getItem('adminToken')
                                        }
                                    });
                                } else {
                                    await fetch(`/answers/${a.id}`, {
                                        method: 'PUT',
                                        headers: {
                                            'Content-Type': 'application/json',
                                            'Authorization': 'Bearer ' + localStorage.getItem('adminToken')
                                        },
                                        body: JSON.stringify({
                                            text: a.input.value.trim(),
                                            is_correct: a.checkbox.checked,
                                            question_id: q.id
                                        })
                                    });
                                }
                            }


                            for (let a of newAnswers) {
                                await fetch(`/answers/`, {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json',
                                        'Authorization': 'Bearer ' + localStorage.getItem('adminToken')
                                    },
                                    body: JSON.stringify({
                                        text: a.text,
                                        is_correct: a.is_correct,
                                        question_id: q.id
                                    })
                                });
                            }

                            await showView('edit-questions');
                        };
                    };

                    li.querySelector('.delete-btn').onclick = async () => {
                        if(!confirm('Are you sure you want to delete this question?')) return;

                        const res = await fetch(`/questions/${q.id}`, {
                            method: 'DELETE',
                            headers: {
                                'Content-Type': 'application/json',
                                'Authorization': 'Bearer ' + localStorage.getItem('adminToken')
                            }
                        });

                        if (res.ok) {
                            li.remove();
                        } else {
                            alert('Question is not deleted.');
                        }
                    };

                    questionList.appendChild(li);
                });

            } catch (err) {
                questionList.innerHTML = '<li>Questions load error.</li>'
                console.error('Error:', err);
            }
        }
    }

    /**
     * Sends request to backend to delete all inactive sessions from the database.
     * Displays a confirmation dialog before proceeding.
     */
    async function flushSessions() {
        const msg = document.createElement('cleanup-msg');
        msg.textContent = '';

        if(!confirm('Are you sure you want to wipe out all of inactive sessions?')) return;

        try {
            const res = await fetch('/sessions/cleanup-sessions', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + localStorage.getItem('adminToken')
                }
            });

            const data = await res.json();

            if (res.ok) {
                msg.style.color = 'green';
                msg.textContent = data.message || 'Sessions deleted.';
            } else {
                msg.style.color = 'red';
                msg.textContent = data.error || 'Sessions cannot be deleted.'
            }

        } catch (err) {
            console.error('Error: ', err)
        }
    }

    // Logs out admin by removing token and redirecting to login page
    function logoutAdmin() {
        localStorage.removeItem('adminToken');
        window.location.href = '/admin-login';
    }

    window.logoutAdmin = logoutAdmin;
    window.showView = showView;
    window.flushSessions = flushSessions;
})