import streamlit as st
import pandas as pd
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
import plotly.graph_objs as go

# Função para obter os últimos 10 jogos de um jogador
def get_player_stats(player_name):
    player_dict = players.find_players_by_full_name(player_name)[0]
    player_id = player_dict['id']
    game_log = playergamelog.PlayerGameLog(player_id=player_id, season='2023').get_data_frames()[0]
    last_10_games = game_log.head(10)
    return last_10_games

# Função para criar gráficos de barras
def create_bar_chart(data, avg, median, title, yaxis_title, color):
    return {
        'data': [
            go.Bar(x=dates, y=data, name=title, marker={'color': color}),
            go.Scatter(x=dates, y=[avg]*len(data), mode='lines', name=f'Média de {title}', line={'color': 'red'}),
            go.Scatter(x=dates, y=[median]*len(data), mode='lines', name=f'Mediana de {title}', line={'color': 'blue', 'dash': 'dash'})
        ],
        'layout': go.Layout(
            title=f'Últimos 10 Jogos - {title} de {player_name}',
            xaxis={'title': 'Data'},
            yaxis={'title': yaxis_title}
        )
    }

# Função para criar gráficos de pizza
def create_pie_chart(data, avg, title):
    above_avg = (data >= avg).sum()
    below_avg = (data < avg).sum()
    return {
        'data': [
            go.Pie(labels=['Acima da Média', 'Abaixo da Média'], 
                   values=[above_avg, below_avg], 
                   name=title)
        ],
        'layout': go.Layout(
            title=f'{title} - Acima/Abaixo da Média'
        )
    }

# Configurando a página no Streamlit
st.set_page_config(page_title='NBA Player Performance Dashboard', layout='wide')
st.title('NBA Player Performance Dashboard')

# Dropdown para selecionar o jogador
player_name = st.selectbox('Escolha o jogador', [player['full_name'] for player in players.get_active_players()])

# Obtenha os dados do jogador selecionado
df = get_player_stats(player_name)
points = df['PTS']
assists = df['AST']
rebounds = df['REB']
dates = pd.to_datetime(df['GAME_DATE'])

# Crie os gráficos de barras
points_figure = create_bar_chart(points, points.mean(), points.median(), 'Pontos', 'Pontos', '#1d428a')
assists_figure = create_bar_chart(assists, assists.mean(), assists.median(), 'Assistências', 'Assistências', '#ff6347')
rebounds_figure = create_bar_chart(rebounds, rebounds.mean(), rebounds.median(), 'Rebotes', 'Rebotes', '#32cd32')

# Crie os gráficos de pizza
points_pie = create_pie_chart(points, points.mean(), 'Pontos')
assists_pie = create_pie_chart(assists, assists.mean(), 'Assistências')
rebounds_pie = create_pie_chart(rebounds, rebounds.mean(), 'Rebotes')

# Exiba os gráficos no Streamlit
col1, col2, col3 = st.columns(3)
with col1:
    st.plotly_chart(points_figure)
    st.plotly_chart(points_pie)
with col2:
    st.plotly_chart(assists_figure)
    st.plotly_chart(assists_pie)
with col3:
    st.plotly_chart(rebounds_figure)
    st.plotly_chart(rebounds_pie)

# Botão para exportar os dados para Excel
if st.button('Exportar para Excel'):
    df.to_excel(f'{player_name}_last_10_games.xlsx')
    st.success('Dados exportados com sucesso!')
