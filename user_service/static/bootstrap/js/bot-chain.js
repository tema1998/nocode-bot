    document.addEventListener('DOMContentLoaded', function () {
        console.log('Chain JSON:', '{{ chain_json|escapejs }}');
        // Преобразуем JSON-строку в JavaScript-объект
        const chainData = JSON.parse('{{ chain_json|escapejs }}');

        // Заполняем информацию о цепочке
        document.getElementById('chain-name').textContent = chainData.name;
        document.getElementById('chain-id').textContent = chainData.id;

        // Подготовка данных для графа
        const nodes = [];
        const edges = [];

        // Рекурсивная функция для добавления шагов и кнопок
        function addStep(step, parentStepId = null) {
            if (!step) return;

            // Добавляем шаг как узел
            nodes.push({
                id: step.id,
                label: `Step ${step.id}\n${step.message}`,
                shape: 'box',
                color: '#D2E5FF',
            });

            // Если есть родительский шаг, добавляем связь
            if (parentStepId !== null) {
                edges.push({
                    from: parentStepId,
                    to: step.id,
                    arrows: 'to',
                    label: 'Next Step',
                });
            }

            // Добавляем кнопки и их связи
            if (step.buttons && step.buttons.length > 0) {
                step.buttons.forEach(button => {
                    if (button.next_step) {
                        edges.push({
                            from: step.id,
                            to: button.next_step.id,
                            arrows: 'to',
                            label: `Button: ${button.text}\nCallback: ${button.callback}`,
                        });
                        addStep(button.next_step, step.id);
                    }
                });
            }

            // Добавляем следующий шаг (если есть)
            if (step.next_step) {
                addStep(step.next_step, step.id);
            }
        }

        // Начинаем с первого шага
        addStep(chainData.first_step);

        // Создаем граф
        const container = document.getElementById('chain-graph');
        const data = {
            nodes: new vis.DataSet(nodes),
            edges: new vis.DataSet(edges),
        };
        const options = {
            layout: {
                hierarchical: {
                    direction: 'LR', // Слева направо
                    sortMethod: 'directed',
                },
            },
            edges: {
                font: {
                    size: 12,
                    align: 'middle',
                },
                arrows: {
                    to: { enabled: true, scaleFactor: 1 },
                },
            },
        };
        new vis.Network(container, data, options);
    });