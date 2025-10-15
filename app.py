import streamlit as st
import requests
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --------------------------------------------------------
# 🎨 Configuración de página
# --------------------------------------------------------
st.set_page_config(
    page_title="Análisis de Usuarios API",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------------
# 🎨 CSS personalizado
# --------------------------------------------------------
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }
    .stApp {
        background: transparent;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
    }
    .card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    h1 {
        color: white !important;
        text-align: center;
        font-size: 3rem !important;
        margin-bottom: 0.5rem !important;
    }
    h2, h3 {
        color: white !important;
    }
    .subtitle {
        color: rgba(255,255,255,0.9);
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------------------
# 🎓 Carátula moderna
# --------------------------------------------------------
st.markdown("# 📊 Dashboard de Análisis de Usuarios")
st.markdown('<p class="subtitle">Visualización avanzada de datos desde API JSONPlaceholder</p>', unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col2:
    st.markdown("**👨‍💻 Autor:** Gilson Tenemea")
    st.markdown("**🚀 Proyecto:** Data Analytics")

st.markdown("---")

# --------------------------------------------------------
# 📦 Configuración inicial
# --------------------------------------------------------
DB_NAME = 'usuarios3.db'
API_URL = 'https://jsonplaceholder.typicode.com/users'

# --------------------------------------------------------
# 🔹 Consumir API con spinner
# --------------------------------------------------------
with st.spinner('🔄 Conectando con la API...'):
    try:
        response = requests.get(API_URL, timeout=20)
        if response.status_code != 200:
            st.error(f"❌ Error al consumir la API ({response.status_code})")
            st.stop()
        users = response.json()
    except Exception as e:
        st.error(f"❌ Error de conexión: {str(e)}")
        st.stop()

# --------------------------------------------------------
# 🗃️ Guardar en SQLite
# --------------------------------------------------------
conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS users;')
cur.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    username TEXT,
    email TEXT,
    phone TEXT,
    website TEXT
)
''')

for u in users:
    cur.execute('''
        INSERT OR REPLACE INTO users (id, name, username, email, phone, website)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        u.get('id'), u.get('name'), u.get('username'), u.get('email'), u.get('phone'), u.get('website')
    ))

conn.commit()
conn.close()

# --------------------------------------------------------
# 📊 Cargar datos desde SQLite
# --------------------------------------------------------
conn = sqlite3.connect(DB_NAME)
df = pd.read_sql_query('SELECT * FROM users', conn)
conn.close()

# --------------------------------------------------------
# 🔍 Procesamiento
# --------------------------------------------------------
df['name_length'] = df['name'].astype(str).apply(len)
df['email_domain'] = df['email'].astype(str).apply(lambda x: x.split('@')[-1].lower() if '@' in str(x) else None)

# --------------------------------------------------------
# 📈 Métricas principales
# --------------------------------------------------------
st.markdown("## 📈 Métricas Principales")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="👥 Total Usuarios",
        value=len(df),
        delta="100% activos"
    )

with col2:
    st.metric(
        label="📧 Dominios Únicos",
        value=df['email_domain'].nunique(),
        delta=f"{df['email_domain'].nunique()} diferentes"
    )

with col3:
    st.metric(
        label="📝 Nombre Promedio",
        value=f"{df['name_length'].mean():.1f} chars",
        delta=f"Max: {df['name_length'].max()}"
    )

with col4:
    st.metric(
        label="✅ Estado",
        value="Sincronizado",
        delta="Base actualizada"
    )

st.markdown("---")

# --------------------------------------------------------
# 📊 Visualizaciones principales
# --------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["📊 Distribuciones", "📈 Análisis", "📋 Datos", "🔍 Detalles"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Distribución de Longitud de Nombres")
        fig1 = px.histogram(
            df, x='name_length', 
            nbins=15,
            color_discrete_sequence=['#667eea']
        )
        fig1.update_layout(
            xaxis_title='Cantidad de caracteres',
            yaxis_title='Frecuencia',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=False
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.markdown("### 🥧 Distribución por Dominio")
        dom_counts = df['email_domain'].value_counts().reset_index()
        dom_counts.columns = ['email_domain', 'count']
        
        fig3 = px.pie(
            dom_counts, 
            names='email_domain', 
            values='count',
            hole=0.5,
            color_discrete_sequence=px.colors.sequential.Purples_r
        )
        fig3.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig3, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📧 Usuarios por Dominio de Correo")
        fig2 = px.bar(
            dom_counts, 
            x='count', 
            y='email_domain',
            orientation='h',
            color='count',
            color_continuous_scale='Purples'
        )
        fig2.update_layout(
            xaxis_title='Cantidad de usuarios',
            yaxis_title='Dominio',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=False
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        st.markdown("### 📏 Longitud Promedio por Dominio")
        avg_length = df.groupby('email_domain')['name_length'].mean().reset_index()
        fig5 = px.bar(
            avg_length, 
            x='email_domain', 
            y='name_length',
            color='name_length',
            color_continuous_scale='Viridis'
        )
        fig5.update_layout(
            xaxis_title='Dominio de email',
            yaxis_title='Longitud promedio',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=False
        )
        st.plotly_chart(fig5, use_container_width=True)
    
    st.markdown("### 🏆 Top 10 Usuarios con Nombres Más Largos")
    top_names = df.sort_values('name_length', ascending=False).head(10)
    fig6 = px.bar(
        top_names, 
        x='name', 
        y='name_length',
        color='name_length',
        color_continuous_scale='Sunset',
        text='name_length'
    )
    fig6.update_layout(
        xaxis_title='Usuario',
        yaxis_title='Longitud del nombre',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False
    )
    fig6.update_traces(textposition='outside')
    st.plotly_chart(fig6, use_container_width=True)

with tab3:
    st.markdown("### 📋 Tabla de Usuarios")
    
    # Selector de columnas
    cols_to_show = st.multiselect(
        "Selecciona las columnas a mostrar:",
        options=df.columns.tolist(),
        default=['id', 'name', 'username', 'email']
    )
    
    if cols_to_show:
        st.dataframe(
            df[cols_to_show],
            use_container_width=True,
            height=400
        )
    
    # Botón de descarga
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Descargar datos como CSV",
        data=csv,
        file_name='usuarios_analisis.csv',
        mime='text/csv',
    )

with tab4:
    st.markdown("### 🔍 Vista Detallada")
    
    fig4 = go.Figure(data=[go.Table(
        header=dict(
            values=list(df[['id','name','username','email','phone','website']].columns),
            fill_color='#667eea',
            align='left',
            font=dict(color='white', size=12)
        ),
        cells=dict(
            values=[df['id'], df['name'], df['username'], df['email'], df['phone'], df['website']],
            fill_color='lavender',
            align='left',
            font=dict(color='black', size=11)
        )
    )])
    
    fig4.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=500
    )
    st.plotly_chart(fig4, use_container_width=True)

# --------------------------------------------------------
# 🎯 Footer
# --------------------------------------------------------
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: rgba(255,255,255,0.7);'>✨ Dashboard creado con Streamlit y Plotly | 2024</p>",
    unsafe_allow_html=True
)
st.success("✅ Visualización completada correctamente.")