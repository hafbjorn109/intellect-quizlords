document.addEventListener('DOMContentLoaded', () => {

    async function showView(viewName) {
        const container = document.getElementById('admin-content');
        container.innerHTML = '';

        switch (viewName) {
            case 'add-category':
                renderAddCategoryForm(container);
                break;
            case 'add-question':
                await renderAddQuestionForm(container);
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
                    headers: { 'Content-Type': 'application/json' },
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
                        headers: { 'Content-Type': 'application/json' },
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

    function addAnswerInput(container) {
        const div = document.createElement('div');
        div.classList.add('answer-entry');

        div.innerHTML = `
            <input type="text" class="answer-text" placeholder="Answer">
            <label><input type="checkbox" class="answer-correct"> Correct</label>
            <button type="button" onclick="this.parentElement.remove()">❌</button>
        `;

        container.appendChild(div);
    }

    window.showView = showView;

})