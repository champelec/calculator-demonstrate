import streamlit as st
import pandas as pd
import plotly.express as px

# Настройка страницы
st.set_page_config(page_title="Медиа-калькулятор (Demo)", layout="wide")

# --- ДОБАВЛЕНИЕ КАРТИНОК В САЙДБАР ---
with st.sidebar:
    try:
        st.image("Logo1.png", use_container_width=True)
    except:
        pass
    
    st.markdown("### О проекте")
    st.info("Демо-версия медиа-калькулятора. Данные анонимизированы и искажены для публичной демонстрации.")
    
    try:
        st.image("Logo2.png", use_container_width=True)
    except:
        pass

def clean_percent_val(x):
    if isinstance(x, str):
        x = x.replace('%', '').replace(',', '.').strip()
        try:
            return float(x)
        except:
            return 0.0
    return float(x) if pd.notnull(x) else 0.0

@st.cache_data
def load_data():
    file_name = "Fake_Calculator_2026.xlsx"
    df = pd.read_excel(file_name, sheet_name="Данные")
    
    cols_to_fix = ['Digital', 'TV', 'Others offline', 'Smart TV', 'Видео',
                   'Мобайл (in-app)', 'Контекст', 'Программатик баннеры',
                   'Нативные баннеры', 'Соц.сети']
    
    for col in cols_to_fix:
        if col in df.columns:
            df[col] = df[col].apply(clean_percent_val)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Ошибка загрузки файла: {e}")
    st.stop()

# --- ИНТЕРФЕЙС: ВЕРХНЯЯ ЧАСТЬ ---
st.title("Медиа-калькулятор клиента")
st.markdown("---")

st.subheader("Параметры выбора")

c1, c2, c3 = st.columns(3)
with c1:
    geo = st.selectbox("ГЕО", sorted(df['ГЕО'].unique()))
    audience = st.selectbox("Целевая аудитория (ЦА)", sorted(df['ЦА'].unique()))
with c2:
    segments = st.selectbox("Наличие сегментов", sorted(df['Сегменты'].unique()), format_func=lambda x: str(x).capitalize())
    budget = st.selectbox("Бюджет (₽)", sorted(df['Бюджет до (₽)'].unique()))
with c3:
    competitors = st.selectbox("Активность конкурентного поля", sorted(df['Конкуренты'].unique()))
    period = st.selectbox("Сезональность РК", sorted(df['Сезональность РК'].unique()))

filtered = df[
    (df['ГЕО'] == geo) &
    (df['ЦА'] == audience) &
    (df['Сегменты'] == segments) &
    (df['Бюджет до (₽)'] == budget) &
    (df['Конкуренты'] == competitors) &
    (df['Сезональность РК'] == period)
]

st.divider()

# --- НИЖНЯЯ ЧАСТЬ: ВЫДАЧА ---
if not filtered.empty:
    res = filtered.iloc[0]
    
    st.subheader("Результаты расчета")
    
    m1, m2, m3, m4, m5 = st.columns(5)
    
    # 1. Емкость ЦА (всего)
    try:
        cap_val = f"{int(res['Емкость всего']):,}".replace(',', ' ')
    except:
        cap_val = str(res['Емкость всего'])
    m1.metric("Доступная емкость ЦА всего, чел", cap_val)

    # 2. Рекламная емкость (Digital)
    try:
        adv_cap_val = f"{int(res['Рекламная емкость']):,}".replace(',', ' ')
    except:
        adv_cap_val = str(res['Рекламная емкость'])
    m2.metric("Доступная емкость ЦА в Интернете, чел", adv_cap_val)
    
    # 3. Прогнозный охват (Исправлено)
    try:
        cov_val = f"{int(res['Прогнозный охват']):,}".replace(',', ' ')
    except:
        cov_val = str(res['Прогнозный охват'])
    m3.metric("Прогнозный охват ЦА за период РК, чел", cov_val)
    
    # 4. Охват в %
    m4.metric("Прогноз. охват на частоте 1+ на период РК, %", str(res['Прогнозный охват, %']))
    
    # 5. Эффективная частота
    m5.metric("Оптимальная частота на месяц (все медиа)", str(res['Эффективная частота']))

    st.markdown("<br>", unsafe_allow_html=True)

    # Визуализация
    col_chart1, col_chart2 = st.columns([1, 1.2])
    
    with col_chart1:
        st.write("**Медиа сплит**")
        pie_df = pd.DataFrame({
            'Канал': ['Digital', 'TV', 'Offline'],
            'Доля': [res['Digital'], res['TV'], res['Others offline']]
        }).query("Доля > 0")
        
        fig1 = px.pie(pie_df, values='Доля', names='Канал', hole=.4,
                      color_discrete_sequence=px.colors.qualitative.Pastel)
        fig1.update_traces(textinfo='percent+label')
        st.plotly_chart(fig1, use_container_width=True)

    with col_chart2:
        st.write("**Digital сплит**")
        dig_labels = ['Smart TV', 'Видео', 'Мобайл', 'Контекст', 'Программатик', 'Нативные', 'Соц.сети']
        dig_vals = [res.get('Smart TV', 0), res.get('Видео', 0), res.get('Мобайл (in-app)', 0),
                    res.get('Контекст', 0), res.get('Программатик баннеры', 0),
                    res.get('Нативные баннеры', 0), res.get('Соц.сети', 0)]
        
        dig_df = pd.DataFrame({'Инструмент': dig_labels, 'Доля': dig_vals}).query("Доля > 0")
        fig2 = px.bar(dig_df, x='Доля', y='Инструмент', orientation='h', text_auto='.0%',
                      color='Инструмент', color_discrete_sequence=px.colors.sequential.Viridis)
        fig2.update_layout(showlegend=False, xaxis_visible=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.success("**Рекомендация эксперта:**")
    st.write(res['Рекомендация'])
else:
    st.warning("Комбинация параметров не найдена. Попробуйте изменить фильтры.")
