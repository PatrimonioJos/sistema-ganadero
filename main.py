import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import altair as alt
from datetime import date
import os # Necesario para detectar si estamos en PC o Nube

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Sistema Ganadero Élite", page_icon="🐮", layout="wide")

# --- CONEXIÓN HÍBRIDA (PC y NUBE) ---
def conectar_db():
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        
        # 1. INTENTAR MODO LOCAL (TU PC)
        if os.path.exists("credentials.json"):
            creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
        
        # 2. INTENTAR MODO NUBE (STREAMLIT CLOUD)
        elif "gcp_service_account" in st.secrets:
            # En la nube, las credenciales vienen de un diccionario secreto
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        
        else:
            st.error("❌ No se encontraron credenciales (ni archivo local ni secretos en la nube).")
            return None

        client = gspread.authorize(creds)
        sheet_id = "1292mc53ss8G8pY-azGsrpq10OR8RDX0gNMVML8LgfU0" # TU ID
        return client.open_by_key(sheet_id)
        
    except Exception as e:
        st.error(f"⚠️ Error de conexión: {e}")
        return None

# --- FUNCIONES DE GUARDADO ---
def guardar_animal(sheet, datos):
    sheet.append_row(datos)
    st.toast("✅ ¡Animal registrado!", icon="🐮")
    st.balloons()

def guardar_evento(sh, datos, tipo_evento):
    try:
        worksheet = sh.worksheet("Historial")
    except:
        worksheet = sh.add_worksheet(title="Historial", rows="1000", cols="10")
        worksheet.append_row(["Fecha", "Tipo Evento", "ID Animal", "Detalle 1", "Detalle 2", "Notas"])
    
    worksheet.append_row(datos)
    st.toast(f"✅ {tipo_evento} registrado exitosamente", icon="📝")

# --- APP PRINCIPAL ---
def main():
    st.title("🧬 Control Ganadero - Génesis")
    st.markdown("---")

    sh = conectar_db()
    
    if sh:
        # Usamos la Hoja 1 (Inventario) para leer datos
        hoja_animales = sh.get_worksheet(0)
        
        try:
            data = hoja_animales.get_all_records()
            df = pd.DataFrame(data)
            lista_ids = df["ID"].astype(str).tolist() if not df.empty and "ID" in df.columns else []
        except:
            df = pd.DataFrame()
            lista_ids = []

        # --- NAVEGACIÓN PRINCIPAL ---
        tab_dash, tab_reg, tab_inv, tab_acc = st.tabs(["📊 DASHBOARD", "📝 CREAR ANIMAL", "🔎 BUSCADOR", "⚡ ACCIONES RÁPIDAS"])

        # ==========================================
        # 1. DASHBOARD
        # ==========================================
        with tab_dash:
            if not df.empty:
                with st.container(border=True):
                    col_finca1, col_finca2 = st.columns([1, 3])
                    with col_finca1:
                        st.image("https://cdn-icons-png.flaticon.com/512/2173/2173516.png", width=80)
                    with col_finca2:
                        st.subheader("Hacienda Génesis")
                        st.caption("Resumen general del hato")
                        st.progress(0.7, text="Capacidad de carga: 70%")

                col_graf, col_stats = st.columns([1, 1])
                with col_graf:
                    with st.container(border=True):
                        st.subheader("Distribución")
                        if "Tipo" in df.columns:
                            base = alt.Chart(df).encode(theta=alt.Theta("count()", stack=True))
                            pie = base.mark_arc(outerRadius=100, innerRadius=60).encode(
                                color=alt.Color("Tipo"),
                                order=alt.Order("Tipo", sort="descending"),
                                tooltip=["Tipo", "count()"]
                            )
                            st.altair_chart(pie, use_container_width=True)

                with col_stats:
                    with st.container(border=True):
                        st.subheader("Indicadores")
                        total = len(df)
                        machos = len(df[df["Sexo"] == "Macho"]) if "Sexo" in df.columns else 0
                        hembras = len(df[df["Sexo"] == "Hembra"]) if "Sexo" in df.columns else 0
                        st.metric("Total Animales", total)
                        st.metric("Hembras / Machos", f"{hembras} / {machos}")
            else:
                st.info("👋 Registra animales para ver el tablero.")

        # ==========================================
        # 2. CREAR ANIMAL
        # ==========================================
        with tab_reg:
            st.info("Ficha de Ingreso")
            with st.form("ficha_tecnica", clear_on_submit=True):
                c1, c2, c3, c4 = st.columns(4)
                with c1: id_animal = st.text_input("Código / ID*")
                with c2: arete = st.text_input("Arete")
                with c3: nombre = st.text_input("Nombre")
                with c4: sexo = st.radio("Sexo", ["Hembra", "Macho"], horizontal=True)
                
                st.markdown("---")
                g1, g2, g3 = st.columns(3)
                with g1: raza = st.selectbox("Raza", ["Brahman", "Gyr", "Holstein", "Mestizo", "Senepol", "Otro"])
                with g2: tipo = st.selectbox("Categoría", ["Vaca", "Toro", "Novilla", "Becerro"])
                with g3: estado = st.selectbox("Estado", ["Sano", "Enfermo", "Preñada", "Vendido"])

                st.markdown("---")
                p1, p2, p3 = st.columns(3)
                with p1: peso = st.number_input("Peso (kg)*", min_value=0.0)
                with p2: fecha_nac = st.date_input("Nacimiento")
                with p3: foto = st.file_uploader("Foto")

                if st.form_submit_button("💾 GUARDAR", type="primary"):
                    if not id_animal:
                        st.error("El ID es obligatorio")
                    else:
                        nom_foto = foto.name if foto else "Sin Foto"
                        datos = [id_animal, tipo, nombre, arete, raza, sexo, str(peso), str(fecha_nac), estado, nom_foto]
                        guardar_animal(hoja_animales, datos)
                        st.rerun()

        # ==========================================
        # 3. BUSCADOR
        # ==========================================
        with tab_inv:
            st.subheader("Inventario")
            if not df.empty:
                busqueda = st.text_input("🔍 Buscar animal:")
                if busqueda:
                    mask = df.apply(lambda x: x.astype(str).str.contains(busqueda, case=False)).any(axis=1)
                    st.dataframe(df[mask], use_container_width=True)
                else:
                    st.dataframe(df, use_container_width=True)

        # ==========================================
        # 4. ⚡ ACCIONES RÁPIDAS
        # ==========================================
        with tab_acc:
            st.header("¿Qué quieres hacer hoy?")
            
            st.markdown("""
            <style>
            div.stButton > button {
                width: 100%;
                height: 80px;
                font-size: 20px;
                border-radius: 10px;
                border: 1px solid #ddd;
            }
            </style>
            """, unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            
            with col_a:
                btn_leche = st.button("🥛 Registro de Leche")
                btn_venta = st.button("🚛 Venta de Ganado")
                btn_evento = st.button("🧬 Evento / Celo")
                
            with col_b:
                btn_peso = st.button("⚖️ Pesaje con Báscula")
                btn_sanidad = st.button("💉 Tratamiento / Vacuna")
                btn_compra = st.button("🐂 Compra de Ganado")

            st.markdown("---")

            if btn_leche:
                st.subheader("🥛 Registro Diario de Leche")
                with st.form("form_leche"):
                    f_fecha = st.date_input("Fecha", date.today())
                    f_litros = st.number_input("Total Litros (L)", min_value=0.0)
                    f_vacas = st.number_input("Vacas Ordeñadas", min_value=1, step=1)
                    if st.form_submit_button("Guardar Producción"):
                        datos_leche = [str(f_fecha), "PRODUCCION_LECHE", "LOTE_GENERAL", str(f_litros), str(f_vacas), ""]
                        guardar_evento(sh, datos_leche, "Registro de Leche")

            elif btn_peso:
                st.subheader("⚖️ Nuevo Pesaje Individual")
                with st.form("form_peso"):
                    p_animal = st.selectbox("Seleccione Animal", lista_ids)
                    p_fecha = st.date_input("Fecha Pesaje", date.today())
                    p_kilos = st.number_input("Nuevo Peso (kg)", min_value=0.0)
                    if st.form_submit_button("Registrar Peso"):
                        datos_peso = [str(p_fecha), "PESAJE", p_animal, str(p_kilos), "", "Control de crecimiento"]
                        guardar_evento(sh, datos_peso, "Pesaje")

            elif btn_sanidad:
                st.subheader("💉 Registro Sanitario")
                with st.form("form_sanidad"):
                    s_animal = st.selectbox("Animal", lista_ids)
                    s_tipo = st.selectbox("Tipo", ["Vacuna", "Vitaminas", "Antibiótico", "Desparasitante"])
                    s_producto = st.text_input("Producto Aplicado")
                    s_notas = st.text_area("Observaciones")
                    if st.form_submit_button("Guardar Tratamiento"):
                        datos_sanidad = [str(date.today()), "SANIDAD", s_animal, s_tipo, s_producto, s_notas]
                        guardar_evento(sh, datos_sanidad, "Tratamiento")
            else:
                st.info("👆 Selecciona una opción arriba.")

if __name__ == "__main__":
    main()