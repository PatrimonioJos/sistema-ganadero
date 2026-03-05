import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import altair as alt
from datetime import date, datetime
import os
import time
import requests # Necesario para ImgBB

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Sistema Ganadero Élite", page_icon="🐮", layout="wide")

# --- 🔑 TU CLAVE DE IMGBB ---
API_KEY_IMGBB = "a2e56c54a8b85f305651768ba9403148"

# --- LISTAS DE OPCIONES ---
OPCIONES_ALIMENTACION = [
    "Pastoreo", "Pastoreo + Concentrado", "Heno", "Ensilage", 
    "Concentrado", "Suplementos", "Forraje", "Raciones mezcladas", 
    "Estabulación", "Otros"
]

# --- NUEVAS LISTAS PARA REGISTRO COMPLETO (ACTUALIZACIÓN) ---
LISTA_ESPECIES = ["Bovino", "Porcino", "Ovino", "Caprino", "Equino", "Bufalino", "Otro"]

LISTA_RAZAS_GLOBAL = [
    # Bovinos
    "Brahman", "Gyr", "Holstein", "Jersey", "Angus", "Brangus", "Senepol", 
    "Guzerat", "Nelore", "Pardo Suizo", "Simmental", "Charolais", "Hereford", 
    "Normando", "Limousin", "Mestizo / Cruzado", "Criollo",
    # Porcinos
    "Landrace", "Yorkshire", "Duroc", "Pietrain", "Hampshire",
    # Ovinos/Caprinos
    "Dorper", "Katahdin", "Pelibuey", "Boer", "Saanen", "Alpina",
    "Otro"
]

LISTA_PROPOSITOS = ["Carne", "Leche", "Doble Propósito", "Cría / Genética", "Deporte / Trabajo", "Mascota"]

# Listas Veterinarias
TIPOS_TRATAMIENTO = [
    "Desparacitación", "Secado", "Tratamiento de fertilidad", "Castración",
    "Tratamiento de mastitis", "Endo-ectoparasiticida", "Endoparasiticida",
    "Ectoparasiticida", "Hemoparasiticida", "Otros antiparasitarios",
    "Suplemento vitamínico-mineral", "Suplemento estimulante metabólico",
    "Suplemento de aminoácidos/proteínas", "Suplemento energético", 
    "Suplemento de fibra", "Suplemento probiótico/prebiótico", 
    "Otros suplementos nutricionales", "Hormona reproductiva", "Esteroide anabólico",
    "Hormona de crecimiento", "Otros tratamientos hormonales", 
    "Antibiótico de amplio espectro", "Antibiótico de espectro reducido",
    "Antibiótico antifúngico", "Antibiótico antiviral", "Otros antibióticos",
    "Antiinflamatorio no esteroideo", "Antiinflamatorio esteroideo",
    "Otros antiinflamatorios", "Agente de diagnóstico - Análisis de sangre",
    "Agente de diagnóstico - Ultrasonido", "Agente de diagnóstico - Rayos X",
    "Otros agentes de diagnóstico", "Otros"
]

LISTA_ENFERMEDADES = [
    "Fiebre Aftosa", "Brucelosis", "Tuberculosis", "Leptospirosis",
    "Rinotraqueitis Infecciosa Bovina (IBR)", "Diarrea Viral Bovina (DVB)",
    "Pasteurelosis", "Clostridium", "Paratuberculosis", "Campylobacteriosis",
    "Mastitis", "Otra Enfermedad"
]

LISTA_VACUNAS = [
    "Fiebre Aftosa", "Brucelosis", "Tuberculosis", "Leptospirosis",
    "Rinotraqueítis Infecciosa Bovina (IBR)", "Diarrea Viral Bovina (DVB)",
    "Pasteurelosis", "Clostridium", "Paratuberculosis", "Campilobacteriosis",
    "Rabia", "Complejo Clostridial", "Complejo Respiratorio",
    "Complejo Reproductivo", "PPCB", "Antiparasitario",
    "Vacuna Viral", "Vacuna Bacteriana", "Otra Vacuna"
]

GRADOS_MASTITIS = ["-", "1 - Oculta (Subclínica)", "2 - Leve", "3 - Moderada"]

CAUSAS_MUERTE = [
    "Ataque animal", "Abandono", "Accidental", "Aborto", 
    "Infección", "Enfermedad", "Envenenamiento", "Desaparecida", "Otro"
]

# Listas Reproducción
TIPOS_FECUNDACION = ["Monta", "Inseminación artificial", "Transferencia de embriones", "Otros"]

# --- ESTILOS CSS ---
st.markdown("""
<style>
    /* Estilo General Botones */
    div.stButton > button {
        width: 100%;
        height: 50px;
        font-size: 16px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Botones Rojos */
    .btn-rojo {
        background-color: #d93025 !important;
        color: white !important;
        font-weight: bold;
        border: none;
    }

    /* Header Estilo App para Registro Completo */
    .app-header {
        background-color: #4CAF50;
        color: white;
        padding: 10px 15px;
        font-weight: bold;
        border-radius: 5px;
        margin-bottom: 15px;
        font-size: 16px;
    }

    .seccion-titulo {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
        margin-bottom: 10px;
        font-weight: bold;
        color: #31333F;
    }
    
    /* Estilo Tablas */
    .tabla-header {
        background-color: #2e7d32;
        color: white;
        padding: 8px;
        border-radius: 8px 8px 0 0;
        font-weight: bold;
        font-size: 14px;
        display: flex;
        justify-content: space-between;
    }
    .tabla-row {
        background-color: white;
        padding: 10px;
        border-bottom: 1px solid #eee;
        border-left: 1px solid #eee;
        border-right: 1px solid #eee;
        font-size: 14px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Tarjetas Historial */
    .vet-card {
        background-color: white;
        border-left: 5px solid #2e7d32;
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .repro-card {
        background-color: white;
        border-left: 5px solid #1565c0; /* Azul para repro */
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Texto centrado para el estado vacío */
    .empty-state {
        text-align: center;
        padding: 20px;
        color: #666;
    }
    
    /* Estilo Ubre Mastitis */
    .ubre-box {
        background-color: #ef9a9a; 
        border-radius: 20px;
        padding: 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 15px;
        width: 100%;
        height: 100%;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.1);
    }
    .ubre-row {
        display: flex;
        gap: 30px;
        font-weight: bold;
        color: white;
        font-size: 20px;
    }
    .ubre-num {
        background-color: rgba(255,255,255,0.3);
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    /* Header Reproductivo (Estadísticas) */
    .repro-stats {
        background-color: #2e7d32;
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .repro-stats h3 { margin: 0; color: white; font-size: 18px; }
    .repro-stats p { margin: 5px 0 0 0; font-size: 14px; opacity: 0.9; }
    .stat-row { display: flex; justify-content: space-between; margin-top: 5px; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 5px; }

    /* Estilo Toggle Macho/Hembra Personalizado */
    div[role="radiogroup"] {
        display: flex;
        justify-content: center;
        gap: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN GOOGLE SHEETS ---
def obtener_credenciales():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    if os.path.exists("credentials.json"):
        return Credentials.from_service_account_file("credentials.json", scopes=scopes)
    elif "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        return Credentials.from_service_account_info(creds_dict, scopes=scopes)
    else:
        return None

def conectar_sheets():
    creds = obtener_credenciales()
    if not creds:
        st.error("❌ No se encontraron credenciales.")
        return None
    try:
        client = gspread.authorize(creds)
        # ID DE TU HOJA DE CALCULO
        sheet_id = "1292mc53ss8G8pY-azGsrpq10OR8RDX0gNMVML8LgfU0" 
        return client.open_by_key(sheet_id)
    except Exception as e:
        st.error(f"⚠️ Error conectando con Google Sheets: {e}")
        return None

# --- FUNCIÓN: SUBIR A IMGBB ---
def subir_foto_imgbb(archivo):
    if archivo is None: return "Sin Foto"
    try:
        url = "https://api.imgbb.com/1/upload"
        payload = {"key": API_KEY_IMGBB, "expiration": 0}
        files = {"image": archivo.getvalue()}
        response = requests.post(url, data=payload, files=files)
        if response.status_code == 200:
            return response.json()["data"]["url"]
        else:
            return "Error"
    except:
        return "Error"

# --- UTILIDADES ---
def calcular_edad(fecha_nac_str):
    try:
        nacimiento = datetime.strptime(str(fecha_nac_str), "%Y-%m-%d").date()
        hoy = date.today()
        dias = (hoy - nacimiento).days
        meses = int(dias / 30.44)
        anios = int(meses / 12)
        meses_restantes = meses % 12
        if anios > 0:
            return f"{anios} años {meses_restantes} meses"
        else:
            return f"{meses} meses"
    except:
        return "--"

# --- CRUD BASE DE DATOS ---
def guardar_animal(sheet, datos, rerun=True):
    # 'datos' ahora puede ser una lista más larga que las columnas actuales
    # Google Sheets simplemente añadirá las celdas en las columnas nuevas
    sheet.append_row(datos)
    st.toast("✅ Animal registrado")
    if rerun:
        st.balloons()
        time.sleep(1)
        st.rerun()

def guardar_evento(sh, datos, tipo_evento):
    try:
        worksheet = sh.worksheet("Historial")
    except:
        worksheet = sh.add_worksheet(title="Historial", rows="1000", cols="10")
        worksheet.append_row(["Fecha", "Tipo Evento", "ID Animal", "Detalle 1", "Detalle 2", "Notas"])
    
    worksheet.append_row(datos)
    st.toast(f"✅ {tipo_evento} guardado")

def encontrar_fila_por_id(sheet, id_animal):
    try:
        columna_ids = sheet.col_values(1)
        return columna_ids.index(str(id_animal)) + 1
    except ValueError:
        return None

def actualizar_animal_completo(sheet, id_animal, nuevos_datos):
    fila = encontrar_fila_por_id(sheet, id_animal)
    if fila:
        rango = f"A{fila}:J{fila}"
        sheet.update(rango, [nuevos_datos])
        st.success("✅ Datos actualizados correctamente")
        time.sleep(1)
        st.rerun()

def cambiar_estado_animal(sheet, id_animal, nuevo_estado):
    fila = encontrar_fila_por_id(sheet, id_animal)
    if fila:
        sheet.update_cell(fila, 9, nuevo_estado)

def eliminar_animal_db(sheet, id_animal):
    fila = encontrar_fila_por_id(sheet, id_animal)
    if fila:
        sheet.delete_rows(fila)
        st.warning("🗑️ Animal eliminado")
        time.sleep(1)
        st.rerun()

def cambiar_estado_vendido(sheet, id_animal):
    fila = encontrar_fila_por_id(sheet, id_animal)
    if fila:
        sheet.update_cell(fila, 9, "VENDIDO") 

# --- GESTIÓN DE ESTADO (NAVEGACIÓN) ---
if 'nav_gestion' not in st.session_state:
    st.session_state.nav_gestion = 'lista' 
if 'animal_seleccionado' not in st.session_state:
    st.session_state.animal_seleccionado = None
if 'accion_activa' not in st.session_state:
    st.session_state.accion_activa = None
if 'sub_accion_produccion' not in st.session_state:
    st.session_state.sub_accion_produccion = None
if 'sub_accion_veterinaria' not in st.session_state:
    st.session_state.sub_accion_veterinaria = None
if 'sub_accion_reproduccion' not in st.session_state:
    st.session_state.sub_accion_reproduccion = None
# NUEVO: Estado para alternar entre registro rápido y completo
if 'registro_expandido' not in st.session_state:
    st.session_state.registro_expandido = False

def ir_a_lista():
    st.session_state.nav_gestion = 'lista'
    st.session_state.animal_seleccionado = None

def ir_a_perfil(animal_id):
    st.session_state.animal_seleccionado = animal_id
    st.session_state.nav_gestion = 'perfil'

def ir_a_detalle():
    st.session_state.nav_gestion = 'detalle'

def ir_a_produccion():
    st.session_state.nav_gestion = 'produccion'
    st.session_state.sub_accion_produccion = None

def ir_a_veterinaria():
    st.session_state.nav_gestion = 'veterinaria'
    st.session_state.sub_accion_veterinaria = None

def ir_a_reproduccion():
    st.session_state.nav_gestion = 'reproduccion'
    st.session_state.sub_accion_reproduccion = None

def set_accion(nombre_accion):
    st.session_state.accion_activa = nombre_accion

def toggle_registro_mode():
    st.session_state.registro_expandido = not st.session_state.registro_expandido

# --- APP PRINCIPAL ---
def main():
    st.title("🧬 Control Ganadero")

    sh = conectar_sheets()
    
    if sh:
        # LEER DATOS
        hoja_animales = sh.get_worksheet(0)
        try:
            data = hoja_animales.get_all_records()
            df = pd.DataFrame(data)
            
            if not df.empty:
                df.columns = df.columns.astype(str).str.strip()
                df["ID"] = df["ID"].astype(str)
                df_activos = df[df["Estado"] != "VENDIDO"]
                lista_ids_activos = df_activos["ID"].tolist()
                lista_ids_todos = df["ID"].tolist()
            else:
                df_activos = pd.DataFrame()
                lista_ids_activos = []
                lista_ids_todos = []
        except:
            df = pd.DataFrame()
            df_activos = pd.DataFrame()
            lista_ids_activos = []

        # Historial
        try:
            hoja_historial = sh.worksheet("Historial")
            df_hist = pd.DataFrame(hoja_historial.get_all_records())
        except:
            df_hist = pd.DataFrame()

        # --- PESTAÑAS (TABS) ---
        tab_dash, tab_reg, tab_gest, tab_acc, tab_ventas = st.tabs([
            "📊 DASHBOARD", "📝 REGISTRO", "📱 GESTIÓN (APP)", "⚡ RÁPIDO", "💰 VENTAS"
        ])

        # ==========================================
        # 1. DASHBOARD
        # ==========================================
        with tab_dash:
            if not df_activos.empty:
                col_graf, col_stats = st.columns([1, 1])
                with col_graf:
                    with st.container(border=True):
                        st.subheader("Distribución")
                        base = alt.Chart(df_activos).encode(theta=alt.Theta("count()", stack=True))
                        pie = base.mark_arc(outerRadius=100, innerRadius=60).encode(
                            color=alt.Color("Tipo"), order=alt.Order("Tipo", sort="descending"), tooltip=["Tipo", "count()"])
                        st.altair_chart(pie, use_container_width=True)
                with col_stats:
                    with st.container(border=True):
                        st.subheader("Indicadores")
                        st.metric("Total en Finca", len(df_activos))
                        hembras = len(df_activos[df_activos["Sexo"] == "Hembra"])
                        st.metric("Hembras", hembras)
            else:
                st.info("👋 Registra animales para ver el tablero.")

        # ==========================================
        # 2. REGISTRO (MODO DUAL: RÁPIDO Y COMPLETO)
        # ==========================================
        with tab_reg:
            
            # --- MODO RÁPIDO (Original) ---
            if not st.session_state.registro_expandido:
                st.info("Ficha de Ingreso Rápido")
                with st.form("ficha_registro_rapido", clear_on_submit=True):
                    c1, c2, c3, c4 = st.columns(4)
                    with c1: id_new = st.text_input("Código / ID*")
                    with c2: arete_new = st.text_input("Arete")
                    with c3: nom_new = st.text_input("Nombre")
                    with c4: sexo_new = st.radio("Sexo", ["Hembra", "Macho"], horizontal=True)
                    
                    c5, c6, c7 = st.columns(3)
                    with c5: raza_new = st.selectbox("Raza", ["Brahman", "Gyr", "Holstein", "Mestizo", "Senepol", "Otro"])
                    with c6: tipo_new = st.selectbox("Categoría", ["Vaca", "Toro", "Novilla", "Becerro"])
                    with c7: estado_new = st.selectbox("Estado", ["Sano", "Enfermo", "Preñada"])

                    c8, c9, c10 = st.columns(3)
                    with c8: peso_new = st.number_input("Peso (kg)*", min_value=0.0)
                    with c9: nac_new = st.date_input("Nacimiento")
                    with c10: foto_new = st.file_uploader("Foto")

                    if st.form_submit_button("💾 GUARDAR RÁPIDO", type="primary"):
                        if not id_new:
                            st.error("El ID es obligatorio")
                        elif id_new in lista_ids_todos:
                            st.error("ID Repetido")
                        else:
                            link = "Sin Foto"
                            if foto_new:
                                with st.spinner("Subiendo foto..."):
                                    link = subir_foto_imgbb(foto_new)
                            
                            # Estructura básica
                            datos = [id_new, tipo_new, nom_new, arete_new, raza_new, sexo_new, str(peso_new), str(nac_new), estado_new, link]
                            guardar_animal(hoja_animales, datos)

                st.write("")
                st.markdown("---")
                # Botón para cambiar al modo completo
                if st.button("✏️ Ampliar datos (Registro Completo)"):
                    toggle_registro_mode()
                    st.rerun()

            # --- MODO COMPLETO (Estilo App Móvil) ---
            else:
                if st.button("⬅️ Volver a registro rápido"):
                    toggle_registro_mode()
                    st.rerun()

                st.markdown('<div class="app-header">📝 Crear Animal (Completo)</div>', unsafe_allow_html=True)

                with st.form("ficha_registro_completo", clear_on_submit=True):
                    
                    # 1. FOTO Y SEXO
                    col_foto, col_sexo = st.columns([1, 1])
                    with col_foto:
                        foto_full = st.file_uploader("Foto del animal", type=["jpg", "png", "jpeg"])
                    with col_sexo:
                        st.write("Sexo")
                        sexo_full = st.radio("Sexo", ["Macho", "Hembra"], horizontal=True, label_visibility="collapsed")

                    # 2. TIPO E IDENTIFICACIÓN
                    st.markdown('<div class="seccion-titulo">Identificación</div>', unsafe_allow_html=True)
                    tipo_full = st.selectbox("Tipo de animal *", LISTA_ESPECIES)
                    
                    col_id1, col_id2 = st.columns(2)
                    with col_id1: id_full = st.text_input("Número del animal (ID) *")
                    with col_id2: arete_full = st.text_input("Arete / Visual (Opcional)")
                    
                    col_id3, col_id4 = st.columns(2)
                    with col_id3: num_raza_full = st.text_input("Número de raza pura (Opcional)")
                    with col_id4: num_chip_full = st.text_input("Número de chip (Opcional)")

                    # 3. INFORMACIÓN BÁSICA
                    st.markdown('<div class="seccion-titulo">Información Básica</div>', unsafe_allow_html=True)
                    nombre_full = st.text_input("Nombre del animal")
                    nac_full = st.date_input("Fecha de nacimiento *", date.today())
                    
                    col_bas1, col_bas2 = st.columns(2)
                    with col_bas1: prop_full = st.selectbox("Propietario", ["Principal", "Socio", "Externo"])
                    with col_bas2: lote_full = st.selectbox("Lote", ["General", "Lote 1", "Lote 2", "Enfermería"])
                    
                    raza_full = st.selectbox("Raza *", LISTA_RAZAS_GLOBAL)
                    
                    # 4. PROPÓSITO Y ESTADO
                    col_prop1, col_prop2 = st.columns(2)
                    with col_prop1: proposito_full = st.selectbox("Propósito Animal", LISTA_PROPOSITOS)
                    with col_prop2: 
                        st.write("¿Está en la finca?")
                        en_finca_full = st.toggle("En Finca", value=True)

                    # 5. PESOS
                    st.markdown('<div class="seccion-titulo">Pesos (kg)</div>', unsafe_allow_html=True)
                    c_peso1, c_peso2, c_peso3 = st.columns(3)
                    with c_peso1: peso_nac = st.number_input("Al nacer", min_value=0.0)
                    with c_peso2: peso_dest = st.number_input("Al destete", min_value=0.0)
                    with c_peso3: peso_12m = st.number_input("12 meses", min_value=0.0)
                    
                    # Calcular Peso Actual Inicial (Prioridad: 12m > Destete > Nacer)
                    peso_actual_reg = peso_nac
                    if peso_dest > 0: peso_actual_reg = peso_dest
                    if peso_12m > 0: peso_actual_reg = peso_12m

                    # 6. ORIGEN (DINÁMICO - Filtra del inventario)
                    st.markdown('<div class="seccion-titulo">Origen</div>', unsafe_allow_html=True)
                    
                    lista_padres = ["Desconocido"]
                    lista_madres = ["Desconocida"]
                    
                    if not df_activos.empty:
                        # Filtrar Machos (Toros)
                        machos = df_activos[(df_activos['Sexo'] == 'Macho') | (df_activos['Tipo'] == 'Toro')]
                        if not machos.empty: lista_padres += machos['Nombre'].tolist()
                        
                        # Filtrar Hembras (Vacas)
                        hembras = df_activos[(df_activos['Sexo'] == 'Hembra') | (df_activos['Tipo'] == 'Vaca') | (df_activos['Tipo'] == 'Novilla')]
                        if not hembras.empty: lista_madres += hembras['Nombre'].tolist()

                    col_orig1, col_orig2 = st.columns(2)
                    with col_orig1: padre_full = st.selectbox("Padre", lista_padres)
                    with col_orig2: madre_full = st.selectbox("Madre", lista_madres)

                    # 7. NOTAS
                    st.markdown('<div class="seccion-titulo">Otros</div>', unsafe_allow_html=True)
                    notas_full = st.text_area("Notas y observaciones")

                    # BOTÓN FINAL
                    st.write("")
                    if st.form_submit_button("REGISTRAR ANIMAL", type="primary"):
                        if not id_full:
                            st.error("El Número del animal (ID) es obligatorio.")
                        elif id_full in lista_ids_todos:
                            st.error("¡Ese ID ya existe en el sistema!")
                        else:
                            link = "Sin Foto"
                            if foto_full:
                                with st.spinner("Subiendo foto..."):
                                    link = subir_foto_imgbb(foto_full)
                            
                            estado_inicial = "Sano"
                            
                            # Lista Extendida de Datos (Se guardará en columnas K, L, M...)
                            # Orden: [ID, Tipo, Nombre, Arete, Raza, Sexo, Peso, Nacimiento, Estado, Foto, 
                            #         Propósito, EnFinca, Padre, Madre, PesoNac, PesoDest, Peso12, Notas, Dueño, Lote, Chip, NumRaza]
                            datos_extendidos = [
                                str(id_full), tipo_full, nombre_full, arete_full, raza_full, sexo_full, str(peso_actual_reg), str(nac_full), estado_inicial, link,
                                proposito_full, str(en_finca_full), padre_full, madre_full, str(peso_nac), str(peso_dest), str(peso_12m), notas_full, prop_full, lote_full, num_chip_full, num_raza_full
                            ]
                            
                            guardar_animal(hoja_animales, datos_extendidos)
                            # ==========================================
        # 3. GESTIÓN TIPO APP MÓVIL (TUS IMÁGENES)
        # ==========================================
        with tab_gest:
            
            # --- VISTA 1: LISTA ---
            if st.session_state.nav_gestion == 'lista':
                c_search, c_filter = st.columns([3, 1])
                with c_search:
                    busqueda = st.text_input("🔍 Buscar (Nombre o ID)", placeholder="Ej. Gloria")
                with c_filter:
                    st.write("") 
                    st.caption(f"{len(df_activos)} Animales")

                df_show = df_activos
                if busqueda:
                    df_show = df_activos[df_activos.apply(lambda row: busqueda.lower() in str(row.values).lower(), axis=1)]

                if not df_show.empty:
                    for index, row in df_show.iterrows():
                        with st.container(border=True):
                            c_img, c_info, c_btn = st.columns([1, 3, 1])
                            
                            with c_img:
                                foto_url = str(row.get("Foto", ""))
                                if "http" in foto_url: st.image(foto_url, use_container_width=True)
                                else: st.image("https://cdn-icons-png.flaticon.com/512/2173/2173516.png", width=50)
                            
                            with c_info:
                                st.subheader(f"{row['Nombre']}")
                                edad = calcular_edad(row['Nacimiento'])
                                st.caption(f"ID: {row['ID']} | {row['Raza']} | {edad}")
                            
                            with c_btn:
                                st.write("") 
                                if st.button("👉 Ver", key=f"btn_{row['ID']}"):
                                    ir_a_perfil(row['ID'])
                                    st.rerun()
                else:
                    st.info("No hay animales activos.")

            # --- VISTA 2: PERFIL ---
            elif st.session_state.nav_gestion == 'perfil':
                animal_id = st.session_state.animal_seleccionado
                datos = df[df["ID"] == animal_id].iloc[0]
                
                col_back, col_tit = st.columns([1, 5])
                with col_back:
                    if st.button("⬅️"):
                        ir_a_lista()
                        st.rerun()
                with col_tit:
                    st.subheader(f"Perfil: {datos['Nombre']}")

                with st.container(border=True):
                    c_h1, c_h2 = st.columns([1, 2])
                    with c_h1:
                        foto_url = str(datos.get("Foto", ""))
                        if "http" in foto_url: st.image(foto_url, use_container_width=True)
                        else: st.image("https://cdn-icons-png.flaticon.com/512/2173/2173516.png")
                    with c_h2:
                        st.title(datos['Nombre'])
                        st.write(f"**{datos['Raza']}**")
                        st.write(f"ID: {datos['ID']}")

                st.markdown("---")
                
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button("ℹ️ Datos generales", use_container_width=True):
                        ir_a_detalle()
                        st.rerun()
                    st.write("")
                    if st.button("❤️ Datos veterinarios", use_container_width=True):
                        ir_a_veterinaria()
                        st.rerun()

                with c_btn2:
                    if st.button("📊 Producción", use_container_width=True):
                        ir_a_produccion()
                        st.rerun()
                    st.write("")
                    if st.button("🧬 Reproducción", use_container_width=True):
                        ir_a_reproduccion()
                        st.rerun()

                st.markdown("---")
                if st.button("Poner en venta", type="primary", use_container_width=True):
                    st.session_state.accion_activa = "venta"
                    st.info("✅ Modo Venta Activado. Ve a la pestaña '⚡ RÁPIDO' para completar los datos.")

            # --- VISTA 3: PRODUCCIÓN ---
            elif st.session_state.nav_gestion == 'produccion':
                animal_id = st.session_state.animal_seleccionado
                datos = df[df["ID"] == animal_id].iloc[0]

                st.markdown(f"""
                <div style='background-color: #2e7d32; padding: 15px; border-radius: 10px; color: white; margin-bottom: 20px;'>
                    <h3 style='margin:0;'>Producción: {datos['Nombre']}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("⬅️ Volver al Perfil"):
                    ir_a_perfil(animal_id)
                    st.rerun()

                if st.session_state.sub_accion_produccion is None:
                    # FILTRAR DATOS
                    df_vaca_hist = pd.DataFrame()
                    if not df_hist.empty:
                        df_hist["ID Animal"] = df_hist["ID Animal"].astype(str)
                        df_vaca_hist = df_hist[df_hist["ID Animal"] == str(animal_id)]

                    hist_leche = pd.DataFrame()
                    hist_peso = pd.DataFrame()
                    
                    if not df_vaca_hist.empty:
                         hist_leche = df_vaca_hist[df_vaca_hist["Tipo Evento"] == "PRODUCCION_LECHE"]
                         hist_peso = df_vaca_hist[df_vaca_hist["Tipo Evento"] == "PESAJE"]

                    if hist_leche.empty and hist_peso.empty:
                        st.markdown("<br>", unsafe_allow_html=True)
                        col_center = st.columns([1, 2, 1])[1]
                        with col_center:
                            st.markdown("""
                            <div class="empty-state">
                                <img src="https://cdn-icons-png.flaticon.com/512/2674/2674067.png" width="100" style="opacity: 0.5;">
                                <h3>No hay nada para mostrar</h3>
                                <p>Registre el peso y la producción de leche para comenzar a controlarlo.</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.write("")
                        promedio_leche = 0.0
                        if not hist_leche.empty:
                            try: promedio_leche = hist_leche["Detalle 1"].astype(float).mean()
                            except: pass

                        st.subheader("Producción de leche")
                        st.caption(f"Promedio diario: {promedio_leche:.1f} L")
                        
                        st.markdown("""
                        <div class="tabla-header">
                            <div style="width:30%">Fecha</div>
                            <div style="width:30%">Concentr...</div>
                            <div style="width:30%">Total leche</div>
                            <div style="width:10%"></div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if not hist_leche.empty:
                            for idx, row in hist_leche.iloc[::-1].iterrows():
                                concentrado_txt = "--"
                                try:
                                    det2 = str(row["Detalle 2"])
                                    if "Conc:" in det2: concentrado_txt = det2.split("Conc:")[1].strip()
                                except: pass
                                
                                st.markdown(f"""
                                <div class="tabla-row">
                                    <div style="width:30%">{row['Fecha']}</div>
                                    <div style="width:30%">{concentrado_txt}</div>
                                    <div style="width:30%">{row['Detalle 1']} L</div>
                                    <div style="width:10%; color: red;">Wait</div> 
                                </div>
                                """, unsafe_allow_html=True)
                        else: st.info("Sin registros de leche.")

                        st.write("")
                        peso_actual = datos['Peso']
                        st.subheader(f"Evolución de peso: <span style='color:green'>Actual {peso_actual} kg</span>", anchor=False, help=None)
                        st.caption("Ganancia diaria: -- kg")

                        st.markdown("""
                        <div class="tabla-header">
                            <div style="width:30%">Fecha</div>
                            <div style="width:30%">Peso</div>
                            <div style="width:30%">Ganancia</div>
                            <div style="width:10%"></div>
                        </div>
                        """, unsafe_allow_html=True)

                        if not hist_peso.empty:
                            hist_peso_rev = hist_peso.iloc[::-1].reset_index()
                            for i, row in hist_peso_rev.iterrows():
                                st.markdown(f"""
                                <div class="tabla-row">
                                    <div style="width:30%">{row['Fecha']}</div>
                                    <div style="width:30%">{row['Detalle 1']} kg</div>
                                    <div style="width:30%">--</div>
                                    <div style="width:10%; color: red;">Wait</div>
                                </div>
                                """, unsafe_allow_html=True)
                        else: st.info("Sin registros de peso.")

                    st.write("")
                    st.markdown("---")
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if st.button("AGREGAR PESO", type="primary", use_container_width=True):
                            st.session_state.sub_accion_produccion = 'add_peso'
                            st.rerun()
                    with col_b2:
                        if st.button("AGREGAR LECHE", type="primary", use_container_width=True):
                            st.session_state.sub_accion_produccion = 'add_leche'
                            st.rerun()

                elif st.session_state.sub_accion_produccion == 'add_peso':
                    st.subheader("Registrar Peso")
                    with st.form("form_peso_app"):
                        fp_fecha = st.date_input("Fecha *", date.today())
                        fp_peso = st.number_input("Peso (kg) *", min_value=0.0)
                        fp_alim = st.selectbox("Tipo de alimentación *", OPCIONES_ALIMENTACION)
                        fp_notas = st.text_area("Notas y observaciones")
                        
                        col_cancel, col_save = st.columns(2)
                        with col_cancel:
                            if st.form_submit_button("Cancelar"):
                                st.session_state.sub_accion_produccion = None
                                st.rerun()
                        with col_save:
                            if st.form_submit_button("Registrar", type="primary"):
                                if fp_peso > 0:
                                    datos_peso = [str(fp_fecha), "PESAJE", animal_id, str(fp_peso), fp_alim, fp_notas]
                                    guardar_evento(sh, datos_peso, "Pesaje")
                                    st.session_state.sub_accion_produccion = None
                                    st.rerun()
                                else: st.error("El peso debe ser mayor a 0")

                elif st.session_state.sub_accion_produccion == 'add_leche':
                    st.subheader("Registrar Leche")
                    with st.form("form_leche_app"):
                        c_fl1, c_fl2 = st.columns(2)
                        with c_fl1: fl_fecha = st.date_input("Fecha *", date.today())
                        with c_fl2: fl_periodo = st.selectbox("Periodo del día", ["Mañana", "Tarde", "Todo el día"])
                        
                        st.markdown("**Datos de producción**")
                        c_fl3, c_fl4 = st.columns(2)
                        with c_fl3: fl_conc = st.number_input("Concentrado (kg)", min_value=0.0)
                        with c_fl4: fl_litros = st.number_input("Leche (L) *", min_value=0.0)
                        
                        st.markdown("**Datos complementarios**")
                        c_fl5, c_fl6 = st.columns(2)
                        with c_fl5: fl_hato = st.selectbox("Hato de ordeño", ["Hato Principal", "Hato Enfermería", "Hato Seco"])
                        with c_fl6: fl_potrero = st.selectbox("Potrero", ["Potrero 1", "Potrero 2", "Potrero 3", "Establo"])
                        
                        col_cancel_l, col_save_l = st.columns(2)
                        with col_cancel_l:
                            if st.form_submit_button("Cancelar"):
                                st.session_state.sub_accion_produccion = None
                                st.rerun()
                        with col_save_l:
                            if st.form_submit_button("Registrar", type="primary"):
                                if fl_litros >= 0:
                                    det_2 = f"{fl_periodo} | Conc: {fl_conc}kg"
                                    notas_l = f"Hato: {fl_hato} | Potrero: {fl_potrero}"
                                    datos_leche = [str(fl_fecha), "PRODUCCION_LECHE", animal_id, str(fl_litros), det_2, notas_l]
                                    guardar_evento(sh, datos_leche, "Registro Leche")
                                    st.session_state.sub_accion_produccion = None
                                    st.rerun()
                                else: st.error("Verifica los litros")

            # --- VISTA 5: VETERINARIA ---
            elif st.session_state.nav_gestion == 'veterinaria':
                animal_id = st.session_state.animal_seleccionado
                datos = df[df["ID"] == animal_id].iloc[0]

                st.markdown(f"""
                <div style='background-color: #2e7d32; padding: 15px; border-radius: 10px; color: white; margin-bottom: 20px;'>
                    <h3 style='margin:0;'>Chequeo veterinario: {datos['Nombre']}</h3>
                </div>
                """, unsafe_allow_html=True)

                if st.button("⬅️ Volver al Perfil", key="btn_back_vet"):
                    ir_a_perfil(animal_id)
                    st.rerun()

                if st.session_state.sub_accion_veterinaria is None:
                    
                    col_v1, col_v2 = st.columns(2)
                    with col_v1:
                        if st.button("🩺 Tratamiento", use_container_width=True):
                            st.session_state.sub_accion_veterinaria = 'tratamiento'
                            st.rerun()
                        st.write("")
                        if st.button("🔴 Mastitis", use_container_width=True): 
                            st.session_state.sub_accion_veterinaria = 'mastitis'
                            st.rerun()
                        st.write("")
                        st.button("🕒 Crear Evento", use_container_width=True) # Sin acción
                        
                    with col_v2:
                        if st.button("💉 Vacunación", use_container_width=True):
                            st.session_state.sub_accion_veterinaria = 'vacuna'
                            st.rerun()
                        st.write("")
                        if st.button("🐮 Muerte", use_container_width=True):
                            st.session_state.sub_accion_veterinaria = 'muerte'
                            st.rerun()

                    # HISTORIAL VETERINARIO
                    st.markdown("<br><h5>📋 Historial Clínico</h5>", unsafe_allow_html=True)
                    
                    df_vaca_hist = pd.DataFrame()
                    if not df_hist.empty:
                        df_hist["ID Animal"] = df_hist["ID Animal"].astype(str)
                        df_vaca_hist = df_hist[df_hist["ID Animal"] == str(animal_id)]
                    
                    hist_vet = pd.DataFrame()
                    if not df_vaca_hist.empty:
                        hist_vet = df_vaca_hist[df_vaca_hist["Tipo Evento"].isin(["TRATAMIENTO", "VACUNACION", "MASTITIS", "MUERTE"])]
                    
                    if hist_vet.empty:
                        st.markdown("""
                        <div class="empty-state">
                            <div style="font-size: 30px; color: #aaa; margin-bottom: 10px;">ℹ️</div>
                            <p>No hay historial clínico registrado</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        for idx, row in hist_vet.iloc[::-1].iterrows():
                            emoji_tipo = "🩺"
                            titulo_evento = row['Tipo Evento']
                            
                            if row['Tipo Evento'] == "VACUNACION":
                                emoji_tipo = "💉"
                                titulo_evento = "Vacunación"
                            elif row['Tipo Evento'] == "TRATAMIENTO":
                                emoji_tipo = "💊"
                                titulo_evento = "Tratamiento"
                            elif row['Tipo Evento'] == "MASTITIS":
                                emoji_tipo = "🔴"
                                titulo_evento = "Mastitis"
                            elif row['Tipo Evento'] == "MUERTE":
                                emoji_tipo = "💀"
                                titulo_evento = "Muerte"
                            
                            st.markdown(f"""
                            <div class="vet-card">
                                <strong>{emoji_tipo} {titulo_evento} - {row['Fecha']}</strong><br>
                                <span style="color:#555;">{row['Detalle 1']}</span><br>
                                <span style="color:#777; font-size: 0.9em;">{row['Detalle 2']}</span>
                                <div style="font-size: 0.8em; color: #999; margin-top: 5px;">{row['Notas']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    if st.button("➕ Registro Rápido", type="primary"):
                        st.toast("Usa los botones de arriba para agregar registros.")

                elif st.session_state.sub_accion_veterinaria == 'tratamiento':
                    st.subheader("Nuevo Tratamiento")
                    with st.form("form_tratamiento_vet"):
                        ft_nombre = st.text_input("Nombre del tratamiento")
                        c_vt1, c_vt2 = st.columns(2)
                        with c_vt1: ft_fecha = st.date_input("Fecha *", date.today())
                        with c_vt2: ft_dias = st.number_input("Días de tratamiento", min_value=1, step=1)
                        c_vt3, c_vt4 = st.columns(2)
                        with c_vt3: ft_tipo = st.selectbox("Tipo de Trat... *", TIPOS_TRATAMIENTO)
                        with c_vt4: ft_enfermedad = st.selectbox("Enfermedad", LISTA_ENFERMEDADES)
                        ft_diagnostico = st.text_input("Diagnóstico")
                        ft_medicamento = st.text_input("Medicamento *")
                        ft_notas = st.text_area("Notas y observaciones")
                        
                        col_cancel_t, col_save_t = st.columns(2)
                        with col_cancel_t:
                            if st.form_submit_button("Cancelar"):
                                st.session_state.sub_accion_veterinaria = None
                                st.rerun()
                        with col_save_t:
                            if st.form_submit_button("Registrar", type="primary"):
                                if ft_medicamento:
                                    d1 = f"{ft_tipo} | {ft_enfermedad}"
                                    d2 = f"{ft_medicamento} | {ft_dias} días"
                                    notas_f = f"Diag: {ft_diagnostico} | {ft_notas}"
                                    datos_vet = [str(ft_fecha), "TRATAMIENTO", animal_id, d1, d2, notas_f]
                                    guardar_evento(sh, datos_vet, "Tratamiento")
                                    st.session_state.sub_accion_veterinaria = None
                                    st.rerun()
                                else: st.error("El medicamento es obligatorio")

                elif st.session_state.sub_accion_veterinaria == 'vacuna':
                    st.subheader("Agregar Vacuna")
                    with st.form("form_vacuna_vet"):
                        fv_fecha = st.date_input("Fecha *", date.today())
                        fv_vacuna = st.selectbox("Vacuna *", LISTA_VACUNAS)
                        fv_notas = st.text_area("Notas y observaciones")
                        
                        col_cancel_v, col_save_v = st.columns(2)
                        with col_cancel_v:
                            if st.form_submit_button("Cancelar"):
                                st.session_state.sub_accion_veterinaria = None
                                st.rerun()
                        with col_save_v:
                            if st.form_submit_button("Registrar", type="primary"):
                                datos_vac = [str(fv_fecha), "VACUNACION", animal_id, fv_vacuna, "", fv_notas]
                                guardar_evento(sh, datos_vac, "Vacunación")
                                st.session_state.sub_accion_veterinaria = None
                                st.rerun()

                elif st.session_state.sub_accion_veterinaria == 'mastitis':
                    st.subheader("Registrar Mastitis")
                    with st.form("form_mastitis_vet"):
                        fm_fecha = st.date_input("Fecha *", date.today())
                        st.write("Ubres infectadas")
                        c_m_left, c_m_center, c_m_right = st.columns([2, 2, 2])
                        with c_m_left:
                            u1 = st.selectbox("Ubre 1 (Izq-Del)", GRADOS_MASTITIS)
                            u3 = st.selectbox("Ubre 3 (Izq-Tras)", GRADOS_MASTITIS)
                        with c_m_center:
                            st.markdown("""
                            <div class="ubre-box">
                                <div class="ubre-row">
                                    <div class="ubre-num">1</div>
                                    <div class="ubre-num">2</div>
                                </div>
                                <div class="ubre-row">
                                    <div class="ubre-num">3</div>
                                    <div class="ubre-num">4</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        with c_m_right:
                            u2 = st.selectbox("Ubre 2 (Der-Del)", GRADOS_MASTITIS)
                            u4 = st.selectbox("Ubre 4 (Der-Tras)", GRADOS_MASTITIS)
                        fm_notas = st.text_area("Notas y observaciones")
                        fm_tratamiento = st.checkbox("Poner en tratamiento")
                        col_cancel_m, col_save_m = st.columns(2)
                        with col_cancel_m:
                            if st.form_submit_button("Cancelar"):
                                st.session_state.sub_accion_veterinaria = None
                                st.rerun()
                        with col_save_m:
                            if st.form_submit_button("Registrar", type="primary"):
                                if u1 != "-" or u2 != "-" or u3 != "-" or u4 != "-":
                                    afectadas = []
                                    if u1 != "-": afectadas.append(f"U1:{u1[0]}")
                                    if u2 != "-": afectadas.append(f"U2:{u2[0]}")
                                    if u3 != "-": afectadas.append(f"U3:{u3[0]}")
                                    if u4 != "-": afectadas.append(f"U4:{u4[0]}")
                                    det_1_m = ", ".join(afectadas)
                                    det_2_m = "En Tratamiento" if fm_tratamiento else "Sin tratamiento inmediato"
                                    datos_mas = [str(fm_fecha), "MASTITIS", animal_id, det_1_m, det_2_m, fm_notas]
                                    guardar_evento(sh, datos_mas, "Mastitis")
                                    st.session_state.sub_accion_veterinaria = None
                                    st.rerun()
                                else: st.error("Selecciona el grado de mastitis en al menos una ubre.")

                elif st.session_state.sub_accion_veterinaria == 'muerte':
                    st.subheader("Registrar Muerte")
                    with st.form("form_muerte_vet"):
                        fmu_fecha = st.date_input("Fecha *", date.today())
                        fmu_causa = st.selectbox("Causa de muerte *", CAUSAS_MUERTE)
                        fmu_notas = st.text_area("Notas y observaciones")
                        col_cancel_mu, col_save_mu = st.columns(2)
                        with col_cancel_mu:
                            if st.form_submit_button("Cancelar"):
                                st.session_state.sub_accion_veterinaria = None
                                st.rerun()
                        with col_save_mu:
                            if st.form_submit_button("Registrar", type="primary"):
                                datos_muerte = [str(fmu_fecha), "MUERTE", animal_id, fmu_causa, "", fmu_notas]
                                guardar_evento(sh, datos_muerte, "Muerte")
                                st.session_state.sub_accion_veterinaria = None
                                st.rerun()

            # --- VISTA 6: REPRODUCCIÓN (CON ABORTO Y PARTO CORREGIDO) ---
            elif st.session_state.nav_gestion == 'reproduccion':
                animal_id = st.session_state.animal_seleccionado
                datos = df[df["ID"] == animal_id].iloc[0]

                if st.button("⬅️ Volver al Perfil", key="btn_back_repro"):
                    ir_a_perfil(animal_id)
                    st.rerun()

                # LOGICA ESTADÍSTICAS REPRO
                df_vaca_hist = pd.DataFrame()
                if not df_hist.empty:
                    df_hist["ID Animal"] = df_hist["ID Animal"].astype(str)
                    df_vaca_hist = df_hist[df_hist["ID Animal"] == str(animal_id)]
                
                ultimo_parto_str = "--"
                dias_abiertos = "--"

                if not df_vaca_hist.empty:
                    partos = df_vaca_hist[df_vaca_hist["Tipo Evento"] == "PARTO"]
                    if not partos.empty:
                        ultimo_parto_str = partos.iloc[-1]["Fecha"]
                        try:
                            f_parto = datetime.strptime(ultimo_parto_str, "%Y-%m-%d").date()
                            if datos['Estado'] != "Preñada":
                                dias_abiertos = (date.today() - f_parto).days
                        except: pass

                # Header Verde
                st.markdown(f"""
                <div class="repro-stats">
                    <h3>Estado reproductivo</h3>
                    <div class="stat-row">
                        <span>Último parto</span>
                        <strong>{ultimo_parto_str}</strong>
                    </div>
                    <div class="stat-row">
                        <span>Estado</span>
                        <strong>{datos['Estado']}</strong>
                    </div>
                    <div class="stat-row" style="border:none;">
                        <span>Días abiertos</span>
                        <strong>{dias_abiertos} día(s)</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.session_state.sub_accion_reproduccion is None:
                    col_r1, col_r2 = st.columns(2)
                    with col_r1:
                        if st.button("🐮 Fecundación", use_container_width=True):
                            st.session_state.sub_accion_reproduccion = 'fecundacion'
                            st.rerun()
                        st.write("")
                        if st.button("🏥 Parto", use_container_width=True):
                            st.session_state.sub_accion_reproduccion = 'parto'
                            st.rerun()
                        st.write("")
                        st.button("🕒 Crear Evento", use_container_width=True) 
                    with col_r2:
                        if st.button("🔍 Chequeo", use_container_width=True):
                            st.session_state.sub_accion_reproduccion = 'chequeo'
                            st.rerun()
                        st.write("")
                        # === BOTÓN MODIFICADO PARA ABORTO ===
                        if st.button("⚠️ Aborto", use_container_width=True): 
                            st.session_state.sub_accion_reproduccion = 'aborto'
                            st.rerun()

                    st.write("")
                    st.markdown("**Partos/Abortos**")
                    hist_partos = pd.DataFrame()
                    if not df_vaca_hist.empty:
                        hist_partos = df_vaca_hist[df_vaca_hist["Tipo Evento"].isin(["PARTO", "ABORTO"])]

                    st.markdown("""
                    <div class="tabla-header">
                        <div style="width:25%">Fecha</div>
                        <div style="width:25%">Tipo</div>
                        <div style="width:25%">Género</div>
                        <div style="width:25%">Cría</div>
                    </div>
                    """, unsafe_allow_html=True)

                    if not hist_partos.empty:
                        for idx, row in hist_partos.iloc[::-1].iterrows():
                            genero = "--"
                            cria_txt = "--"
                            try:
                                d1 = row['Detalle 1']
                                d2 = row['Detalle 2']
                                if "Macho" in d1: genero = "Macho"
                                elif "Hembra" in d1: genero = "Hembra"
                                if "ID Cría:" in d2: cria_txt = d2.replace("ID Cría:", "").strip()
                            except: pass
                            tipo_txt = "Parto" if row['Tipo Evento'] == "PARTO" else "Aborto"
                            st.markdown(f"""
                            <div class="tabla-row">
                                <div style="width:25%">{row['Fecha']}</div>
                                <div style="width:25%">{tipo_txt}</div>
                                <div style="width:25%">{genero}</div>
                                <div style="width:25%">{cria_txt}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else: st.info("No hay partos registrados.")

                    st.markdown("<br><h5>📋 Historial Completo</h5>", unsafe_allow_html=True)
                    hist_repro = pd.DataFrame()
                    if not df_vaca_hist.empty:
                        hist_repro = df_vaca_hist[df_vaca_hist["Tipo Evento"].isin(["FECUNDACION", "PARTO", "ABORTO", "CHEQUEO_REPRO"])]
                    if hist_repro.empty:
                        st.markdown("""<div class="empty-state"><p>No hay historial reproductivo</p></div>""", unsafe_allow_html=True)
                    else:
                        for idx, row in hist_repro.iloc[::-1].iterrows():
                            emoji_tipo = "🧬"
                            titulo_evento = row['Tipo Evento']
                            if row['Tipo Evento'] == "FECUNDACION": emoji_tipo = "❤️"; titulo_evento = "Fecundación"
                            elif row['Tipo Evento'] == "CHEQUEO_REPRO": emoji_tipo = "🔍"; titulo_evento = "Chequeo"
                            elif row['Tipo Evento'] == "PARTO": emoji_tipo = "🎉"; titulo_evento = "Parto"
                            elif row['Tipo Evento'] == "ABORTO": emoji_tipo = "⚠️"; titulo_evento = "Aborto"
                            
                            st.markdown(f"""
                            <div class="repro-card">
                                <strong>{emoji_tipo} {titulo_evento} - {row['Fecha']}</strong><br>
                                <span style="color:#555;">{row['Detalle 1']}</span><br>
                                <span style="color:#777; font-size: 0.9em;">{row['Detalle 2']}</span>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    if st.button("➕ Registro Rápido", type="primary", key="btn_add_repro"):
                        st.toast("Usa los botones de arriba para agregar registros.")

                # --- FORMULARIOS DE REPRODUCCIÓN ---
                elif st.session_state.sub_accion_reproduccion == 'fecundacion':
                    st.subheader("Nueva Fecundación")
                    c_f1, c_f2 = st.columns(2)
                    with c_f1: ff_fecha = st.date_input("Fecha *", date.today())
                    with c_f2: tipo_seleccionado = st.selectbox("Tipo de Fecundación *", TIPOS_FECUNDACION, index=0)
                    with st.form("form_fecundacion_dinamico"):
                        ff_padre_select = ""; ff_padre_manual = ""; ff_pajilla = ""; ff_madre_select = ""
                        if tipo_seleccionado == "Monta":
                            lista_toros = []
                            if not df_activos.empty:
                                df_machos = df_activos[(df_activos['Sexo'] == 'Macho') | (df_activos['Tipo'] == 'Toro')]
                                if not df_machos.empty: lista_toros = df_machos['Nombre'].tolist()
                            opciones_padre = lista_toros + ["Otro / Externo"]
                            ff_padre_select = st.selectbox("Padre (Toro)", opciones_padre)
                            if ff_padre_select == "Otro / Externo": ff_padre_manual = st.text_input("Nombre del Toro (si es externo)")
                        elif tipo_seleccionado == "Inseminación artificial":
                            lista_toros = []
                            if not df_activos.empty:
                                df_machos = df_activos[(df_activos['Sexo'] == 'Macho') | (df_activos['Tipo'] == 'Toro')]
                                if not df_machos.empty: lista_toros = df_machos['Nombre'].tolist()
                            opciones_padre = lista_toros + ["Otro / Externo"]
                            ff_padre_select = st.selectbox("Padre (Toro)", opciones_padre)
                            if ff_padre_select == "Otro / Externo": ff_padre_manual = st.text_input("Nombre del Toro (si es externo)")
                            ff_pajilla = st.text_input("Número de pajilla")
                        elif tipo_seleccionado == "Transferencia de embriones":
                            lista_toros = []
                            if not df_activos.empty:
                                df_machos = df_activos[(df_activos['Sexo'] == 'Macho') | (df_activos['Tipo'] == 'Toro')]
                                if not df_machos.empty: lista_toros = df_machos['Nombre'].tolist()
                            opciones_padre = lista_toros + ["Otro / Externo"]
                            ff_padre_select = st.selectbox("Padre (Toro)", opciones_padre)
                            if ff_padre_select == "Otro / Externo": ff_padre_manual = st.text_input("Nombre del Toro (si es externo)")
                            lista_vacas = []
                            if not df_activos.empty:
                                df_hembras = df_activos[(df_activos['Sexo'] == 'Hembra') & (df_activos['ID'] != str(animal_id))]
                                if not df_hembras.empty: lista_vacas = df_hembras['Nombre'].tolist()
                            ff_madre_select = st.selectbox("Madre Donadora", lista_vacas)
                        ff_notas = st.text_area("Notas y observaciones")
                        col_cancel_f, col_save_f = st.columns(2)
                        with col_cancel_f:
                            if st.form_submit_button("Cancelar"): st.session_state.sub_accion_reproduccion = None; st.rerun()
                        with col_save_f:
                            if st.form_submit_button("Registrar", type="primary"):
                                padre_final = ff_padre_manual if ff_padre_select == "Otro / Externo" else ff_padre_select
                                if not padre_final: padre_final = "No esp."
                                detalle_info = f"Padre: {padre_final}"
                                if tipo_seleccionado == "Inseminación artificial": detalle_info += f" | Pajilla: {ff_pajilla}"
                                elif tipo_seleccionado == "Transferencia de embriones": detalle_info += f" | Donadora: {ff_madre_select}"
                                datos_fec = [str(date.today()), "FECUNDACION", animal_id, tipo_seleccionado, detalle_info, ff_notas]
                                guardar_evento(sh, datos_fec, "Fecundación")
                                st.session_state.sub_accion_reproduccion = None
                                st.rerun()

                elif st.session_state.sub_accion_reproduccion == 'chequeo':
                    st.subheader("Nuevo Chequeo")
                    with st.form("form_chequeo_repro"):
                        fc_fecha = st.date_input("Fecha *", date.today())
                        fc_res = st.selectbox("Resultado", ["No preñada", "Preñada"])
                        fc_notas = st.text_area("Notas y observaciones")
                        col_cancel_c, col_save_c = st.columns(2)
                        with col_cancel_c:
                            if st.form_submit_button("Cancelar"): st.session_state.sub_accion_reproduccion = None; st.rerun()
                        with col_save_c:
                            if st.form_submit_button("Registrar", type="primary"):
                                datos_cheq = [str(fc_fecha), "CHEQUEO_REPRO", animal_id, fc_res, "", fc_notas]
                                guardar_evento(sh, datos_cheq, "Chequeo")
                                if fc_res == "Preñada":
                                    cambiar_estado_animal(hoja_animales, animal_id, "Preñada")
                                    st.success("¡Estado actualizado a PREÑADA!")
                                    time.sleep(1)
                                st.session_state.sub_accion_reproduccion = None
                                st.rerun()

                elif st.session_state.sub_accion_reproduccion == 'parto':
                    st.subheader("Crear animal (Nacimiento)")
                    with st.form("form_parto_cria"):
                        st.markdown("<h3 style='text-align: center;'>🐮 🐴 🐷</h3>", unsafe_allow_html=True)
                        fp_sexo = st.radio("Sexo de la cría", ["Macho", "Hembra"], horizontal=True)
                        fp_nombre = st.text_input("Nombre del animal")
                        c_p1, c_p2 = st.columns(2)
                        with c_p1: fp_id = st.text_input("Número del animal (ID)*")
                        with c_p2: fp_nac = st.date_input("Fecha de nacimiento", date.today())
                        c_p3, c_p4 = st.columns(2)
                        with c_p3: fp_raza = st.selectbox("Raza *", ["Brahman", "Gyr", "Holstein", "Mestizo", "Senepol", "Otro"])
                        with c_p4: 
                            st.write("¿Esta en la finca?")
                            fp_finca = st.checkbox("Sí", value=True)
                        col_cancel_p, col_save_p = st.columns(2)
                        with col_cancel_p:
                            if st.form_submit_button("Cancelar"): st.session_state.sub_accion_reproduccion = None; st.rerun()
                        with col_save_p:
                            if st.form_submit_button("Crear (Registrar Parto)", type="primary"):
                                if fp_id:
                                    if fp_id in lista_ids_todos:
                                        st.error("¡Ese ID ya existe!")
                                    else:
                                        datos_cria = [fp_id, "Becerro", fp_nombre, "", fp_raza, fp_sexo, "0", str(fp_nac), "Sano", "Sin Foto"]
                                        guardar_animal(hoja_animales, datos_cria, rerun=False)
                                        detalle_parto = f"Cría: {fp_nombre} ({fp_sexo})"
                                        datos_evento_parto = [str(fp_nac), "PARTO", animal_id, detalle_parto, f"ID Cría: {fp_id}", "Parto normal"]
                                        guardar_evento(sh, datos_evento_parto, "Parto")
                                        cambiar_estado_animal(hoja_animales, animal_id, "Lactancia")
                                        st.success("¡Nacimiento registrado con éxito!")
                                        time.sleep(2)
                                        st.session_state.sub_accion_reproduccion = None
                                        st.rerun()
                                else: st.error("El ID del animal es obligatorio.")

                elif st.session_state.sub_accion_reproduccion == 'aborto':
                    st.markdown(f"""
                    <div style='background-color: #2e7d32; padding: 10px; border-radius: 5px 5px 0 0; color: white; text-align: center;'>
                        <h3 style='margin:0;'>✖ Nuevo Aborto</h3>
                    </div>
                    <div style='background-color: #e8f5e9; padding: 5px; text-align: center; margin-bottom: 20px; font-weight: bold;'>
                        🐮 {datos['Nombre']}
                    </div>
                    """, unsafe_allow_html=True)
                    with st.form("form_aborto"):
                        fa_sexo = st.radio("Sexo del feto (si se identifica)", ["Macho", "Hembra"], horizontal=True)
                        fa_fecha = st.date_input("Fecha del suceso *", date.today())
                        fa_notas = st.text_area("Notas y observaciones")
                        col_cancel_a, col_save_a = st.columns(2)
                        with col_cancel_a:
                            if st.form_submit_button("Cancelar"): st.session_state.sub_accion_reproduccion = None; st.rerun()
                        with col_save_a:
                            if st.form_submit_button("Registrar", type="primary"):
                                datos_aborto = [str(fa_fecha), "ABORTO", animal_id, f"Feto: {fa_sexo}", "Pérdida gestacional", fa_notas]
                                guardar_evento(sh, datos_aborto, "Aborto")
                                cambiar_estado_animal(hoja_animales, animal_id, "Sano")
                                st.error("Aborto registrado. Estado: Vacía (Sano).")
                                time.sleep(2)
                                st.session_state.sub_accion_reproduccion = None
                                st.rerun()

            # --- VISTA 4: DATOS GENERALES ---
            elif st.session_state.nav_gestion == 'detalle':
                animal_id = st.session_state.animal_seleccionado
                datos = df[df["ID"] == animal_id].iloc[0]

                col_back, col_tit = st.columns([1, 5])
                with col_back:
                    if st.button("⬅️"):
                        ir_a_perfil(animal_id)
                        st.rerun()
                with col_tit:
                    st.subheader("Datos generales")

                with st.container(border=True):
                    # Datos básicos
                    st.text_input("Nombre", value=datos['Nombre'], disabled=True)
                    st.text_input("ID", value=datos['ID'], disabled=True)
                    st.text_input("Raza", value=datos['Raza'], disabled=True)
                    st.text_input("Sexo", value=datos['Sexo'], disabled=True)
                    
                    # Intentamos mostrar datos extendidos si existen
                    padre_txt = datos.get("Padre", "--") if "Padre" in datos else "--"
                    madre_txt = datos.get("Madre", "--") if "Madre" in datos else "--"
                    
                    c_padres1, c_padres2 = st.columns(2)
                    with c_padres1: st.text_input("Padre", value=padre_txt, disabled=True)
                    with c_padres2: st.text_input("Madre", value=madre_txt, disabled=True)
                    
                    notas_txt = datos.get("Notas", "") if "Notas" in datos else ""
                    if notas_txt:
                        st.text_area("Notas registradas", value=notas_txt, disabled=True)

                with st.expander("✏️ Editar estos datos"):
                    with st.form("form_editar_app"):
                        e_nombre = st.text_input("Nombre", value=datos["Nombre"])
                        e_arete = st.text_input("Arete", value=datos["Arete"])
                        e_peso = st.number_input("Peso", value=float(datos["Peso"]) if datos["Peso"] else 0.0)
                        e_estado = st.selectbox("Estado", ["Sano", "Enfermo", "Preñada", "VENDIDO"], 
                                                index=["Sano", "Enfermo", "Preñada", "VENDIDO"].index(datos["Estado"]) if datos["Estado"] in ["Sano", "Enfermo", "Preñada", "VENDIDO"] else 0)
                        e_foto = st.file_uploader("Actualizar Foto", type=["jpg", "png", "jpeg"])
                        if st.form_submit_button("💾 Guardar Cambios"):
                            nuevo_link = datos.get("Foto", "Sin Foto")
                            if e_foto:
                                with st.spinner("Subiendo foto..."):
                                    nuevo_link = subir_foto_imgbb(e_foto)
                            datos_upd = [animal_id, datos["Tipo"], e_nombre, e_arete, datos["Raza"], datos["Sexo"], str(e_peso), str(datos["Nacimiento"]), e_estado, nuevo_link]
                            actualizar_animal_completo(hoja_animales, animal_id, datos_upd)
                    
                    st.write("")
                    if st.button("🗑️ Eliminar Animal"):
                            eliminar_animal_db(hoja_animales, animal_id)
                            ir_a_lista()
                            st.rerun()

        # ==========================================
        # 4. ACCIONES RÁPIDAS
        # ==========================================
        with tab_acc:
            col_a, col_b = st.columns(2)
            with col_a:
                st.button("🥛 Registro de Leche", on_click=set_accion, args=("leche",))
                st.button("🚛 Venta de Ganado", on_click=set_accion, args=("venta",))
                st.button("🧬 Evento / Celo", on_click=set_accion, args=("evento",))
            with col_b:
                st.button("⚖️ Pesaje Individual", on_click=set_accion, args=("peso",))
                st.button("💉 Sanidad / Vacuna", on_click=set_accion, args=("sanidad",))
                st.button("🐂 Compra de Ganado", on_click=set_accion, args=("compra",))

            st.markdown("---")
            
            if st.session_state.accion_activa == "venta":
                st.subheader("🚛 Nueva Venta de Ganado")
                with st.form("form_venta_completa"):
                    c_f1, c_f2 = st.columns(2)
                    with c_f1: fecha_venta = st.date_input("Fecha Venta", date.today())
                    with c_f2: fecha_envio = st.date_input("Fecha Envío", date.today())
                    st.markdown('<div class="seccion-titulo">👤 Comprador</div>', unsafe_allow_html=True)
                    c_c1, c_c2 = st.columns(2)
                    with c_c1: comp_nombre = st.text_input("Nombre/Empresa")
                    with c_c2: comp_telefono = st.text_input("Teléfono")
                    st.markdown('<div class="seccion-titulo">📍 Destino y Transporte</div>', unsafe_allow_html=True)
                    dest_ciudad = st.text_input("Ciudad / Destino / Finca")
                    with st.expander("Información del Transporte (Opcional)"):
                            c_t1, c_t2 = st.columns(2)
                            with c_t1: trans_guia = st.text_input("Nro. Guía")
                            with c_t2: trans_placa = st.text_input("Placa")
                    st.markdown('<div class="seccion-titulo">💰 Datos Económicos</div>', unsafe_allow_html=True)
                    pre_select = [st.session_state.animal_seleccionado] if st.session_state.animal_seleccionado and st.session_state.animal_seleccionado in lista_ids_activos else None
                    ids_seleccionados = st.multiselect("Animales (Activos)*", lista_ids_activos, default=pre_select)
                    c_m1, c_m2, c_m3 = st.columns([1,1,2])
                    with c_m1: moneda = st.selectbox("Moneda", ["USD", "VES", "COP"])
                    with c_m2: monto_manual = st.number_input("Precio", min_value=0.0)
                    with c_m3: tipo_precio = st.radio("Tipo:", ["Por Kilo", "Por Cabeza", "Lote"], horizontal=True)
                    notas_venta = st.text_area("Notas")
                    traslado = st.toggle("¿Trasladar a otro usuario de Control Ganadero?")
                    if st.form_submit_button("✅ CONFIRMAR VENTA", type="primary"):
                        if not ids_seleccionados: st.error("Selecciona un animal")
                        else:
                            precio_str = f"{monto_manual} {moneda} ({tipo_precio})"
                            for animal_id in ids_seleccionados:
                                detalle = f"Comp: {comp_nombre} | Dest: {dest_ciudad}"
                                notas_full = f"Guia: {trans_guia} | {notas_venta}"
                                datos_venta = [str(fecha_venta), "VENTA", animal_id, precio_str, detalle, notas_full]
                                guardar_evento(sh, datos_venta, "Venta")
                                cambiar_estado_vendido(hoja_animales, animal_id)
                            st.success("Venta registrada.")
                            if st.session_state.animal_seleccionado: ir_a_lista() 
                            time.sleep(2)
                            st.rerun()

            elif st.session_state.accion_activa == "leche":
                st.subheader("🥛 Registro Diario de Leche")
                with st.form("form_leche"):
                    f_fecha = st.date_input("Fecha", date.today())
                    c_l1, c_l2 = st.columns(2)
                    with c_l1: f_litros = st.number_input("Total Litros (L)", min_value=0.0)
                    with c_l2: f_vacas = st.number_input("Vacas Ordeñadas", min_value=1, step=1)
                    if st.form_submit_button("Guardar"):
                        datos_leche = [str(f_fecha), "PRODUCCION_LECHE", "LOTE_GENERAL", str(f_litros), str(f_vacas), ""]
                        guardar_evento(sh, datos_leche, "Registro de Leche")

            elif st.session_state.accion_activa == "peso":
                st.subheader("⚖️ Nuevo Pesaje")
                with st.form("form_peso"):
                    p_animal = st.selectbox("Animal", lista_ids_activos)
                    c_p1, c_p2 = st.columns(2)
                    with c_p1: p_fecha = st.date_input("Fecha", date.today())
                    with c_p2: p_kilos = st.number_input("Peso (kg)", min_value=0.0)
                    if st.form_submit_button("Registrar"):
                        datos_peso = [str(p_fecha), "PESAJE", p_animal, str(p_kilos), "", "Control"]
                        guardar_evento(sh, datos_peso, "Pesaje")

            elif st.session_state.accion_activa == "sanidad":
                st.subheader("💉 Registro Sanitario")
                with st.form("form_sanidad"):
                    s_animal = st.selectbox("Animal", lista_ids_activos)
                    s_tipo = st.selectbox("Tipo", ["Vacuna", "Vitaminas", "Antibiótico", "Desparasitante"])
                    s_producto = st.text_input("Producto")
                    s_notas = st.text_area("Observaciones")
                    if st.form_submit_button("Guardar"):
                        datos_sanidad = [str(date.today()), "SANIDAD", s_animal, s_tipo, s_producto, s_notas]
                        guardar_evento(sh, datos_sanidad, "Tratamiento")

            elif st.session_state.accion_activa is None:
                st.info("👆 Selecciona una opción arriba.")

        # ==========================================
        # 5. HISTORIAL VENTAS
        # ==========================================
        with tab_ventas:
            st.header("💰 Historial de Ventas")
            if not df_hist.empty and "Tipo Evento" in df_hist.columns:
                mask_venta = df_hist["Tipo Evento"].astype(str).str.contains("VENTA", case=False, na=False)
                df_ventas = df_hist[mask_venta]
                if not df_ventas.empty:
                    st.dataframe(df_ventas[["Fecha", "ID Animal", "Detalle 1", "Detalle 2"]], use_container_width=True, hide_index=True)
                else:
                    st.warning("No hay ventas registradas.")
            else:
                st.info("Sin historial.")

if __name__ == "__main__":
    main()