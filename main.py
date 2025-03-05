import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

# Пример данных (замените на реальные логи)
data = [
    {
        "Выбранная роль": "Студент",
        "Кампус": "Нижний Новгород",
        "Уровень образования": "Бакалавриат",
        "Категория вопроса": "Учебный процесс",
        "Время ответа модели": 3.294378,
        "user_filters": ["Нижний Новгород", "бакалавриат"],
        "question_filters": ["Учебный процесс", "Практическая подготовка"],
        "chat_history": {
            "old_contexts": ["Пример текста контекста"],
            "old_questions": ["Когда пересдача?"],
            "old_answers": ["Пересдача пройдет в сентябре."]
        }
    },
    # Добавьте больше данных для тестирования
]

# Создаем DataFrame
df = pd.DataFrame(data)

# Инициализация Dash-приложения
app = dash.Dash(name)

# Лейаут дашборда
app.layout = html.Div([
    html.H1("Аналитика модели и бота"),

    # Распределение по кампусам
    html.H2("Распределение запросов по кампусам"),
    dcc.Graph(id='campus-distribution'),

    # Разбивка по уровням образования
    html.H2("Распределение запросов по уровням образования"),
    dcc.Graph(id='education-level-distribution'),

    # Категории вопросов
    html.H2("Распределение запросов по категориям вопросов"),
    dcc.Graph(id='question-category-distribution'),

    # Среднее время ответа модели
    html.H2("Среднее время ответа модели"),
    dcc.Graph(id='average-response-time'),

    # Частота пустых/непустых chat_history
    html.H2("Частота пустых и непустых chat_history"),
    dcc.Graph(id='chat-history-distribution'),
])

# Callback для обновления графиков
@app.callback(
    [Output('campus-distribution', 'figure'),
     Output('education-level-distribution', 'figure'),
     Output('question-category-distribution', 'figure'),
     Output('average-response-time', 'figure'),
     Output('chat-history-distribution', 'figure')],
    [Input('campus-distribution', 'id')]  # Просто триггер, можно заменить на реальный Input
)
def update_graphs(_):
    # Распределение по кампусам
    campus_distribution = df['Кампус'].value_counts().reset_index()
    campus_distribution.columns = ['Кампус', 'Количество запросов']
    fig1 = px.bar(campus_distribution, x='Кампус', y='Количество запросов', title="Распределение по кампусам")

    # Разбивка по уровням образования
    education_distribution = df['Уровень образования'].value_counts().reset_index()
    education_distribution.columns = ['Уровень образования', 'Количество запросов']
    fig2 = px.bar(education_distribution, x='Уровень образования', y='Количество запросов', title="Распределение по уровням образования")

    # Категории вопросов
    question_distribution = df['Категория вопроса'].value_counts().reset_index()
    question_distribution.columns = ['Категория вопроса', 'Количество запросов']
    fig3 = px.bar(question_distribution, x='Категория вопроса', y='Количество запросов', title="Распределение по категориям вопросов")

    # Среднее время ответа модели
    avg_response_time = df['Время ответа модели'].mean()
    fig4 = px.bar(x=['Среднее время ответа'], y=[avg_response_time], title=f"Среднее время ответа: {avg_response_time:.2f} сек")

    # Частота пустых/непустых chat_history
    empty_chat_history = df['chat_history'].apply(lambda x: not x['old_questions']).sum()
    non_empty_chat_history = len(df) - empty_chat_history
    chat_history_distribution = pd.DataFrame({
        'Тип': ['Пустой chat_history', 'Непустой chat_history'],
        'Количество': [empty_chat_history, non_empty_chat_history]
    })
    fig5 = px.bar(chat_history_distribution, x='Тип', y='Количество', title="Частота пустых и непустых chat_history")

    return fig1, fig2, fig3, fig4, fig5

# Запуск приложения
if name == 'main':
    app.run_server(debug=True)