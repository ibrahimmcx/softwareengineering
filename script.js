document.addEventListener('DOMContentLoaded', () => {
    const app = document.getElementById('app');
    const nav = document.getElementById('doc-nav');
    let qaData = [];

    // Fetch the QA Data
    fetch('qa_data.json')
        .then(response => response.json())
        .then(data => {
            qaData = data;
            initApp();
        })
        .catch(err => {
            app.innerHTML = `<div class="loading"><i class="fas fa-exclamation-triangle" style="color: #ef4444; font-size: 3rem; margin-bottom: 1rem;"></i><br>Veri yüklenirken bir hata oluştu.</div>`;
            console.error('Error loading qa_data.json:', err);
        });

    function initApp() {
        if (qaData.length === 0) {
            app.innerHTML = `<div class="loading">Gösterilecek veri bulunamadı.</div>`;
            return;
        }

        // Render Navigation Buttons
        qaData.forEach((doc, index) => {
            const btn = document.createElement('button');
            btn.className = 'doc-btn';
            if (index === 0) btn.classList.add('active');
            
            // Clean up title for button
            let btnText = doc.title.replace('_Sorular', '').replace(/_/g, ' ');
            btn.textContent = btnText;
            
            btn.addEventListener('click', () => {
                document.querySelectorAll('.doc-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                renderDocument(index);
            });
            
            nav.appendChild(btn);
        });

        // Render first document by default
        renderDocument(0);
    }

    function renderDocument(docIndex) {
        const doc = qaData[docIndex];
        app.innerHTML = ''; // Clear current content
        
        // Use document fragment for performance
        const fragment = document.createDocumentFragment();

        doc.sections.forEach(section => {
            const sectionDiv = document.createElement('div');
            sectionDiv.className = 'section-container';

            // Section Header
            const secHeader = document.createElement('div');
            secHeader.className = 'section-header';
            
            const secTitle = document.createElement('h2');
            secTitle.className = 'section-title';
            secTitle.textContent = `BÖLÜM ${section.letter}: ${section.title}`;
            secHeader.appendChild(secTitle);

            if (section.instructions) {
                const secInst = document.createElement('p');
                secInst.className = 'section-instruction';
                secInst.textContent = section.instructions;
                secHeader.appendChild(secInst);
            }

            sectionDiv.appendChild(secHeader);

            const isMatching = section.title.toLowerCase().includes('eşleştirme');

            // Questions
            section.questions.forEach(q => {
                const qCard = document.createElement('div');
                qCard.className = 'question-card';

                const qHeader = document.createElement('div');
                qHeader.className = 'question-header';

                const qNum = document.createElement('div');
                qNum.className = 'question-number';
                qNum.textContent = q.number;

                const qText = document.createElement('div');
                qText.className = 'question-text';
                qText.textContent = q.text;

                qHeader.appendChild(qNum);
                qHeader.appendChild(qText);
                qCard.appendChild(qHeader);

                // Answer box
                if (q.answer) {
                    const ansBox = document.createElement('div');
                    ansBox.className = 'answer-box';
                    
                    const ansIcon = document.createElement('div');
                    ansIcon.className = 'answer-icon';
                    ansIcon.innerHTML = '<i class="fas fa-check-circle"></i>';

                    const ansText = document.createElement('div');
                    
                    let displayAnswer = q.answer;
                    if (isMatching) {
                        const letterToFind = q.answer.trim().toLowerCase();
                        let explanation = '';
                        for (const sq of section.questions) {
                            const lines = sq.text.split('\n');
                            for (const line of lines) {
                                const match = line.trim().match(new RegExp(`^${letterToFind}\\s*\\)\\s*(.*)`, 'i'));
                                if (match) {
                                    explanation = match[1];
                                    break;
                                }
                            }
                            if (explanation) break;
                        }
                        if (explanation) {
                            displayAnswer = `${q.answer.toUpperCase()}) ${explanation}`;
                        }
                    }
                    ansText.textContent = displayAnswer;

                    ansBox.appendChild(ansIcon);
                    ansBox.appendChild(ansText);
                    qCard.appendChild(ansBox);
                }

                sectionDiv.appendChild(qCard);
            });

            fragment.appendChild(sectionDiv);
        });

        app.appendChild(fragment);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
});
