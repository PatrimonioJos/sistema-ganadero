import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import altair as alt
from datetime import date
import os
import time
import requests # Necesario para ImgBB

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Sistema Ganadero Élite", page_icon="🐮", layout="wide")

# --- 🔑 TU CLAVE DE IMGBB (YA INTEGRADA) ---
API_KEY_IMGBB = "a2e56c54a8b85f305651768ba9403148"

# --- ESTILOS CSS ---
st.markdown("""
<style>
    div.stButton > button {
        width: 100%;
        height: 50px;
        font-size: 16px;
        border-radius: 8px;
    }
    .seccion-titulo {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin-top: 20px;
        margin-bottom: 10px;
        font-weight: bold;
        color: #31333F;
    }
    div.stButton > button:first-child {
        font-weight: bold;
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
        # TU ID DE HOJA DE CALCULO
        sheet_id = "1292mc53ss8G8pY-azGsrpq10OR8RDX0gNMVML8LgfU0" 
        return client.open_by_key(sheet_id)
    except Exception as e:
        st.error(f"⚠️ Error conectando con Google Sheets: {e}")
        return None

# --- FUNCIÓN: SUBIR A IMGBB ---
def subir_foto_imgbb(archivo):
    """Sube la foto a ImgBB y devuelve el enlace público"""
    if archivo is None:
        return "Sin Foto"
    
    try:
        url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": API_KEY_IMGBB,
            "expiration": 0 # No expira nunca
        }
        files = {
            "image": archivo.getvalue()
        }
        
        response = requests.post(url, data=payload, files=files)
        
        if response.status_code == 200:
            json_data = response.json()
            return json_data["data"]["url"] # Retorna el link directo
        else:
            st.error(f"Error ImgBB: {response.text}")
            return "Error"
            
    except Exception as e:
        st.error(f"Error de conexión al subir imagen: {e}")
        return "Error"

# --- FUNCIONES DE BASE DE DATOS (CRUD) ---
def guardar_animal(sheet, datos):
    sheet.append_row(datos)
    st.toast("✅ ¡Animal registrado!", icon="🐮")
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
    st.toast(f"✅ {tipo_evento} registrado exitosamente", icon="📝")

def encontrar_fila_por_id(sheet, id_animal):
    try:
        columna_ids = sheet.col_values(1)
        return columna_ids.index(str(id_animal)) + 1
    except ValueError:
        return None

def cambiar_estado_vendido(sheet, id_animal):
    fila = encontrar_fila_por_id(sheet, id_animal)
    if fila:
        sheet.update_cell(fila, 9, "VENDIDO") 
        return True
    return False

def actualizar_animal_completo(sheet, id_animal, nuevos_datos):
    fila = encontrar_fila_por_id(sheet, id_animal)
    if fila:
        rango = f"A{fila}:J{fila}"
        sheet.update(rango, [nuevos_datos])
        st.success("✅ Datos actualizados correctamente")
        time.sleep(1)
        st.rerun()

def eliminar_animal_db(sheet, id_animal):
    fila = encontrar_fila_por_id(sheet, id_animal)
    if fila:
        sheet.delete_rows(fila)
        st.warning("🗑️ Animal eliminado del sistema")
        time.sleep(1)
        st.rerun()

# --- GESTIÓN DE ESTADO ---
if 'accion_activa' not in st.session_state:
    st.session_state.accion_activa = None

def set_accion(nombre_accion):
    st.session_state.accion_activa = nombre_accion

# --- APP PRINCIPAL ---
def main():
    st.title("🧬 Control Ganadero")
    st.markdown("---")

    sh = conectar_sheets()
    
    if sh:
        # 1. LEER INVENTARIO
        hoja_animales = sh.get_worksheet(0)
        try:
            data = hoja_animales.get_all_records()
            df = pd.DataFrame(data)
            
            # --- LIMPIEZA DE COLUMNAS (Corrección de errores) ---
            if not df.empty:
                df.columns = df.columns.astype(str).str.strip()
            
            if not df.empty and "ID" in df.columns:
                df["ID"] = df["ID"].astype(str)
                df_activos = df[df["Estado"] != "VENDIDO"]
                lista_ids_activos = df_activos["ID"].tolist()
                lista_ids_todos = df["ID"].tolist()
            else:
                df_activos = pd.DataFrame()
                lista_ids_activos = []
                lista_ids_todos = []
        except Exception as e:
            st.error(f"Error leyendo DB: {e}")
            df = pd.DataFrame()
            df_activos = pd.DataFrame()
            lista_ids_activos = []

        # 2. LEER HISTORIAL
        try:
            hoja_historial = sh.worksheet("Historial")
            df_hist = pd.DataFrame(hoja_historial.get_all_records())
        except:
            df_hist = pd.DataFrame()

        # --- NAVEGACIÓN ---
        tab_dash, tab_reg, tab_gest, tab_acc, tab_ventas = st.tabs([
            "📊 DASHBOARD", "📝 CREAR ANIMAL", "🛠️ GESTIÓN E IMÁGENES", "⚡ ACCIONES RÁPIDAS", "💰 HISTORIAL VENTAS"
        ])

        # ==========================================
        # 1. DASHBOARD
        # ==========================================
        with tab_dash:
            if not df_activos.empty:
                with st.container(border=True):
                    col_finca1, col_finca2 = st.columns([1, 3])
                    with col_finca1:
                        st.image("https://cdn-icons-png.flaticon.com/512/2173/2173516.png", width=80)
                    with col_finca2:
                        st.subheader("Resumen del Hato (Activos)") 
                        st.caption("Animales presentes en finca")
                        
                col_graf, col_stats = st.columns([1, 1])
                with col_graf:
                    with st.container(border=True):
                        st.subheader("Distribución")
                        if "Tipo" in df_activos.columns:
                            base = alt.Chart(df_activos).encode(theta=alt.Theta("count()", stack=True))
                            pie = base.mark_arc(outerRadius=100, innerRadius=60).encode(
                                color=alt.Color("Tipo"),
                                order=alt.Order("Tipo", sort="descending"),
                                tooltip=["Tipo", "count()"]
                            )
                            st.altair_chart(pie, use_container_width=True)

                with col_stats:
                    with st.container(border=True):
                        st.subheader("Indicadores")
                        total = len(df_activos)
                        machos = len(df_activos[df_activos["Sexo"] == "Macho"]) if "Sexo" in df_activos.columns else 0
                        hembras = len(df_activos[df_activos["Sexo"] == "Hembra"]) if "Sexo" in df_activos.columns else 0
                        st.metric("Total en Finca", total)
                        st.metric("Hembras / Machos", f"{hembras} / {machos}")
            else:
                st.info("👋 Registra animales para ver el tablero.")

        # ==========================================
        # 2. CREAR ANIMAL (CON IMGBB)
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
                with g3: estado = st.selectbox("Estado", ["Sano", "Enfermo", "Preñada"])

                st.markdown("---")
                p1, p2, p3 = st.columns(3)
                with p1: peso = st.number_input("Peso (kg)*", min_value=0.0)
                with p2: fecha_nac = st.date_input("Nacimiento")
                with p3: foto = st.file_uploader("Foto (Opcional)", type=["jpg", "png", "jpeg"])

                if st.form_submit_button("💾 GUARDAR", type="primary"):
                    if not id_animal:
                        st.error("El ID es obligatorio")
                    elif id_animal in lista_ids_todos:
                        st.error("⚠️ Este ID ya existe.")
                    else:
                        link_foto = "Sin Foto"
                        if foto:
                            with st.spinner("Subiendo foto a la nube..."):
                                link_foto = subir_foto_imgbb(foto)
                        
                        datos = [id_animal, tipo, nombre, arete, raza, sexo, str(peso), str(fecha_nac), estado, link_foto]
                        guardar_animal(hoja_animales, datos)

        # ==========================================
        # 3. GESTIÓN E IMÁGENES
        # ==========================================
        with tab_gest:
            st.subheader("🛠️ Gestión y Visualización")
            
            modo_ver = st.radio("Filtro:", ["Ver Activos", "Ver Vendidos", "Ver Todo"], horizontal=True)
            if modo_ver == "Ver Activos": df_show = df_activos
            elif modo_ver == "Ver Vendidos": df_show = df[df["Estado"] == "VENDIDO"]
            else: df_show = df

            st.dataframe(df_show, use_container_width=True)
            st.markdown("---")

            st.subheader("📸 Ficha del Animal")
            animal_sel = st.selectbox("Seleccione un ID:", [""] + lista_ids_todos)

            if animal_sel:
                try:
                    datos = df[df["ID"] == animal_sel].iloc[0]
                    
                    col_foto, col_datos = st.columns([1, 2])
                    
                    with col_foto:
                        st.markdown("**Fotografía:**")
                        link_foto = str(datos.get("Foto", "Sin Foto"))
                        
                        # Manejo de links
                        if "http" in link_foto:
                            st.image(link_foto, caption=f"ID: {animal_sel}", use_container_width=True)
                        elif link_foto == "Error":
                            st.error("Error en carga anterior.")
                        else:
                            st.image("https://via.placeholder.com/300x300?text=Sin+Foto", caption="No hay imagen", use_container_width=True)

                    with col_datos:
                        with st.expander("✏️ Editar Datos", expanded=True):
                            with st.form("form_editar"):
                                e_c1, e_c2 = st.columns(2)
                                with e_c1: e_nombre = st.text_input("Nombre", value=datos["Nombre"])
                                with e_c2: e_arete = st.text_input("Arete", value=datos["Arete"])
                                
                                peso_val = float(datos["Peso"]) if datos["Peso"] else 0.0
                                e_peso = st.number_input("Peso (kg)", value=peso_val)
                                
                                e_estado = st.selectbox("Estado", ["Sano", "Enfermo", "Preñada", "VENDIDO"], 
                                                        index=["Sano", "Enfermo", "Preñada", "VENDIDO"].index(datos["Estado"]) if datos["Estado"] in ["Sano", "Enfermo", "Preñada", "VENDIDO"] else 0)

                                e_foto = st.file_uploader("Actualizar Foto", type=["jpg", "png", "jpeg"])

                                if st.form_submit_button("💾 Actualizar Datos"):
                                    nuevo_link = datos.get("Foto", "Sin Foto")
                                    if e_foto:
                                        with st.spinner("Subiendo nueva foto..."):
                                            nuevo_link = subir_foto_imgbb(e_foto)

                                    datos_upd = [
                                        animal_sel, datos["Tipo"], e_nombre, e_arete, 
                                        datos["Raza"], datos["Sexo"], str(e_peso), 
                                        str(datos["Nacimiento"]), e_estado, nuevo_link
                                    ]
                                    actualizar_animal_completo(hoja_animales, animal_sel, datos_upd)
                except Exception as e:
                    st.error(f"Error cargando ficha: {e}")
                    if st.button("🗑️ Eliminar Animal"):
                         eliminar_animal_db(hoja_animales, animal_sel)

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
            
            # --- FORMULARIO VENTA ---
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

                    st.markdown('<div class="seccion-titulo">📍 Destino</div>', unsafe_allow_html=True)
                    dest_ciudad = st.text_input("Ciudad / Destino / Finca")
                    
                    with st.expander("Transporte (Opcional)"):
                         c_t1, c_t2 = st.columns(2)
                         with c_t1: trans_guia = st.text_input("Nro. Guía")
                         with c_t2: trans_placa = st.text_input("Placa")

                    st.markdown('<div class="seccion-titulo">💰 Datos Económicos</div>', unsafe_allow_html=True)
                    ids_seleccionados = st.multiselect("Animales (Activos)*", lista_ids_activos)
                    
                    c_m1, c_m2, c_m3 = st.columns([1,1,2])
                    with c_m1: moneda = st.selectbox("Moneda", ["USD", "VES", "COP"])
                    with c_m2: monto_manual = st.number_input("Precio", min_value=0.0)
                    with c_m3: tipo_precio = st.radio("Tipo:", ["Por Kilo", "Por Cabeza", "Lote"], horizontal=True)
                    
                    notas_venta = st.text_area("Notas")

                    if st.form_submit_button("✅ CONFIRMAR VENTA", type="primary"):
                        if not ids_seleccionados:
                            st.error("Selecciona un animal")
                        else:
                            precio_str = f"{monto_manual} {moneda} ({tipo_precio})"
                            for animal_id in ids_seleccionados:
                                detalle = f"Comp: {comp_nombre} | Dest: {dest_ciudad}"
                                notas_full = f"Guia: {trans_guia} | {notas_venta}"
                                
                                datos_venta = [str(fecha_venta), "VENTA", animal_id, precio_str, detalle, notas_full]
                                guardar_evento(sh, datos_venta, "Venta")
                                cambiar_estado_vendido(hoja_animales, animal_id)

                            st.success("Venta registrada.")
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
        # 5. HISTORIAL DE VENTAS
        # ==========================================
        with tab_ventas:
            st.header("💰 Historial de Ventas")
            if not df_hist.empty and "Tipo Evento" in df_hist.columns:
                mask_venta = df_hist["Tipo Evento"].astype(str).str.contains("VENTA", case=False, na=False)
                df_ventas = df_hist[mask_venta]
                if not df_ventas.empty:
                    st.dataframe(df_ventas[["Fecha", "ID Animal", "Detalle 1", "Detalle 2"]], use_container_width=True, hide_index=True)
                else:
                    st.warning("No hay ventas.")
            else:
                st.info("Sin historial.")

if __name__ == "__main__":
    main()