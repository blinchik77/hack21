import pandas as pd
import dash
from dash import dcc, html, Output, Input
import plotly.express as px
import json
import dash_bootstrap_components as dbc
# парс джисона
with open('train_set.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
# сощздаем датафрейм
df = pd.DataFrame(data)
#создаем сам дашборд
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
#лейаут дашборда
app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("жесткий анализ года 2025", className="text-center my-4"))),
    # фильтр по кампусам
    dbc.Row([
        dbc.Col(html.Label("Выберите кампус:"), width=6),
        dbc.Col(dcc.Dropdown(
            id='campus-filter',
            options=[{'label': campus, 'value': campus} for campus in df['Кампус'].unique()],
            multi=True,  # можно сразу несколько фильтров
            placeholder="Все кампусы"
        ), width=6),
    ]),
    #по вопросам
    dbc.Row([
        dbc.Col(html.Label("Выберите категорию вопроса:"), width=6),
        dbc.Col(dcc.Dropdown(
            id='category-filter',
            options=[{'label': category, 'value': category} for category in df['Категория вопроса'].unique()],
            multi=True,  # можно сразу несколько фильтров
            placeholder="Все категории"
        ), width=6),
    ]),
    dbc.Row([
        dbc.Col(html.Div(id='total-requests', className="text-center h4"), width=4),
        dbc.Col(html.Div(id='average-response-time', className="text-center h4"), width=4),
        dbc.Col(html.Div(id='satisfaction-rate', className="text-center h4"), width=4),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='campus-distribution'), width=6),
        dbc.Col(dcc.Graph(id='education-level-distribution'), width=6),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='question-category-distribution'), width=6),
        dbc.Col(dcc.Graph(id='response-time-distribution'), width=6),
    ]),
    dbc.Row(dbc.Col(dcc.Graph(id='satisfaction-metrics'), width=12)),

    dcc.Interval( # обновляем резы каждые 10 сек, на случай если получиться что-нибудь подключить
        id='interval-component',
        interval=10 * 1000,
        n_intervals=0
    ),
], fluid=True)
# сам коллбэк
@app.callback(
    [Output('campus-distribution', 'figure'),
     Output('education-level-distribution', 'figure'),
     Output('question-category-distribution', 'figure'),
     Output('response-time-distribution', 'figure'),
     Output('satisfaction-metrics', 'figure'),
     Output('total-requests', 'children'),
     Output('average-response-time', 'children'),
     Output('satisfaction-rate', 'children')],
    [Input('interval-component', 'n_intervals'),
     Input('campus-filter', 'value'),  # тут фильтры
     Input('category-filter', 'value')]
)
def update_graphs(_, selected_campuses, selected_categories):
    # реализация фильтрации
    filtered_df = df.copy()
    if selected_campuses:
        filtered_df = filtered_df[filtered_df['Кампус'].isin(selected_campuses)]
    if selected_categories:
        filtered_df = filtered_df[filtered_df['Категория вопроса'].isin(selected_categories)]
    #разбивка по кампусам
    if 'Кампус' in filtered_df.columns:
        campus_distribution = filtered_df['Кампус'].value_counts().reset_index()
        campus_distribution.columns = ['Кампус', 'Количество запросов']
        fig1 = px.pie(campus_distribution, names='Кампус', values='Количество запросов',
                      title="Распределение запросов по кампусам")
    else:
        fig1 = px.bar(title="Нет данных о кампусах")
    #разбивка по степени обучения
    if 'Уровень образования' in filtered_df.columns:
        education_distribution = filtered_df['Уровень образования'].value_counts().reset_index()
        education_distribution.columns = ['Уровень образования', 'Количество запросов']
        fig2 = px.bar(education_distribution, x='Уровень образования', y='Количество запросов',
                      title="Распределение по уровням образования")
    else:
        fig2 = px.bar(title="Нет данных об уровне образования")

    #разбивка по категории вопросов
    if 'Категория вопроса' in filtered_df.columns:
        question_distribution = filtered_df['Категория вопроса'].value_counts().reset_index()
        question_distribution.columns = ['Категория вопроса', 'Количество запросов']
        fig3 = px.bar(question_distribution,
                      y='Категория вопроса',   x='Количество запросов',  title="Распределение по категориям вопросов",
                      orientation='h')
    else:
        fig3 = px.bar(title="Нет данных о категориях вопросов")

    # прикол про распределение по времени ответа ботом
    if 'Время ответа модели (сек)' in filtered_df.columns:
        bins = [0, 1, 2, 3, 4, 5, 10, 15, 20, float('inf')] # интервалы
        labels = ['<1 сек', '1-2 сек', '2-3 сек', '3-4 сек', '4-5 сек', '5-10 сек', '10-15 сек', '15-20 сек', '>20 сек']

        filtered_df['Время ответа категория'] = pd.cut(filtered_df['Время ответа модели (сек)'], bins=bins, labels=labels, right=False)

        response_time_distribution = filtered_df['Время ответа категория'].value_counts().reset_index()
        response_time_distribution.columns = ['Время ответа категория', 'Количество запросов']
        fig4 = px.bar(response_time_distribution, x='Время ответа категория', y='Количество запросов',
                      title="Распределение времени ответа модели")
    else:
        fig4 = px.bar(title="Нет данных о времени ответа модели")
    #удовлетворенность, подробнее в презе расскажем
    satisfied_count = filtered_df['Уточненный вопрос пользователя'].isna().sum()
    unsatisfied_count = filtered_df['Уточненный вопрос пользователя'].notna().sum()
    satisfaction_data = {
        'Состояние': ['Удовлетворённые', 'Неудовлетворённые'],
        'Количество': [satisfied_count, unsatisfied_count]
    }
    satisfaction_df = pd.DataFrame(satisfaction_data)
    fig5 = px.pie(satisfaction_df, names='Состояние', values='Количество', title="Метрика удовлетворенности ответами")

    # обновляем счетчики KPI
    total_requests = len(filtered_df)
    average_response_time = filtered_df['Время ответа модели (сек)'].mean() if 'Время ответа модели (сек)' in filtered_df.columns else 0
    satisfaction_rate = filtered_df['Уточненный вопрос пользователя'].isna().mean() * 100  # Процент удовлетворенных
    kpi_total_requests = f"всего запросов: {total_requests}"
    kpi_average_response_time = f"среднее время ответа: {average_response_time:.2f} сек"
    kpi_satisfaction_rate = f"% удовлетворённости: {satisfaction_rate:.2f}%"
    return fig1, fig2, fig3, fig4, fig5, kpi_total_requests, kpi_average_response_time, kpi_satisfaction_rate
# запуск
if __name__ == '__main__':
    app.run_server(debug=True)