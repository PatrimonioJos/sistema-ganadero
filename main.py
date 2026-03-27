import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import altair as alt
from datetime import date, datetime, timedelta
import os
import time
import requests 
import io 
from fpdf import FPDF 
import uuid 

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

LISTA_ESPECIES = ["Bovino", "Porcino", "Ovino", "Caprino", "Equino", "Bufalino", "Otro"]

# --- LISTA MAESTRA DE RAZAS ACTUALIZADA ---
LISTA_RAZAS_GLOBAL = [
    "7 Colores", "Abigar", "Abondance", "Abyssinian Shorthorned Zebu", "Aceh", "Achham", 
    "Adamawa", "Adaptaur", "Africangus", "Afrikane", "Agerolese", "Ala Tau", "Alambadi", 
    "Albanian", "Albera", "Alderney", "Alentejana", "Aleutian Wild", "Aliab Dinka", 
    "Alistana-Sanabresa", "Allmogekor", "Alur", "American", "American Beef Friesian", 
    "American Brown Swiss", "American White Park", "Americano", "Amerifax", "Amiata", 
    "Amrit Mahal", "Anatolian Black", "Andalusian Black", "Angeln", "Angoni", "Angun Negro", 
    "Angus", "Angus Hybrid", "Angus-Nelore", "Ankole-Watusi", "Aosta", "Apulian Podolian", 
    "Arado", "Armorican", "Arouquesa", "Asturian Mountain", "Asturiana de los Valles", 
    "Aubrac", "Australian Braford", "Australian Lowline", "Ayrshire", "Azul Belga", "Baherie", 
    "Bakosi", "Balancer", "Bale", "Baoule", "Barrosã", "Barzona", "Batangas", "Bazadaise", 
    "Beefalo", "Beefmaker", "Beefmaster", "Belgian Red", "Belmont Red", "Belted Galloway", 
    "Bernese", "Berrendas", "Betizu", "Bianca Val Padana", "Blaarkop", "Black Angus", 
    "Black Baldy", "Black Hereford", "Black Pied", "Black Sardo", "Blanca Cacerena", 
    "Blanco Orejinegro BEW", "Blue Grey", "Bohus Polled", "Bon", "Bonsmara", "Boran", 
    "Bororo", "Braford", "Brahman", "Brahman Rojo", "Brahmousin", "Brangus", "Braunvieh", 
    "Brava", "British White", "BueLingo", "Burlina", "Busa", "Butana", "Cabannina", "Cachena", 
    "Calvana", "Calvesiana", "Camargue", "Campbell Island", "Canadian Speckle Park", 
    "Canadienne", "Canaria", "Canchim", "Caracu are Brazilian", "Cardena Andaluza", 
    "Carinthian Blondvieh", "Carora", "Casanareño", "Cebú", "Charbray", "Charolais", 
    "Chiangus", "Chianina", "Chillingham", "Chinese Black Pied", "Chinese Central Plains Yellow", 
    "Chinese Northern Yellow", "Chino Santandereano", "Chirikof Island", "Color Sided White Back", 
    "Commercial", "Corriente", "Costeño con Cuernos", "Criollo", "Criollo Lechero Tropical", 
    "Crioulo Lageano Longhorn", "Crossbred", "Cruzado", "Dairy Shorthorn", "Dajal", 
    "Danish Black-Pied", "Danish Jersey", "Danish Red", "Deep Red", "Desconocida", "Devon", 
    "Dexter", "Dhanni", "Doayo", "Doela", "Droughtmaster", "Dulong", "Dutch Belted", 
    "Dwarf Lulu", "Dølafe", "East Anatolian Red", "Eastern Finncattle", "Eastern Red Polled", 
    "Enderby Island", "English Longhorn", "Ennstal Mountain Pied", "Estonian Holstein", 
    "Estonian Native", "Estonian Red", "Evolene", "F1", "F1-Beefmaster", "F1-Brahman", 
    "F1-Brahmousin", "F1-Normando", "F1-Simmental", "F2-Brahman", "F2-Normando", "F2-Simmental", 
    "Finnish", "Finnish Ayrshire", "Fjall", "Fleckvieh", "Florida Cracker", "French Simmental", 
    "Fresian Red and White", "Fribourg Black and White", "Fribourgeoise", "Fulani Sudanese", 
    "Garfagnina", "Garvonesa", "Gascon", "Gelbray", "Gelbvieh", "Georgian Mountain", 
    "German Angus", "German Black Pied", "German Red Pied", "Girolando", "Glan", "Gloucester", 
    "Gobra", "Goffa", "Golden Pied", "Grand Noir du Berry", "Greek Shorthorn", "Greek Steppe", 
    "Grey Alpine", "Greyman", "Groningen Whiteheaded", "Gudali", "Guernsey", "Guzerat", "Gyr", 
    "Hallikar", "Hammer", "Harar", "Hariana", "Harton del Valle", "Harz Red Mountain", 
    "Hays Converter", "Heck", "Hereford", "Herens", "Highland", "Hinterwald", "Holando-Argentino", 
    "Holstein Friesian", "Holstein Negro", "Holstein Rojo", "Holzer", "Horro", "Hungarian Grey", 
    "Hybridmaster", "Icelandic", "Illawarras", "Improved Red and White", "Indubrasil", "INRA 95", 
    "Irish Black and Red", "Irish Moiled", "Israeli", "Israeli Red", "Istoben", "Jamaica Black", 
    "Jamaica Hope", "Jamaica Red", "Jarmelista", "Jem-Jem", "Jerhol", "Jersey", "Jersyrolando", 
    "Jijiga", "Jutland", "Kalmyk", "Kangayam", "Kankrej", "Karan Swiss", "Kazakh White-Headed", 
    "Kerry", "Kholmogory", "Kostroma", "Kurgan", "Kuri", "Lampurger", "Latvian Blue", 
    "Latvian Brown", "Levantina", "Lidia", "Limia", "Limousin", "Limpurger", "Lincoln", 
    "Lincoln Red", "Lineback", "Lithuanian Black-and-White", "Lithuanian Red", "Lohani", 
    "Lombard", "Longhorn", "Lourdaise", "Lucerna", "Luing", "Madura", "Maine-Anjou", "Mambí", 
    "Mandalong Special", "Mantequera Leonesa", "Maramure Brown", "Marchigiana", "Maremmana", 
    "Maringa", "Maronesa", "Masai", "Mashona", "Menorquina", "Mertolenga", "Mestiza", 
    "Meuse-Rhine-Issel", "Minhota", "Miniature", "Mirandesa", "Modenese", "Modicana", 
    "Monchina", "Mongolian", "Montbéliarde", "Mucca Pisana", "Murboden", "Murnau-Werdenfels", 
    "Murray Grey", "Mursi", "N'Dama", "Nelore", "Nelore Pintado", "Nguni", "Normande", 
    "Normando", "Northern Finncattle", "Northern Shorthorn", "Norwegian Red", "Pajuna", 
    "Palmera", "Pantaneiro", "Parda Alpina", "Pardo Suizo", "Parthenaise", "Pasiega", 
    "Pasturina", "Pembroke", "Pezzata Rossa D'Oropa", "Philippine", "Physical Characteristics", 
    "Pie Rouge des Plaines", "Piemontese", "Pineywoods", "Pinzgauer", "Pirenaica", "Podolica", 
    "Polish Black-and-White", "Polish Red", "Polled Hereford", "Ponwar", "Preta", 
    "Punganur Dwarf", "Pustertaler", "Qinchuan", "Queensland Miniature Boran", "Ramo Grande", 
    "Randall Lineback", "Red Angus", "Red Brahman", "Red Brangus", "Red Fulani", "Red Pied", 
    "Red Poll", "Red Polled Ostland", "Red Steppe", "Reina", "Rendena", "Retinta", "Reyna", 
    "Rojo Sueco", "Romagnola", "Romanian Balata", "Romanian Steppe Gray", "Rombrah", 
    "Romosinuano", "Rubia de Aquitania", "Rubia Gallega", "Russian Black Pied", "RX3", 
    "Rätisches Grauvieh", "Sahiwal", "Salers", "Salorn", "Sanga", "Sanhe", "Santa Cruz", 
    "Santa Gertrudis", "Sarda", "Sardo Bruna", "Sardo-modicana", "Savoiarda", "Sayaguesa", 
    "Schwyz", "Selembu", "Senepol", "Sheko", "Shetland", "Shorthorn", "Siboney", "Sided Tronder", 
    "Simbrah", "Simbrasil", "Simford", "Simmental", "Sindhi", "Smada", "South Devon", 
    "Speckle Park", "Square Meater", "Suizbu", "Sussex", "Swedish Red-and-White", "Tropicame", 
    "Wagyu", "Wangus", "Watusi", "Welsh Black", "Western Finncattle", "Western Fjord", 
    "White Caceres", "White Fulani", "White Park", "Whitebred Shorthorn", "Xingjiang Brown", 
    "Yanbian", "Zebu"
]

LISTA_PROPOSITOS = ["Carne", "Leche", "Doble Propósito", "Cría / Genética", "Deporte / Trabajo", "Mascota"]

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

TIPOS_FECUNDACION = ["Monta", "Inseminación artificial", "Transferencia de embriones", "Otros"]

# --- ESTILOS CSS ---
st.markdown("""
<style>
    /* Estilo General Botones */
    div.stButton > button { width: 100%; height: 50px; font-size: 16px; border-radius: 12px; border: 1px solid #e0e0e0; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    div.stButton > button[kind="primary"] { background-color: #e53935 !important; color: white !important; border-radius: 25px !important; font-weight: bold !important; border: none !important; }
    div.stButton > button[kind="primary"]:hover { background-color: #c62828 !important; }

    /* Headers y Secciones */
    .app-header { background-color: #4CAF50; color: white; padding: 10px 15px; font-weight: bold; border-radius: 5px; margin-bottom: 15px; font-size: 16px; }
    .seccion-titulo { background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-top: 10px; margin-bottom: 10px; font-weight: bold; color: #31333F; }
    
    /* Tablas y Tarjetas */
    .tabla-header { background-color: #2e7d32; color: white; padding: 8px; border-radius: 8px 8px 0 0; font-weight: bold; font-size: 14px; display: flex; justify-content: space-between; }
    .tabla-row { background-color: white; padding: 10px; border-bottom: 1px solid #eee; border-left: 1px solid #eee; border-right: 1px solid #eee; font-size: 14px; display: flex; justify-content: space-between; align-items: center; }
    .vet-card { background-color: white; border-left: 5px solid #2e7d32; padding: 10px; margin-bottom: 10px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .repro-card { background-color: white; border-left: 5px solid #1565c0; padding: 10px; margin-bottom: 10px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .empty-state { text-align: center; padding: 20px; color: #666; }
    
    /* Módulo Finanzas (Tarjetas de Cuentas) */
    .cuenta-card { background-color: #f8f9fa; border-left: 5px solid #1976d2; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 15px; }
    .cuenta-title { font-size: 14px; color: #555; font-weight: bold; margin-bottom: 5px; text-transform: uppercase; }
    .cuenta-saldo { font-size: 26px; font-weight: bold; color: #2e7d32; margin: 0; }
    .cuenta-moneda { font-size: 14px; color: #777; font-weight: normal; }
    
    /* Módulo Finanzas (Historial / Libro Mayor) */
    .fin-row { background-color: white; padding: 15px; border-radius: 8px; border: 1px solid #e0e0e0; box-shadow: 0 2px 4px rgba(0,0,0,0.02); margin-bottom: 10px; display: flex; align-items: center; }
    .fin-icon { font-size: 24px; margin-right: 15px; width: 40px; text-align: center; background-color: #f0f2f6; padding: 10px; border-radius: 50%; }
    .fin-details { flex-grow: 1; }
    .fin-title { font-weight: bold; color: #333; font-size: 15px; margin-bottom: 3px; display: flex; justify-content: space-between;}
    .fin-subtitle { color: #666; font-size: 13px; margin-bottom: 3px; }
    .fin-notas { color: #999; font-size: 11px; font-style: italic; }
    .fin-date { font-size: 12px; color: #888; text-align: right; min-width: 80px; }
    .fin-pos { border-left: 5px solid #2e7d32; } /* Verde Ingreso */
    .fin-neg { border-left: 5px solid #d32f2f; } /* Rojo Egreso */
    .fin-neu { border-left: 5px solid #1976d2; } /* Azul Neutro */

    /* Dashboard & Alertas */
    .dash-card { background-color: white; border-radius: 10px; padding: 15px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #f0f0f0; }
    .grid-2-col { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
    .metric-card { background-color: white; border-radius: 10px; padding: 15px; display: flex; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #f0f0f0; }
    .metric-icon { font-size: 35px; margin-right: 15px; }
    .metric-info { flex-grow: 1; text-align: right; }
    .metric-title { font-size: 12px; color: #777; margin-bottom: 5px; text-transform: uppercase; }
    .metric-value { font-size: 22px; font-weight: bold; margin: 0; color: #333; }
    .alerta-card { background-color: white; padding: 15px; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border-left: 5px solid #9e9e9e; display: flex; align-items: center; }
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN GOOGLE SHEETS ---
@st.cache_resource
def conectar_sheets():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = None
    if os.path.exists("credentials.json"):
        creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    elif "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        
    if not creds:
        st.error("❌ No se encontraron credenciales.")
        return None
    try:
        client = gspread.authorize(creds)
        sheet_id = "1292mc53ss8G8pY-azGsrpq10OR8RDX0gNMVML8LgfU0" 
        sh = client.open_by_key(sheet_id)
        
        try:
            sh.worksheet("Cuentas")
        except gspread.exceptions.WorksheetNotFound:
            ws_cuentas = sh.add_worksheet(title="Cuentas", rows="100", cols="5")
            ws_cuentas.append_row(["ID", "Nombre", "Moneda", "Saldo"])
            
        return sh
    except Exception as e:
        st.error(f"⚠️ Error conectando con Google Sheets: {e}")
        return None

# --- CARGA DE DATOS (AHORA BLINDADA) ---
@st.cache_data(ttl=600) 
def cargar_datos():
    sh = conectar_sheets()
    if not sh:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    # Función auxiliar para leer hojas y evitar el error de las columnas vacías ("")
    def leer_hoja_segura(worksheet):
        datos = worksheet.get_all_values()
        if not datos or len(datos) < 2:
            return pd.DataFrame()
        
        encabezados = [str(x).strip() for x in datos[0]]
        df = pd.DataFrame(datos[1:], columns=encabezados)
        
        # Eliminar cualquier columna que no tenga título (esto soluciona tu error de duplicates: [''])
        if "" in df.columns:
            df = df.drop(columns=[""])
            
        return df

    try:
        hoja_animales = sh.get_worksheet(0)
        df = leer_hoja_segura(hoja_animales)
        if not df.empty:
            df.columns = df.columns.astype(str).str.strip()
            df["ID"] = df["ID"].astype(str)
    except Exception as e:
        st.error(f"🚨 Error leyendo la pestaña de Animales: {e}")
        df = pd.DataFrame()

    try:
        hoja_historial = sh.worksheet("Historial")
        df_hist = leer_hoja_segura(hoja_historial)
    except Exception as e:
        st.error(f"🚨 Error leyendo el Historial: {e}")
        df_hist = pd.DataFrame()
        
    try:
        hoja_cuentas = sh.worksheet("Cuentas")
        df_cuentas = leer_hoja_segura(hoja_cuentas)
    except Exception as e:
        st.error(f"🚨 Error leyendo las Cuentas: {e}")
        df_cuentas = pd.DataFrame()
        
    return df, df_hist, df_cuentas

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
    sheet.append_row(datos)
    cargar_datos.clear() 
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
        worksheet.append_row(["Fecha", "Tipo Evento", "ID Animal", "Detalle 1", "Detalle 2", "Notas", "ID Evento"])
    
    if len(datos) == 6:
        id_evento = str(uuid.uuid4())[:8]
        datos.append(id_evento)
        
    worksheet.append_row(datos)
    cargar_datos.clear()
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
        cargar_datos.clear() 
        st.success("✅ Datos actualizados correctamente")
        time.sleep(1)
        st.rerun()

def cambiar_estado_animal(sheet, id_animal, nuevo_estado):
    fila = encontrar_fila_por_id(sheet, id_animal)
    if fila:
        sheet.update_cell(fila, 9, nuevo_estado)
        cargar_datos.clear() 

def eliminar_animal_db(sheet, id_animal):
    fila = encontrar_fila_por_id(sheet, id_animal)
    if fila:
        sheet.delete_rows(fila)
        cargar_datos.clear() 
        st.warning("🗑️ Animal eliminado")
        time.sleep(1)
        st.rerun()

def cambiar_estado_vendido(sheet, id_animal):
    fila = encontrar_fila_por_id(sheet, id_animal)
    if fila:
        sheet.update_cell(fila, 9, "VENDIDO") 
        cargar_datos.clear() 

# --- FUNCIONES FINANZAS ---
def crear_cuenta(sh, nombre, moneda, saldo_inicial):
    hoja = sh.worksheet("Cuentas")
    nuevo_id = str(len(hoja.get_all_values())) 
    hoja.append_row([nuevo_id, nombre, moneda, str(saldo_inicial)])
    cargar_datos.clear()
    st.success(f"✅ Cuenta '{nombre}' creada exitosamente.")

def actualizar_saldo_cuenta(sh, nombre_cuenta, variacion_monto):
    hoja = sh.worksheet("Cuentas")
    nombres = hoja.col_values(2) 
    if nombre_cuenta in nombres:
        fila = nombres.index(nombre_cuenta) + 1
        saldo_actual = float(str(hoja.cell(fila, 4).value).replace(",", "")) 
        nuevo_saldo = saldo_actual + float(variacion_monto)
        hoja.update_cell(fila, 4, str(nuevo_saldo))
        cargar_datos.clear()

def eliminar_evento_finanzas_por_id(sh, id_evento):
    hoja = sh.worksheet("Historial")
    registros = hoja.get_all_values()
    fila_a_borrar = None
    fila_datos = None
    
    for i, fila in enumerate(registros):
        if len(fila) > 6 and str(fila[6]).strip() == str(id_evento).strip():
            fila_a_borrar = i + 1
            fila_datos = fila
            break
            
    if fila_a_borrar:
        tipo = fila_datos[1]
        det1 = str(fila_datos[3])
        det2 = str(fila_datos[4])
        notas = str(fila_datos[5])
        
        monto_reversion = 0.0
        cuenta_reversion = ""
        
        try:
            if tipo == "VENTA":
                monto_reversion = float(det1.split()[0])
                if "Ingresa a:" in notas: cuenta_reversion = notas.split("Ingresa a:")[1].split("|")[0].strip()
            elif tipo == "COMPRA":
                if "Monto Total:" in notas: monto_reversion = float(notas.split("Monto Total:")[1].split("|")[0].strip())
                if "Pagado desde:" in notas: cuenta_reversion = notas.split("Pagado desde:")[1].split("|")[0].strip()
            elif tipo == "APORTE_CAPITAL":
                cuenta_reversion = det1.replace("Cuenta:", "").strip()
                monto_reversion = float(det2.replace("Monto:", "").strip())
            elif tipo == "GASTO_OPERATIVO" or tipo == "INGRESO_OPERATIVO":
                monto_reversion = float(det1.split("Monto:")[1].split("(Cuenta:")[0].strip())
                cuenta_reversion = det1.split("(Cuenta:")[1].replace(")", "").strip()
        except Exception as e:
            st.error(f"No se pudo detectar el monto exacto para revertir la caja. Borrado manual sugerido en Google Sheets.")
            return False
            
        if cuenta_reversion and monto_reversion > 0:
            if tipo in ["GASTO_OPERATIVO", "COMPRA"]:
                actualizar_saldo_cuenta(sh, cuenta_reversion, monto_reversion) 
            elif tipo in ["VENTA", "APORTE_CAPITAL", "INGRESO_OPERATIVO"]:
                actualizar_saldo_cuenta(sh, cuenta_reversion, -monto_reversion) 

        hoja.delete_rows(fila_a_borrar)
        cargar_datos.clear()
        st.toast("✅ Registro eliminado y dinero devuelto a la cuenta correctamente.")
        return True
    else:
        st.error("❌ ID no encontrado. Verifica que lo escribiste correctamente.")
        return False

def reparar_ids_historial(sh):
    """Función de auto-sanación que asigna UUIDs a transacciones viejas sin ID"""
    try:
        hoja = sh.worksheet("Historial")
        registros = hoja.get_all_values()
        if not registros: return 0
        
        header = registros[0]
        if len(header) < 7:
            hoja.update_cell(1, 7, "ID Evento")
        elif header[6].strip() == "":
            hoja.update_cell(1, 7, "ID Evento")
        
        lista_updates = []
        for i, fila in enumerate(registros):
            if i == 0: continue
            if len(fila) < 7 or str(fila[6]).strip() == "":
                nuevo_id = str(uuid.uuid4())[:8]
                lista_updates.append({'range': f'G{i+1}', 'values': [[nuevo_id]]})
        
        if lista_updates:
            hoja.batch_update(lista_updates)
            cargar_datos.clear()
        return len(lista_updates)
    except Exception as e:
        st.error(f"Error reparando IDs: {e}")
        return 0

# --- GESTIÓN DE ESTADO (NAVEGACIÓN) ---
if 'nav_gestion' not in st.session_state: st.session_state.nav_gestion = 'lista' 
if 'animal_seleccionado' not in st.session_state: st.session_state.animal_seleccionado = None
if 'accion_activa' not in st.session_state: st.session_state.accion_activa = None
if 'sub_accion_produccion' not in st.session_state: st.session_state.sub_accion_produccion = None
if 'sub_accion_veterinaria' not in st.session_state: st.session_state.sub_accion_veterinaria = None
if 'sub_accion_reproduccion' not in st.session_state: st.session_state.sub_accion_reproduccion = None
if 'registro_expandido' not in st.session_state: st.session_state.registro_expandido = False
if 'sub_accion_sanidad_rapida' not in st.session_state: st.session_state.sub_accion_sanidad_rapida = None

def ir_a_lista(): st.session_state.nav_gestion = 'lista'; st.session_state.animal_seleccionado = None
def ir_a_perfil(animal_id): st.session_state.animal_seleccionado = animal_id; st.session_state.nav_gestion = 'perfil'
def ir_a_detalle(): st.session_state.nav_gestion = 'detalle'
def ir_a_produccion(): st.session_state.nav_gestion = 'produccion'; st.session_state.sub_accion_produccion = None
def ir_a_veterinaria(): st.session_state.nav_gestion = 'veterinaria'; st.session_state.sub_accion_veterinaria = None
def ir_a_reproduccion(): st.session_state.nav_gestion = 'reproduccion'; st.session_state.sub_accion_reproduccion = None
def set_accion(nombre_accion): st.session_state.accion_activa = nombre_accion; st.session_state.sub_accion_sanidad_rapida = None 
def toggle_registro_mode(): st.session_state.registro_expandido = not st.session_state.registro_expandido


# --- APP PRINCIPAL ---
def main():
    st.title("🧬 Control Ganadero")

    sh = conectar_sheets()
    
    if sh:
        hoja_animales = sh.get_worksheet(0)
        df, df_hist, df_cuentas = cargar_datos()
        
        if not df.empty:
            df_activos = df[df["Estado"] != "VENDIDO"]
            lista_ids_activos = df_activos["ID"].tolist()
            lista_ids_todos = df["ID"].tolist()
        else:
            df_activos = pd.DataFrame()
            lista_ids_activos = []
            lista_ids_todos = []

        # --- PESTAÑAS (TABS) ---
        tab_dash, tab_reg, tab_gest, tab_acc, tab_finanzas, tab_alertas, tab_reportes = st.tabs([
            "📊 DASHBOARD", "📝 REGISTRO", "📱 GESTIÓN", "⚡ RÁPIDO", "🏦 FINANZAS", "🔔 ALERTAS", "📑 REPORTES"
        ])

        # ==========================================
        # 1. DASHBOARD
        # ==========================================
        with tab_dash:
            st.markdown("""
            <div style="background-color: #4CAF50; color: white; padding: 15px; text-align: center; border-radius: 5px 5px 0 0; position: relative;">
                <h2 style="margin: 0; font-size: 24px; color: white;">Finca ⚠️</h2>
            </div>
            <div style="background-color: #e0e0e0; padding: 8px 15px; font-size: 14px; border-radius: 0 0 5px 5px; margin-bottom: 15px; color: #555;">
                <strong>Perfil:</strong> Propietario | <strong>Sincronización:</strong> ✅
            </div>
            """, unsafe_allow_html=True)

            c_d1, c_d2 = st.columns(2)
            with c_d1:
                st.markdown("""
                <div class="dash-card">
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                        <div style="font-size: 30px;">🏠</div>
                        <h3 style="margin:0; font-size: 20px;">Alvicion</h3>
                    </div>
                    <p style="color:#666; margin: 0; font-size: 14px;"><strong>Propósito:</strong> Doble propósito</p>
                    <p style="color:#666; margin: 0; font-size: 14px;"><strong>Área de ganado:</strong> 50.0 ha</p>
                </div>
                """, unsafe_allow_html=True)
            with c_d2:
                st.markdown("""
                <div class="dash-card">
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                        <div style="font-size: 30px;">📊</div>
                        <h3 style="margin:0; font-size: 20px;">Informes</h3>
                    </div>
                    <p style="color:#666; margin: 0; font-size: 14px;">Último informe: --</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")

            if not df_activos.empty:
                machos = len(df_activos[df_activos["Sexo"] == "Macho"])
                hembras = len(df_activos[df_activos["Sexo"] == "Hembra"])
                crias = len(df_activos[df_activos["Tipo"] == "Becerro"])
                adultos = len(df_activos) - crias
                try: peso_total = df_activos["Peso"].astype(float).sum()
                except: peso_total = 0.0

                ganancias_diarias = []
                for _, row in df_activos.iterrows():
                    try:
                        peso_actual = float(row["Peso"]) if pd.notnull(row["Peso"]) and str(row["Peso"]).strip() != "" else 0.0
                        peso_nac = 35.0 
                        if "PesoNac" in df_activos.columns and pd.notnull(row["PesoNac"]) and str(row["PesoNac"]).strip() != "":
                            peso_nac = float(row["PesoNac"])
                        fecha_nac = pd.to_datetime(row["Nacimiento"], errors='coerce')
                        if pd.notnull(fecha_nac):
                            dias_vida = (pd.Timestamp(date.today()) - fecha_nac).days
                            if dias_vida > 0 and peso_actual > peso_nac:
                                gmd = ((peso_actual - peso_nac) / dias_vida) * 1000 
                                ganancias_diarias.append(gmd)
                    except: pass
                
                ganancia_promedio_g = sum(ganancias_diarias) / len(ganancias_diarias) if ganancias_diarias else 0.0
                leche_total = 0.0
                if not df_hist.empty and "Tipo Evento" in df_hist.columns:
                    df_leche = df_hist[df_hist["Tipo Evento"] == "PRODUCCION_LECHE"]
                    if not df_leche.empty:
                        try: leche_total = df_leche["Detalle 1"].astype(float).sum()
                        except: pass

                vacas = len(df_activos[df_activos["Tipo"] == "Vaca"])

                st.markdown('<div class="dash-card"><h4 style="margin-top:0;">Inventario de animales</h4>', unsafe_allow_html=True)
                df_pie = pd.DataFrame({"Categoría": ["Crías", "Adultos"], "Cantidad": [crias, adultos]})
                domain = ["Crías", "Adultos"]
                range_ = ["#9c27b0", "#388e3c"] 
                
                pie = alt.Chart(df_pie).mark_arc(innerRadius=60).encode(
                    theta=alt.Theta("Cantidad:Q"),
                    color=alt.Color("Categoría:N", scale=alt.Scale(domain=domain, range=range_)),
                    tooltip=["Categoría", "Cantidad"]
                ).properties(height=250)
                st.altair_chart(pie, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown(f"""
                <div class="grid-2-col">
                    <div class="metric-card"><div class="metric-icon" style="color: #29b6f6;">♂️</div><div class="metric-info"><div class="metric-title">Machos</div><div class="metric-value">{machos}</div></div></div>
                    <div class="metric-card"><div class="metric-icon" style="color: #ab47bc;">♀️</div><div class="metric-info"><div class="metric-title">Hembras</div><div class="metric-value">{hembras}</div></div></div>
                    <div class="metric-card"><div class="metric-icon">🥩</div><div class="metric-info"><div class="metric-title" style="text-transform: none;">Promedio de ganancia de peso</div><div class="metric-value">{ganancia_promedio_g:.1f} g</div></div></div>
                    <div class="metric-card"><div class="metric-icon">🥩</div><div class="metric-info"><div class="metric-title" style="text-transform: none;">Total de carne</div><div class="metric-value">{peso_total:.1f} kg</div></div></div>
                    <div class="metric-card"><div class="metric-icon">🥛</div><div class="metric-info"><div class="metric-title" style="text-transform: none;">Producción total de leche</div><div class="metric-value">{leche_total:.1f} L</div><div style="font-size: 10px; color: #d32f2f;">-100.0% Mes pas...</div></div></div>
                    <div class="metric-card"><div class="metric-icon">🐄</div><div class="metric-info"><div class="metric-title" style="text-transform: none;">Animales productivos</div><div class="metric-value">{vacas}</div></div></div>
                </div>
                <div style="text-align: center; color: #888; font-size: 12px; margin-top: 20px; padding-bottom: 20px;">
                    La información de este panel se actualiza de forma automática en cada registro.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("👋 Registra animales para ver el tablero de la finca.")

        # ==========================================
        # 2. REGISTRO 
        # ==========================================
        with tab_reg:
            if not st.session_state.registro_expandido:
                st.info("Ficha de Ingreso Rápido")
                with st.form("ficha_registro_rapido", clear_on_submit=True):
                    c1, c2, c3, c4 = st.columns(4)
                    with c1: id_new = st.text_input("Código / ID*")
                    with c2: arete_new = st.text_input("Arete")
                    with c3: nom_new = st.text_input("Nombre")
                    with c4: sexo_new = st.radio("Sexo", ["Hembra", "Macho"], horizontal=True)
                    
                    c5, c6, c7 = st.columns(3)
                    with c5: raza_new = st.selectbox("Raza *", LISTA_RAZAS_GLOBAL, index=None, placeholder="🔍 Escribe para buscar...")
                    with c6: tipo_new = st.selectbox("Categoría", ["Vaca", "Toro", "Novilla", "Becerro"])
                    with c7: estado_new = st.selectbox("Estado", ["Sano", "Enfermo", "Preñada"])

                    c8, c9, c10 = st.columns(3)
                    with c8: peso_new = st.number_input("Peso (kg)*", min_value=0.0)
                    with c9: nac_new = st.date_input("Nacimiento")
                    with c10: foto_new = st.file_uploader("Foto")

                    if st.form_submit_button("💾 GUARDAR RÁPIDO", type="primary"):
                        if not id_new: st.error("El ID es obligatorio")
                        elif not raza_new: st.error("Selecciona una raza usando el buscador")
                        elif id_new in lista_ids_todos: st.error("ID Repetido")
                        else:
                            link = "Sin Foto"
                            if foto_new:
                                with st.spinner("Subiendo foto..."):
                                    link = subir_foto_imgbb(foto_new)
                            
                            datos = [id_new, tipo_new, nom_new, arete_new, raza_new, sexo_new, str(peso_new), str(nac_new), estado_new, link]
                            guardar_animal(hoja_animales, datos)

                st.write("")
                st.markdown("---")
                if st.button("✏️ Ampliar datos (Registro Completo)"):
                    toggle_registro_mode()
                    st.rerun()

            else:
                if st.button("⬅️ Volver a registro rápido"):
                    toggle_registro_mode()
                    st.rerun()

                st.markdown('<div class="app-header">📝 Crear Animal (Completo)</div>', unsafe_allow_html=True)

                with st.form("ficha_registro_completo", clear_on_submit=True):
                    
                    col_foto, col_sexo = st.columns([1, 1])
                    with col_foto: foto_full = st.file_uploader("Foto del animal", type=["jpg", "png", "jpeg"])
                    with col_sexo:
                        st.write("Sexo")
                        sexo_full = st.radio("Sexo", ["Macho", "Hembra"], horizontal=True, label_visibility="collapsed")

                    st.markdown('<div class="seccion-titulo">Identificación</div>', unsafe_allow_html=True)
                    tipo_full = st.selectbox("Tipo de animal *", LISTA_ESPECIES)
                    
                    col_id1, col_id2 = st.columns(2)
                    with col_id1: id_full = st.text_input("Número del animal (ID) *")
                    with col_id2: arete_full = st.text_input("Arete / Visual (Opcional)")
                    
                    col_id3, col_id4 = st.columns(2)
                    with col_id3: num_raza_full = st.text_input("Número de raza pura (Opcional)")
                    with col_id4: num_chip_full = st.text_input("Número de chip (Opcional)")

                    st.markdown('<div class="seccion-titulo">Información Básica</div>', unsafe_allow_html=True)
                    nombre_full = st.text_input("Nombre del animal")
                    nac_full = st.date_input("Fecha de nacimiento *", date.today())
                    
                    col_bas1, col_bas2 = st.columns(2)
                    with col_bas1: prop_full = st.selectbox("Propietario", ["Principal", "Socio", "Externo"])
                    with col_bas2: lote_full = st.selectbox("Lote", ["General", "Lote 1", "Lote 2", "Enfermería"])
                    
                    raza_full = st.selectbox("Raza *", LISTA_RAZAS_GLOBAL, index=None, placeholder="🔍 Escribe para buscar la raza...")
                    
                    col_prop1, col_prop2 = st.columns(2)
                    with col_prop1: proposito_full = st.selectbox("Propósito Animal", LISTA_PROPOSITOS)
                    with col_prop2: 
                        st.write("¿Está en la finca?")
                        en_finca_full = st.toggle("En Finca", value=True)

                    st.markdown('<div class="seccion-titulo">Pesos (kg)</div>', unsafe_allow_html=True)
                    c_peso1, c_peso2, c_peso3 = st.columns(3)
                    with c_peso1: peso_nac = st.number_input("Al nacer", min_value=0.0)
                    with c_peso2: peso_dest = st.number_input("Al destete", min_value=0.0)
                    with c_peso3: peso_12m = st.number_input("12 meses", min_value=0.0)
                    
                    peso_actual_reg = peso_nac
                    if peso_dest > 0: peso_actual_reg = peso_dest
                    if peso_12m > 0: peso_actual_reg = peso_12m

                    st.markdown('<div class="seccion-titulo">Origen</div>', unsafe_allow_html=True)
                    
                    lista_padres = ["Desconocido"]
                    lista_madres = ["Desconocida"]
                    
                    if not df_activos.empty:
                        machos = df_activos[(df_activos['Sexo'] == 'Macho') | (df_activos['Tipo'] == 'Toro')]
                        if not machos.empty: lista_padres += machos['Nombre'].tolist()
                        hembras = df_activos[(df_activos['Sexo'] == 'Hembra') | (df_activos['Tipo'] == 'Vaca') | (df_activos['Tipo'] == 'Novilla')]
                        if not hembras.empty: lista_madres += hembras['Nombre'].tolist()

                    col_orig1, col_orig2 = st.columns(2)
                    with col_orig1: padre_full = st.selectbox("Padre", lista_padres)
                    with col_orig2: madre_full = st.selectbox("Madre", lista_madres)

                    st.markdown('<div class="seccion-titulo">Otros</div>', unsafe_allow_html=True)
                    notas_full = st.text_area("Notas y observaciones")

                    st.write("")
                    if st.form_submit_button("REGISTRAR ANIMAL", type="primary"):
                        if not id_full: st.error("El Número del animal (ID) es obligatorio.")
                        elif not raza_full: st.error("La raza es obligatoria. Por favor usa el buscador.")
                        elif id_full in lista_ids_todos: st.error("¡Ese ID ya existe en el sistema!")
                        else:
                            link = "Sin Foto"
                            if foto_full:
                                with st.spinner("Subiendo foto..."):
                                    link = subir_foto_imgbb(foto_full)
                            
                            estado_inicial = "Sano"
                            datos_extendidos = [
                                str(id_full), tipo_full, nombre_full, arete_full, raza_full, sexo_full, str(peso_actual_reg), str(nac_full), estado_inicial, link,
                                proposito_full, str(en_finca_full), padre_full, madre_full, str(peso_nac), str(peso_dest), str(peso_12m), notas_full, prop_full, lote_full, num_chip_full, num_raza_full
                            ]
                            guardar_animal(hoja_animales, datos_extendidos)

        if 'sub_accion_sanidad_rapida' not in st.session_state:
            st.session_state.sub_accion_sanidad_rapida = None

        # ==========================================
        # 3. GESTIÓN TIPO APP MÓVIL
        # ==========================================
        with tab_gest:
            if st.session_state.nav_gestion == 'lista':
                busqueda = st.text_input("🔍 Buscar rápido (Nombre, ID o Arete)", placeholder="Ej. Gloria, 1024...")
                with st.expander("⚙️ Filtros Avanzados de Inventario"):
                    c_f1, c_f2, c_f3 = st.columns(3)
                    opciones_tipo = df_activos['Tipo'].dropna().unique().tolist() if 'Tipo' in df_activos.columns else ["Vaca", "Toro", "Novilla", "Becerro"]
                    opciones_estado = df_activos['Estado'].dropna().unique().tolist() if 'Estado' in df_activos.columns else ["Sano", "Enfermo", "Preñada"]
                    opciones_lote = df_activos['Lote'].dropna().unique().tolist() if 'Lote' in df_activos.columns else ["General", "Lote 1", "Lote 2", "Enfermería"]
                    
                    with c_f1: f_cat = st.multiselect("Categoría", opciones_tipo)
                    with c_f2: f_est = st.multiselect("Estado Médico/Repro.", opciones_estado)
                    with c_f3: 
                        if 'Lote' in df_activos.columns: f_lote = st.multiselect("Ubicación / Lote", opciones_lote)
                        else: f_lote = []; st.write("*(Lote no disponible en BD)*")

                df_show = df_activos.copy()
                
                if busqueda: df_show = df_show[df_show.apply(lambda row: busqueda.lower() in str(row.values).lower(), axis=1)]
                if f_cat: df_show = df_show[df_show['Tipo'].isin(f_cat)]
                if f_est: df_show = df_show[df_show['Estado'].isin(f_est)]
                if f_lote and 'Lote' in df_show.columns: df_show = df_show[df_show['Lote'].isin(f_lote)]

                st.markdown(f"""
                <div style="background-color: #e8f5e9; padding: 8px 15px; border-radius: 5px; color: #2e7d32; font-weight: bold; font-size: 14px; margin-bottom: 15px; border-left: 4px solid #4CAF50;">
                    Mostrando {len(df_show)} de {len(df_activos)} animales en la finca
                </div>
                """, unsafe_allow_html=True)

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
                else: st.info("No se encontraron animales con esos filtros.")

            elif st.session_state.nav_gestion == 'perfil':
                animal_id = st.session_state.animal_seleccionado
                datos = df[df["ID"] == animal_id].iloc[0]
                
                col_back, col_tit = st.columns([1, 5])
                with col_back:
                    if st.button("⬅️"):
                        ir_a_lista()
                        st.rerun()
                with col_tit: st.subheader(f"Perfil: {datos['Nombre']}")

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
                    if st.button("ℹ️ Datos generales", use_container_width=True): ir_a_detalle(); st.rerun()
                    st.write("")
                    if st.button("❤️ Datos veterinarios", use_container_width=True): ir_a_veterinaria(); st.rerun()
                with c_btn2:
                    if st.button("📊 Producción", use_container_width=True): ir_a_produccion(); st.rerun()
                    st.write("")
                    if st.button("🧬 Reproducción", use_container_width=True): ir_a_reproduccion(); st.rerun()

                st.markdown("---")
                if st.button("Poner en venta", type="primary", use_container_width=True):
                    st.session_state.accion_activa = "venta"
                    st.info("✅ Modo Venta Activado. Ve a la pestaña '⚡ RÁPIDO' para completar los datos.")

            elif st.session_state.nav_gestion == 'produccion':
                animal_id = st.session_state.animal_seleccionado
                datos = df[df["ID"] == animal_id].iloc[0]

                st.markdown(f"""
                <div style='background-color: #2e7d32; padding: 15px; border-radius: 10px; color: white; margin-bottom: 20px;'>
                    <h3 style='margin:0;'>Producción</h3>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("⬅️ Volver al Perfil"): ir_a_perfil(animal_id); st.rerun()

                if st.session_state.sub_accion_produccion is None:
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

                        st.markdown("<h3>Producción de leche</h3>", unsafe_allow_html=True)
                        st.caption(f"Promedio diario: {promedio_leche:.1f} L")
                        
                        st.markdown("""
                        <div style="background-color: #4CAF50; color: white; padding: 10px; border-radius: 10px 10px 0 0; display: flex; justify-content: space-between; font-weight: bold; font-size: 14px;">
                            <div style="width:33%">Fecha</div>
                            <div style="width:33%">Concentr...</div>
                            <div style="width:33%">Total leche</div>
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
                                <div style="background-color: white; padding: 10px; border-bottom: 1px solid #eee; border-left: 1px solid #eee; border-right: 1px solid #eee; display: flex; justify-content: space-between; font-size: 14px;">
                                    <div style="width:33%">{row['Fecha']}</div>
                                    <div style="width:33%">{concentrado_txt}</div>
                                    <div style="width:33%">{row['Detalle 1']} L</div>
                                </div>
                                """, unsafe_allow_html=True)
                        else: st.info("Sin registros de leche.")

                        st.write("")
                        peso_actual = datos['Peso']
                        st.markdown(f"<h3>Evolución de peso: <span style='color:#4CAF50'>Actual {peso_actual} kg</span></h3>", unsafe_allow_html=True)
                        
                        ganancia_diaria_general = "--"
                        if len(hist_peso) > 1:
                            try:
                                hist_peso_ordenado = hist_peso.sort_values(by="Fecha", ascending=True)
                                p_inicial = float(hist_peso_ordenado.iloc[0]["Detalle 1"])
                                p_final = float(hist_peso_ordenado.iloc[-1]["Detalle 1"])
                                f_inicial = pd.to_datetime(hist_peso_ordenado.iloc[0]["Fecha"])
                                f_final = pd.to_datetime(hist_peso_ordenado.iloc[-1]["Fecha"])
                                dias = (f_final - f_inicial).days
                                if dias > 0:
                                    ganancia_diaria_general = f"{((p_final - p_inicial) / dias):.2f}"
                            except: pass

                        st.caption(f"Ganancia diaria: {ganancia_diaria_general} kg")

                        st.markdown("""
                        <div style="background-color: #4CAF50; color: white; padding: 10px; border-radius: 10px 10px 0 0; display: flex; justify-content: space-between; font-weight: bold; font-size: 14px;">
                            <div style="width:33%">Fecha</div>
                            <div style="width:33%">Peso</div>
                            <div style="width:33%">Ganancia</div>
                        </div>
                        """, unsafe_allow_html=True)

                        if not hist_peso.empty:
                            hist_peso = hist_peso.sort_values(by="Fecha", ascending=True).reset_index(drop=True)
                            ganancias = ["--"]
                            for i in range(1, len(hist_peso)):
                                try:
                                    peso_act = float(hist_peso.iloc[i]["Detalle 1"])
                                    peso_ant = float(hist_peso.iloc[i-1]["Detalle 1"])
                                    diff = peso_act - peso_ant
                                    ganancia_str = f"+{diff:.1f} kg" if diff > 0 else f"{diff:.1f} kg"
                                    ganancias.append(ganancia_str)
                                except:
                                    ganancias.append("--")
                            
                            hist_peso["Ganancia"] = ganancias
                            hist_peso_rev = hist_peso.iloc[::-1]

                            for i, row in hist_peso_rev.iterrows():
                                st.markdown(f"""
                                <div style="background-color: white; padding: 10px; border-bottom: 1px solid #eee; border-left: 1px solid #eee; border-right: 1px solid #eee; display: flex; justify-content: space-between; font-size: 14px;">
                                    <div style="width:33%">{row['Fecha']}</div>
                                    <div style="width:33%">{row['Detalle 1']} kg</div>
                                    <div style="width:33%">{row['Ganancia']}</div>
                                </div>
                                """, unsafe_allow_html=True)
                        else: st.info("Sin registros de peso.")

                    st.markdown("<br>", unsafe_allow_html=True)
                    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                    with col_btn2:
                        if st.button("AGREGAR PESO", type="primary", use_container_width=True):
                            st.session_state.sub_accion_produccion = 'add_peso'
                            st.rerun()
                        st.write("")
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
                                    cambiar_peso_actual = [animal_id, datos["Tipo"], datos["Nombre"], datos["Arete"], datos["Raza"], datos["Sexo"], str(fp_peso), str(datos["Nacimiento"]), datos["Estado"], datos["Foto"]]
                                    actualizar_animal_completo(sh.get_worksheet(0), animal_id, cambiar_peso_actual)
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
                        if st.button("🩺 Tratamiento", use_container_width=True): st.session_state.sub_accion_veterinaria = 'tratamiento'; st.rerun()
                        st.write("")
                        if st.button("🔴 Mastitis", use_container_width=True):  st.session_state.sub_accion_veterinaria = 'mastitis'; st.rerun()
                        st.write("")
                        st.button("🕒 Crear Evento", use_container_width=True) 
                        
                    with col_v2:
                        if st.button("💉 Vacunación", use_container_width=True): st.session_state.sub_accion_veterinaria = 'vacuna'; st.rerun()
                        st.write("")
                        if st.button("🐮 Muerte", use_container_width=True): st.session_state.sub_accion_veterinaria = 'muerte'; st.rerun()

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
                            
                            if row['Tipo Evento'] == "VACUNACION": emoji_tipo = "💉"; titulo_evento = "Vacunación"
                            elif row['Tipo Evento'] == "TRATAMIENTO": emoji_tipo = "💊"; titulo_evento = "Tratamiento"
                            elif row['Tipo Evento'] == "MASTITIS": emoji_tipo = "🔴"; titulo_evento = "Mastitis"
                            elif row['Tipo Evento'] == "MUERTE": emoji_tipo = "💀"; titulo_evento = "Muerte"
                            
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
                            if st.form_submit_button("Cancelar"): st.session_state.sub_accion_veterinaria = None; st.rerun()
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
                            if st.form_submit_button("Cancelar"): st.session_state.sub_accion_veterinaria = None; st.rerun()
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
                                <div class="ubre-row"><div class="ubre-num">1</div><div class="ubre-num">2</div></div>
                                <div class="ubre-row"><div class="ubre-num">3</div><div class="ubre-num">4</div></div>
                            </div>
                            """, unsafe_allow_html=True)
                        with c_m_right:
                            u2 = st.selectbox("Ubre 2 (Der-Del)", GRADOS_MASTITIS)
                            u4 = st.selectbox("Ubre 4 (Der-Tras)", GRADOS_MASTITIS)
                        fm_notas = st.text_area("Notas y observaciones")
                        fm_tratamiento = st.checkbox("Poner en tratamiento")
                        col_cancel_m, col_save_m = st.columns(2)
                        with col_cancel_m:
                            if st.form_submit_button("Cancelar"): st.session_state.sub_accion_veterinaria = None; st.rerun()
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
                            if st.form_submit_button("Cancelar"): st.session_state.sub_accion_veterinaria = None; st.rerun()
                        with col_save_mu:
                            if st.form_submit_button("Registrar", type="primary"):
                                datos_muerte = [str(fmu_fecha), "MUERTE", animal_id, fmu_causa, "", fmu_notas]
                                guardar_evento(sh, datos_muerte, "Muerte")
                                st.session_state.sub_accion_veterinaria = None
                                st.rerun()

            elif st.session_state.nav_gestion == 'reproduccion':
                animal_id = st.session_state.animal_seleccionado
                datos = df[df["ID"] == animal_id].iloc[0]

                if st.button("⬅️ Volver al Perfil", key="btn_back_repro"): ir_a_perfil(animal_id); st.rerun()

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

                st.markdown(f"""
                <div class="repro-stats">
                    <h3>Estado reproductivo</h3>
                    <div class="stat-row"><span>Último parto</span><strong>{ultimo_parto_str}</strong></div>
                    <div class="stat-row"><span>Estado</span><strong>{datos['Estado']}</strong></div>
                    <div class="stat-row" style="border:none;"><span>Días abiertos</span><strong>{dias_abiertos} día(s)</strong></div>
                </div>
                """, unsafe_allow_html=True)

                if st.session_state.sub_accion_reproduccion is None:
                    col_r1, col_r2 = st.columns(2)
                    with col_r1:
                        if st.button("🐮 Fecundación", use_container_width=True): st.session_state.sub_accion_reproduccion = 'fecundacion'; st.rerun()
                        st.write("")
                        if st.button("🏥 Parto", use_container_width=True): st.session_state.sub_accion_reproduccion = 'parto'; st.rerun()
                        st.write("")
                        st.button("🕒 Crear Evento", use_container_width=True) 
                    with col_r2:
                        if st.button("🔍 Chequeo", use_container_width=True): st.session_state.sub_accion_reproduccion = 'chequeo'; st.rerun()
                        st.write("")
                        if st.button("⚠️ Aborto", use_container_width=True):  st.session_state.sub_accion_reproduccion = 'aborto'; st.rerun()

                    st.write("")
                    st.markdown("**Partos/Abortos**")
                    hist_partos = pd.DataFrame()
                    if not df_vaca_hist.empty: hist_partos = df_vaca_hist[df_vaca_hist["Tipo Evento"].isin(["PARTO", "ABORTO"])]

                    st.markdown("""
                    <div class="tabla-header">
                        <div style="width:25%">Fecha</div><div style="width:25%">Tipo</div>
                        <div style="width:25%">Género</div><div style="width:25%">Cría</div>
                    </div>
                    """, unsafe_allow_html=True)

                    if not hist_partos.empty:
                        for idx, row in hist_partos.iloc[::-1].iterrows():
                            genero = "--"; cria_txt = "--"
                            try:
                                d1 = row['Detalle 1']; d2 = row['Detalle 2']
                                if "Macho" in d1: genero = "Macho"
                                elif "Hembra" in d1: genero = "Hembra"
                                if "ID Cría:" in d2: cria_txt = d2.replace("ID Cría:", "").strip()
                            except: pass
                            tipo_txt = "Parto" if row['Tipo Evento'] == "PARTO" else "Aborto"
                            st.markdown(f"""
                            <div class="tabla-row">
                                <div style="width:25%">{row['Fecha']}</div><div style="width:25%">{tipo_txt}</div>
                                <div style="width:25%">{genero}</div><div style="width:25%">{cria_txt}</div>
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
                            emoji_tipo = "🧬"; titulo_evento = row['Tipo Evento']
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
                    
                    if st.button("➕ Registro Rápido", type="primary", key="btn_add_repro"): st.toast("Usa los botones de arriba para agregar registros.")

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

            elif st.session_state.nav_gestion == 'detalle':
                animal_id = st.session_state.animal_seleccionado
                datos = df[df["ID"] == animal_id].iloc[0]

                col_back, col_tit = st.columns([1, 5])
                with col_back:
                    if st.button("⬅️"):
                        ir_a_perfil(animal_id)
                        st.rerun()
                with col_tit: st.subheader("Datos generales")

                with st.container(border=True):
                    st.text_input("Nombre", value=datos['Nombre'], disabled=True)
                    st.text_input("ID", value=datos['ID'], disabled=True)
                    st.text_input("Raza", value=datos['Raza'], disabled=True)
                    st.text_input("Sexo", value=datos['Sexo'], disabled=True)
                    
                    padre_txt = datos.get("Padre", "--") if "Padre" in datos else "--"
                    madre_txt = datos.get("Madre", "--") if "Madre" in datos else "--"
                    
                    c_padres1, c_padres2 = st.columns(2)
                    with c_padres1: st.text_input("Padre", value=padre_txt, disabled=True)
                    with c_padres2: st.text_input("Madre", value=madre_txt, disabled=True)
                    
                    notas_txt = datos.get("Notas", "") if "Notas" in datos else ""
                    if notas_txt: st.text_area("Notas registradas", value=notas_txt, disabled=True)

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
                            # --- FUNCIÓN DE AUTO-REPARACIÓN (Definida aquí para fácil integración) ---
        def reparar_ids_historial_local(sheet_conn):
            try:
                hoja = sheet_conn.worksheet("Historial")
                registros = hoja.get_all_values()
                if not registros: return 0
                
                header = registros[0]
                if len(header) < 7:
                    hoja.update_cell(1, 7, "ID Evento")
                elif header[6].strip() == "":
                    hoja.update_cell(1, 7, "ID Evento")
                
                lista_updates = []
                for i, fila in enumerate(registros):
                    if i == 0: continue # Saltar el encabezado
                    # Si la fila no tiene 7 columnas, o la columna G está vacía
                    if len(fila) < 7 or str(fila[6]).strip() == "":
                        nuevo_id = str(uuid.uuid4())[:8]
                        lista_updates.append({'range': f'G{i+1}', 'values': [[nuevo_id]]})
                
                if lista_updates:
                    hoja.batch_update(lista_updates)
                    cargar_datos.clear() # Limpiar caché para forzar recarga
                return len(lista_updates)
            except Exception as e:
                st.error(f"Error reparando IDs: {e}")
                return 0

        # ==========================================
        # 4. ACCIONES RÁPIDAS (INTEGRADO CON FINANZAS)
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
            
            # --- COMPRA DE GANADO ---
            if st.session_state.accion_activa == "compra":
                st.markdown("<h3>⬅ Compra de ganado</h3>", unsafe_allow_html=True)
                with st.form("form_compra_ganado"):
                    c_c1, c_c2 = st.columns(2)
                    with c_c1: f_fecha_compra = st.date_input("Fecha *", date.today())
                    with c_c2: f_moneda_compra = st.selectbox("Moneda", ["VES", "USD", "COP"])

                    st.markdown('<div class="app-header">Ubicación</div>', unsafe_allow_html=True)
                    c_u1, c_u2 = st.columns(2)
                    with c_u1: f_pais = st.selectbox("País", ["(+58) Venezuela", "Colombia", "Brasil", "Otro"])
                    with c_u2: f_region = st.selectbox("Región", ["Bolívar", "Anzoátegui", "Monagas", "Otra"])
                    f_ciudad = st.selectbox("Ciudad", ["Ciudad Bolívar", "Puerto Ordaz", "Otra"])

                    with st.expander("Información del vendedor", expanded=False):
                        f_vend_nombre = st.text_input("Nombre/Empresa")
                        c_v1, c_v2 = st.columns(2)
                        with c_v1: f_vend_tel = st.text_input("Teléfono/Celular")
                        with c_v2: f_vend_id = st.text_input("Número de identificación")

                    with st.expander("Información del transporte", expanded=False):
                        f_trans_emp = st.text_input("Empresa de transporte")
                        f_trans_guia = st.text_input("Número guía de transporte")

                    st.markdown('<div class="app-header">Datos generales y Pago</div>', unsafe_allow_html=True)
                    c_d1, c_d2 = st.columns(2)
                    with c_d1: f_tipo_animal = st.selectbox("Tipo de animal", ["Bovino", "Porcino", "Ovino", "Caprino", "Equino", "Bufalino", "Otro"])
                    with c_d2: f_precio_kg = st.number_input("Precio por kg *", min_value=0.0)
                    
                    f_monto_total_compra = st.number_input("Costo Total de la Compra (Pago) *", min_value=0.0)
                    
                    opciones_cuentas = df_cuentas['Nombre'].tolist() if not df_cuentas.empty else ["Caja General (Por defecto)"]
                    cuenta_origen = st.selectbox("📤 Cuenta Origen (De donde sale el dinero)", opciones_cuentas)

                    f_responsable = st.text_input("Persona responsable de la compra *")
                    f_notas_compra = st.text_area("Notas y observaciones")

                    st.markdown("---")
                    c_btn_c1, c_btn_c2 = st.columns(2)
                    with c_btn_c1:
                        if st.form_submit_button("Anterior"):
                            st.session_state.accion_activa = None
                            st.rerun()
                    with c_btn_c2:
                        if st.form_submit_button("Siguiente", type="primary"):
                            if f_monto_total_compra > 0 and f_responsable:
                                detalle_compra = f"Vendedor: {f_vend_nombre} | Resp: {f_responsable}"
                                notas_compra = f"Monto Total: {f_monto_total_compra} | Pagado desde: {cuenta_origen} | Ubicación: {f_ciudad}, {f_region} | Precio: {f_precio_kg} {f_moneda_compra}/kg | {f_notas_compra}"
                                datos_compra = [str(f_fecha_compra), "COMPRA", "LOTE EXTERNO", f_tipo_animal, detalle_compra, notas_compra]
                                guardar_evento(sh, datos_compra, "Compra de Ganado")
                                
                                if not df_cuentas.empty:
                                    actualizar_saldo_cuenta(sh, cuenta_origen, -f_monto_total_compra)
                                
                                st.session_state.accion_activa = None
                                st.success("Compra registrada y saldo descontado con éxito.")
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error("Por favor completa los campos obligatorios (*) como el Costo Total y el Responsable.")

            # --- VENTA DE GANADO ---
            elif st.session_state.accion_activa == "venta":
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
                            
                    st.markdown('<div class="seccion-titulo">💰 Datos Económicos y Cobro</div>', unsafe_allow_html=True)
                    pre_select = [st.session_state.animal_seleccionado] if st.session_state.animal_seleccionado and st.session_state.animal_seleccionado in lista_ids_activos else None
                    ids_seleccionados = st.multiselect("Animales (Activos)*", lista_ids_activos, default=pre_select)
                    
                    c_m1, c_m2, c_m3 = st.columns([1,1,2])
                    with c_m1: moneda = st.selectbox("Moneda", ["USD", "VES", "COP"])
                    with c_m2: monto_manual = st.number_input("Precio Total", min_value=0.0)
                    with c_m3: tipo_precio = st.radio("Tipo:", ["Por Kilo", "Por Cabeza", "Lote"], horizontal=True)
                    
                    opciones_cuentas = df_cuentas['Nombre'].tolist() if not df_cuentas.empty else ["Caja General (Por defecto)"]
                    cuenta_destino = st.selectbox("📥 Cuenta Destino (Donde entra el dinero)", opciones_cuentas)
                    
                    notas_venta = st.text_area("Notas")
                    traslado = st.toggle("¿Trasladar a otro usuario de Control Ganadero?")
                    
                    if st.form_submit_button("✅ CONFIRMAR VENTA", type="primary"):
                        if not ids_seleccionados: st.error("Selecciona un animal")
                        else:
                            precio_str = f"{monto_manual} {moneda} ({tipo_precio})"
                            for animal_id in ids_seleccionados:
                                detalle = f"Comp: {comp_nombre} | Dest: {dest_ciudad}"
                                notas_full = f"Ingresa a: {cuenta_destino} | Guia: {trans_guia} | {notas_venta}"
                                datos_venta = [str(fecha_venta), "VENTA", animal_id, precio_str, detalle, notas_full]
                                guardar_evento(sh, datos_venta, "Venta")
                                cambiar_estado_vendido(hoja_animales, animal_id)
                            
                            if not df_cuentas.empty:
                                actualizar_saldo_cuenta(sh, cuenta_destino, monto_manual)
                            
                            st.success("Venta registrada y saldo actualizado.")
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
                        st.rerun()

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
                        st.rerun()

            elif st.session_state.accion_activa == "sanidad":
                if st.session_state.sub_accion_sanidad_rapida is None:
                    st.markdown("<h3>⬅ Selecciona una opción</h3>", unsafe_allow_html=True)
                    c_s1, c_s2 = st.columns(2)
                    with c_s1:
                        if st.button("🩺\nTratamiento masivo", use_container_width=True):
                            st.session_state.sub_accion_sanidad_rapida = "tratamiento_masivo"
                            st.rerun()
                    with c_s2:
                        if st.button("💉\nVacunación masiva", use_container_width=True):
                            st.session_state.sub_accion_sanidad_rapida = "vacunacion_masiva"
                            st.rerun()
                
                elif st.session_state.sub_accion_sanidad_rapida == "tratamiento_masivo":
                    st.markdown("""
                    <div style='background-color: #2e7d32; padding: 10px; color: white; border-radius: 5px 5px 0 0;'>
                        <h3 style='margin:0;'>⬅ Tratamiento masivo</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("⬅ Volver a opciones de sanidad"):
                        st.session_state.sub_accion_sanidad_rapida = None
                        st.rerun()
                    
                    st.markdown('<br>', unsafe_allow_html=True)
                    c_tm1, c_tm2 = st.columns(2)
                    with c_tm1: f_tipo_animal_tm = st.selectbox("Tipo de animal *", LISTA_ESPECIES, index=0, key="tipo_anim_tm")
                    with c_tm2: f_filtro_tm = st.selectbox("Seleccionar animales", ["Todos los animales", "Todos los machos", "Todas las hembras", "Selección manual"], key="filtro_tm")
                    
                    ids_afectados_tm = []
                    if not df_activos.empty:
                        if f_filtro_tm == "Todos los animales": ids_afectados_tm = df_activos['ID'].tolist()
                        elif f_filtro_tm == "Todos los machos": ids_afectados_tm = df_activos[df_activos['Sexo'] == 'Macho']['ID'].tolist()
                        elif f_filtro_tm == "Todas las hembras": ids_afectados_tm = df_activos[df_activos['Sexo'] == 'Hembra']['ID'].tolist()
                        elif f_filtro_tm == "Selección manual": ids_afectados_tm = st.multiselect("Elige los animales", df_activos['ID'].tolist(), key="multi_tm")
                    
                    st.markdown(f"""
                    <div style='background-color: #e0e0e0; padding: 10px; font-weight: bold; text-align: right; border-radius: 0 0 5px 5px; margin-bottom: 15px;'>
                        Total de animales seleccionados: {len(ids_afectados_tm)}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.form("form_tratamiento_masivo_full"):
                        ftm_nombre = st.text_input("Nombre del tratamiento")
                        c_f1, c_f2 = st.columns(2)
                        with c_f1: ftm_fecha = st.date_input("Fecha *", date.today())
                        with c_f2: ftm_dias = st.number_input("Días de tratamiento...", min_value=1, step=1)
                        
                        c_t1, c_t2 = st.columns(2)
                        with c_t1: ftm_tipo = st.selectbox("Tipo de Trat... *", TIPOS_TRATAMIENTO)
                        with c_t2: ftm_enfermedad = st.selectbox("Enfermedad *", LISTA_ENFERMEDADES)
                        
                        ftm_diag = st.text_input("Diagnóstico")
                        ftm_med = st.text_input("Medicamento *")
                        ftm_notas = st.text_area("Notas y observaciones")
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        submitted_tm = st.form_submit_button("Registrar", type="primary")
                        if submitted_tm:
                            if not ids_afectados_tm: st.error("Debe seleccionar al menos un animal.")
                            elif not ftm_med: st.error("El campo 'Medicamento' es obligatorio.")
                            else:
                                with st.spinner(f"Registrando tratamiento para {len(ids_afectados_tm)} animales..."):
                                    for animal_id in ids_afectados_tm:
                                        d1 = f"{ftm_tipo} | {ftm_enfermedad}"
                                        d2 = f"{ftm_med} | {ftm_dias} días"
                                        notas_f = f"Masivo: {ftm_nombre} | Diag: {ftm_diag} | {ftm_notas}"
                                        datos_vet = [str(ftm_fecha), "TRATAMIENTO", str(animal_id), d1, d2, notas_f]
                                        guardar_evento(sh, datos_vet, f"Tratamiento")
                                st.success(f"¡Tratamiento masivo registrado con éxito!")
                                time.sleep(2)
                                st.session_state.sub_accion_sanidad_rapida = None
                                st.rerun()

                elif st.session_state.sub_accion_sanidad_rapida == "vacunacion_masiva":
                    st.markdown("""
                    <div style='background-color: #2e7d32; padding: 10px; color: white; border-radius: 5px 5px 0 0;'>
                        <h3 style='margin:0;'>⬅ Vacunación masiva</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("⬅ Volver a opciones de sanidad"):
                        st.session_state.sub_accion_sanidad_rapida = None
                        st.rerun()

                    st.markdown('<br>', unsafe_allow_html=True)
                    c_vm1, c_vm2 = st.columns(2)
                    with c_vm1: f_tipo_animal_vm = st.selectbox("Tipo de animal *", LISTA_ESPECIES, index=0, key="tipo_anim_vac")
                    with c_vm2: f_filtro_vm = st.selectbox("Seleccionar animales", ["Todos los animales", "Todos los machos", "Todas las hembras", "Selección manual"], key="filtro_vac")
                    
                    ids_afectados_vac = []
                    if not df_activos.empty:
                        if f_filtro_vm == "Todos los animales": ids_afectados_vac = df_activos['ID'].tolist()
                        elif f_filtro_vm == "Todos los machos": ids_afectados_vac = df_activos[df_activos['Sexo'] == 'Macho']['ID'].tolist()
                        elif f_filtro_vm == "Todas las hembras": ids_afectados_vac = df_activos[df_activos['Sexo'] == 'Hembra']['ID'].tolist()
                        elif f_filtro_vm == "Selección manual": ids_afectados_vac = st.multiselect("Elige los animales", df_activos['ID'].tolist(), key="multi_vac")
                    
                    st.markdown(f"""
                    <div style='background-color: #e0e0e0; padding: 10px; font-weight: bold; text-align: right; border-radius: 0 0 5px 5px; margin-bottom: 15px;'>
                        Total de animales seleccionados: {len(ids_afectados_vac)}
                    </div>
                    """, unsafe_allow_html=True)

                    with st.form("form_vacunacion_masiva_full"):
                        fvm_fecha = st.date_input("Fecha *", date.today())
                        fvm_vacuna = st.selectbox("Vacuna *", LISTA_VACUNAS)
                        fvm_notas = st.text_area("Notas y observaciones")
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        submitted_vm = st.form_submit_button("Registrar", type="primary")
                        if submitted_vm:
                            if not ids_afectados_vac: st.error("Debe seleccionar al menos un animal.")
                            else:
                                with st.spinner(f"Registrando vacunación para {len(ids_afectados_vac)} animales..."):
                                    for animal_id in ids_afectados_vac:
                                        datos_vac = [str(fvm_fecha), "VACUNACION", str(animal_id), fvm_vacuna, "", f"Masiva | {fvm_notas}"]
                                        guardar_evento(sh, datos_vac, "Vacunación")
                                st.success(f"¡Vacunación masiva registrada con éxito!")
                                time.sleep(2)
                                st.session_state.sub_accion_sanidad_rapida = None
                                st.rerun()

            elif st.session_state.accion_activa is None:
                st.info("👆 Selecciona una opción arriba.")

        # ==========================================
        # 5. 🏦 MÓDULO DE FINANZAS Y CUENTAS
        # ==========================================
        with tab_finanzas:
            st.markdown("""
            <div style='text-align:center; padding: 10px; margin-bottom: 20px;'>
                <h2 style='margin:0; color: #1976d2;'>Gestión de Cuentas y Finanzas</h2>
                <p style='color:#666;'>Control de Flujo de Caja, Cuentas Bancarias y Aportes</p>
            </div>
            """, unsafe_allow_html=True)
            
            sub_bal, sub_hist, sub_ingresos, sub_gastos, sub_transf, sub_capital, sub_config = st.tabs([
                "📊 Balance", "📜 Historial", "💰 Ingresos", "💸 Gastos", "🔄 Transferencias", "📥 Capital", "⚙️ Configurar"
            ])
            
            # --- 5.1 BALANCE ---
            with sub_bal:
                st.markdown("### Estado Financiero Actual")
                if not df_cuentas.empty:
                    cols = st.columns(3)
                    for i, row in df_cuentas.iterrows():
                        col = cols[i % 3]
                        with col:
                            st.markdown(f"""
                            <div class="cuenta-card">
                                <div class="cuenta-title">{row['Nombre']}</div>
                                <div class="cuenta-saldo">{float(row['Saldo']):,.2f} <span class="cuenta-moneda">{row['Moneda']}</span></div>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("No hay cuentas creadas. Ve a '⚙️ Configurar Cuentas' para empezar.")

            # --- 5.2 HISTORIAL DETALLADO ---
            with sub_hist:
                st.markdown("### 📜 Historial de Movimientos")
                
                # --- DETECCIÓN DE IDs FALTANTES PARA AUTO-REPARACIÓN ---
                if not df_hist.empty:
                    faltan_id = 0
                    if "ID Evento" not in df_hist.columns:
                        faltan_id = len(df_hist)
                    else:
                        faltan_id = len(df_hist[df_hist["ID Evento"].astype(str).str.strip() == ""])
                        
                    if faltan_id > 0:
                        st.warning(f"⚠️ Se detectaron **{faltan_id}** registros antiguos sin 'ID Evento'. Para poder anularlos, el sistema debe asignarles un código único.")
                        if st.button("🛠️ Generar IDs Faltantes Automáticamente", type="primary"):
                            with st.spinner("Inyectando IDs en tu base de datos... esto puede tardar unos segundos..."):
                                arreglados = reparar_ids_historial_local(sh)
                                if arreglados > 0:
                                    st.success(f"¡Se asignaron {arreglados} IDs con éxito!")
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    st.error("Hubo un problema. Verifica tu conexión a Google Sheets.")
                        st.markdown("---")

                st.markdown("#### 🗑️ Anular transacción")
                st.write("Copia el 'ID Evento' que aparece en las tarjetas de abajo y pégalo aquí para eliminar el movimiento y revertir el saldo de tu cuenta bancaria.")
                c_del1, c_del2 = st.columns([3, 1])
                with c_del1:
                    id_a_eliminar = st.text_input("Ingrese el ID del Evento a eliminar:", placeholder="Ej: a1b2c3d4")
                with c_del2:
                    st.write("") 
                    if st.button("Anular Transacción", type="primary", use_container_width=True):
                        if id_a_eliminar:
                            if eliminar_evento_finanzas_por_id(sh, id_a_eliminar):
                                st.rerun()
                        else:
                            st.warning("Ingrese un ID válido primero.")
                st.markdown("---")

                # Calendario y Filtros de Fecha
                c_filtro1, c_filtro2 = st.columns([1, 2])
                with c_filtro1:
                    filtro_fecha = st.selectbox("📅 Filtrar por fecha", ["Todos los tiempos", "Hoy", "Esta semana", "Este mes", "Mes pasado", "Rango personalizado"])
                
                f_inicio = None
                f_fin = None
                hoy = date.today()
                
                if filtro_fecha == "Hoy":
                    f_inicio = hoy
                    f_fin = hoy
                elif filtro_fecha == "Esta semana":
                    f_inicio = hoy - timedelta(days=hoy.weekday())
                    f_fin = hoy
                elif filtro_fecha == "Este mes":
                    f_inicio = hoy.replace(day=1)
                    f_fin = hoy
                elif filtro_fecha == "Mes pasado":
                    f_fin = hoy.replace(day=1) - timedelta(days=1)
                    f_inicio = f_fin.replace(day=1)
                elif filtro_fecha == "Rango personalizado":
                    with c_filtro2:
                        fechas = st.date_input("Selecciona el rango:", [hoy - timedelta(days=7), hoy])
                        if len(fechas) == 2:
                            f_inicio, f_fin = fechas
                
                if not df_hist.empty and "Tipo Evento" in df_hist.columns:
                    tipos_financieros = ["VENTA", "COMPRA", "TRANSFERENCIA", "APORTE_CAPITAL", "GASTO_OPERATIVO", "INGRESO_OPERATIVO"]
                    df_finanzas = df_hist[df_hist["Tipo Evento"].isin(tipos_financieros)].copy()
                    
                    if f_inicio and f_fin:
                        df_finanzas["Fecha_DT"] = pd.to_datetime(df_finanzas["Fecha"], errors='coerce').dt.date
                        df_finanzas = df_finanzas[(df_finanzas["Fecha_DT"] >= f_inicio) & (df_finanzas["Fecha_DT"] <= f_fin)]
                    
                    if not df_finanzas.empty:
                        df_finanzas_rev = df_finanzas.iloc[::-1]
                        
                        for _, row in df_finanzas_rev.iterrows():
                            tipo = row["Tipo Evento"]
                            fecha = row["Fecha"]
                            
                            id_evento = str(row.get("ID Evento", ""))
                            if not id_evento.strip(): id_evento = "N/A"
                            
                            icon = "📄"
                            css_class = "fin-neu"
                            titulo = tipo
                            sub = f"ID Evento: **{id_evento}** | {row['Detalle 1']}"
                            notas = str(row['Notas'])
                            
                            if tipo == "VENTA":
                                icon = "📈"
                                css_class = "fin-pos"
                                titulo = "Ingreso por Venta de Ganado"
                                sub = f"ID Evento: **{id_evento}** | Animal: {row['ID Animal']} | {row['Detalle 2']}"
                            elif tipo == "COMPRA":
                                icon = "📉"
                                css_class = "fin-neg"
                                titulo = "Egreso por Compra de Ganado"
                                sub = f"ID Evento: **{id_evento}** | {row['Detalle 1']}"
                            elif tipo == "APORTE_CAPITAL":
                                icon = "📥"
                                css_class = "fin-pos"
                                titulo = "Aporte de Capital / Préstamo"
                                sub = f"ID Evento: **{id_evento}** | {row['Detalle 1']}"
                            elif tipo == "GASTO_OPERATIVO":
                                icon = "💸"
                                css_class = "fin-neg"
                                titulo = "Gasto Operativo"
                                sub = f"ID Evento: **{id_evento}** | {row['Detalle 2']} | {row['Detalle 1']}"
                            elif tipo == "INGRESO_OPERATIVO":
                                icon = "💰"
                                css_class = "fin-pos"
                                titulo = "Ingreso Operativo (Subproductos)"
                                sub = f"ID Evento: **{id_evento}** | {row['Detalle 2']} | {row['Detalle 1']}"
                            elif tipo == "TRANSFERENCIA":
                                icon = "🔄"
                                css_class = "fin-neu"
                                titulo = "Transferencia entre cuentas"
                                sub = f"ID Evento: **{id_evento}** | {row['Detalle 1']} ➔ {row['Detalle 2']}"

                            st.markdown(f"""
                            <div class="fin-row {css_class}">
                                <div class="fin-icon">{icon}</div>
                                <div class="fin-details">
                                    <div class="fin-title">{titulo}</div>
                                    <div class="fin-subtitle">{sub}</div>
                                    <div class="fin-notas">{notas}</div>
                                </div>
                                <div class="fin-date">{fecha}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info(f"No hay movimientos financieros para el filtro de fecha actual.")
                else:
                    st.info("El historial está vacío.")

            # --- 5.3 INGRESOS OPERATIVOS ---
            with sub_ingresos:
                st.markdown("### 💰 Registro de Ingresos Operativos")
                st.write("Registra las ventas del día a día como queso, leche, suero, huevos, cosechas, etc.")
                if not df_cuentas.empty:
                    with st.form("form_ingresos_operativos"):
                        c_i1, c_i2 = st.columns(2)
                        with c_i1: 
                            categoria_ingreso = st.selectbox("Categoría de Ingreso", [
                                "Venta de Queso", "Venta de Leche", "Venta de Huevos", 
                                "Venta de Cosecha/Siembra", "Venta de Subproductos", "Otros Ingresos"
                            ])
                        with c_i2: cta_cobro = st.selectbox("Ingresa a (Cuenta Bancaria/Caja)", df_cuentas['Nombre'].tolist())
                        
                        monto_ingreso = st.number_input("Monto Recibido", min_value=0.0)
                        desc_ingreso = st.text_input("Descripción detallada (Ej: 20kg de Queso Llanero o 5 cartones de huevo)")
                        
                        if st.form_submit_button("Registrar Ingreso", type="primary"):
                            if monto_ingreso > 0:
                                actualizar_saldo_cuenta(sh, cta_cobro, monto_ingreso)
                                datos_ingreso = [str(date.today()), "INGRESO_OPERATIVO", "FINANZAS", f"Monto: {monto_ingreso} (Cuenta: {cta_cobro})", categoria_ingreso, desc_ingreso]
                                guardar_evento(sh, datos_ingreso, "Ingreso registrado")
                                st.rerun()
                            else: st.error("Monto inválido.")
                else: st.info("Crea una cuenta para poder registrar ingresos.")

            # --- 5.4 GASTOS OPERATIVOS ---
            with sub_gastos:
                st.markdown("### 💸 Registro de Gastos Operativos")
                if not df_cuentas.empty:
                    with st.form("form_gastos"):
                        c_g1, c_g2 = st.columns(2)
                        with c_g1: categoria_gasto = st.selectbox("Categoría", ["Alimentación (Concentrado/Pasto)", "Medicinas / Veterinaria", "Nómina / Personal", "Mantenimiento / Equipos", "Servicios", "Otros Gastos"])
                        with c_g2: cta_pago = st.selectbox("Pagado desde (Cuenta)", df_cuentas['Nombre'].tolist())
                        
                        monto_gasto = st.number_input("Monto del Gasto", min_value=0.0)
                        desc_gasto = st.text_input("Descripción detallada (Ej: 10 Sacos de Alimento)")
                        
                        if st.form_submit_button("Registrar Gasto", type="primary"):
                            if monto_gasto > 0:
                                actualizar_saldo_cuenta(sh, cta_pago, -monto_gasto)
                                datos_gasto = [str(date.today()), "GASTO_OPERATIVO", "FINANZAS", f"Monto: {monto_gasto} (Cuenta: {cta_pago})", categoria_gasto, desc_gasto]
                                guardar_evento(sh, datos_gasto, "Gasto registrado")
                                st.rerun()
                            else: st.error("Monto inválido.")
                else: st.info("Crea una cuenta para poder registrar gastos.")

            # --- 5.5 TRANSFERENCIAS / CANJE ---
            with sub_transf:
                st.markdown("### 🔄 Transferencias y Cambio de Divisas")
                st.write("Mueve dinero entre cuentas o registra cambios de divisa.")
                if not df_cuentas.empty and len(df_cuentas) >= 2:
                    with st.form("form_transferencia"):
                        lista_ctas = df_cuentas['Nombre'].tolist()
                        c_t1, c_t2 = st.columns(2)
                        with c_t1: cta_origen = st.selectbox("📤 Cuenta ORIGEN (Sale dinero)", lista_ctas, index=0)
                        with c_t2: cta_destino = st.selectbox("📥 Cuenta DESTINO (Entra dinero)", lista_ctas, index=1)
                        
                        monto_transferir = st.number_input("Monto a debitar del Origen", min_value=0.0)
                        tasa_cambio = st.number_input("Tasa de cambio (Opcional, multiplicador)", value=1.0, min_value=0.01)
                        monto_recibir = monto_transferir * tasa_cambio
                        st.info(f"La cuenta destino recibirá: **{monto_recibir:,.2f}**")
                        
                        if st.form_submit_button("Realizar Transferencia", type="primary"):
                            if cta_origen == cta_destino: st.error("❌ La cuenta origen y destino no pueden ser la misma.")
                            elif monto_transferir <= 0: st.error("❌ El monto debe ser mayor a 0.")
                            else:
                                actualizar_saldo_cuenta(sh, cta_origen, -monto_transferir)
                                actualizar_saldo_cuenta(sh, cta_destino, monto_recibir)
                                datos_transf = [str(date.today()), "TRANSFERENCIA", "FINANZAS", f"De: {cta_origen}", f"A: {cta_destino}", f"Monto Origen: {monto_transferir} | Monto Recibido: {monto_recibir}"]
                                guardar_evento(sh, datos_transf, "Transferencia completada")
                                st.rerun()
                else:
                    st.warning("Necesitas al menos 2 cuentas creadas para hacer transferencias.")

            # --- 5.6 CAPITAL / PRÉSTAMO (INYECCIÓN DE DINERO) ---
            with sub_capital:
                st.markdown("### 📥 Registrar Capital o Préstamo")
                st.write("Añade dinero de tu bolsillo o banco sin que cuente como un Ingreso Operativo.")
                if not df_cuentas.empty:
                    with st.form("form_capital"):
                        cta_capital = st.selectbox("Cuenta Destino (Dónde cayó el dinero)", df_cuentas['Nombre'].tolist())
                        concepto_cap = st.selectbox("Concepto", ["Aporte de Propietario (Bolsillo)", "Préstamo Bancario", "Préstamo Terceros", "Otro"])
                        monto_cap = st.number_input("Monto Recibido", min_value=0.0)
                        notas_cap = st.text_area("Notas / Razón (Opcional)")
                        
                        if st.form_submit_button("Ingresar Dinero", type="primary"):
                            if monto_cap > 0:
                                actualizar_saldo_cuenta(sh, cta_capital, monto_cap)
                                datos_cap = [str(date.today()), "APORTE_CAPITAL", "FINANZAS", f"Cuenta: {cta_capital}", f"Monto: {monto_cap}", f"Concepto: {concepto_cap} | {notas_cap}"]
                                guardar_evento(sh, datos_cap, "Aporte registrado")
                                st.rerun()
                            else: st.error("El monto debe ser mayor a 0.")
                else: st.info("Crea una cuenta primero.")

            # --- 5.7 CONFIGURAR CUENTAS ---
            with sub_config:
                st.markdown("### ⚙️ Nueva Cuenta")
                with st.form("form_crear_cuenta"):
                    c_cc1, c_cc2, c_cc3 = st.columns(3)
                    with c_cc1: nom_cta = st.text_input("Nombre (Ej: Banco Banesco, Caja Fuerte)")
                    with c_cc2: mon_cta = st.selectbox("Moneda", ["USD ($)", "VES (Bs)", "COP", "EUR"])
                    with c_cc3: saldo_ini = st.number_input("Saldo Inicial", value=0.0)
                    
                    if st.form_submit_button("Crear Cuenta"):
                        if nom_cta:
                            crear_cuenta(sh, nom_cta, mon_cta, saldo_ini)
                            st.rerun()
                        else: st.error("El nombre es obligatorio.")

        # ==========================================
        # 6. ALERTAS AUTOMÁTICAS
        # ==========================================
        with tab_alertas:
            st.header("🔔 Centro de Alertas")
            st.write("El sistema analiza automáticamente tu rebaño para detectar acciones pendientes.")

            alertas_generadas = []

            # 1. Alertas de Destete (Becerros >= 210 días)
            if not df_activos.empty:
                becerros = df_activos[df_activos['Tipo'] == 'Becerro']
                for _, row in becerros.iterrows():
                    try:
                        nac = pd.to_datetime(row['Nacimiento'])
                        dias_vida = (pd.Timestamp(date.today()) - nac).days
                        if dias_vida >= 210:
                            alertas_generadas.append({
                                "tipo": "Destete", "animal": f"{row['Nombre']} (ID: {row['ID']})",
                                "msg": f"Alcanzó la edad de destete ({dias_vida} días).",
                                "icon": "🍼", "color": "#f57c00"
                            })
                    except: pass

            # 2. Alertas Reproductivas (Parto y Secado)
            if not df_activos.empty and not df_hist.empty:
                vacas_prenadas = df_activos[df_activos['Estado'] == 'Preñada']
                df_repro = df_hist[df_hist['Tipo Evento'].isin(['FECUNDACION', 'CHEQUEO_REPRO'])]
                for _, vaca in vacas_prenadas.iterrows():
                    eventos = df_repro[df_repro['ID Animal'] == vaca['ID']].sort_values(by='Fecha')
                    if not eventos.empty:
                        ult_fecha = pd.to_datetime(eventos.iloc[-1]['Fecha'])
                        dias_gest = (pd.Timestamp(date.today()) - ult_fecha).days
                        if dias_gest >= 280:
                            alertas_generadas.append({
                                "tipo": "Alerta de Parto", "animal": f"{vaca['Nombre']} (ID: {vaca['ID']})",
                                "msg": f"Posible parto inminente. {dias_gest} días de gestación.",
                                "icon": "🚨", "color": "#d32f2f"
                            })
                        elif 220 <= dias_gest < 280:
                            alertas_generadas.append({
                                "tipo": "Secado de Vaca", "animal": f"{vaca['Nombre']} (ID: {vaca['ID']})",
                                "msg": f"Requiere secado para preparar el parto. {dias_gest} días de gestación.",
                                "icon": "🛑", "color": "#1976d2"
                            })

            # 3. Alertas Sanitarias (Tratamientos por terminar)
            if not df_hist.empty:
                df_trat = df_hist[df_hist['Tipo Evento'] == 'TRATAMIENTO']
                for _, trat in df_trat.iterrows():
                    try:
                        f_inicio = pd.to_datetime(trat['Fecha'])
                        det2 = str(trat['Detalle 2'])
                        if "días" in det2:
                            dias_trat = int(det2.split("|")[1].replace("días", "").strip())
                            f_fin = f_inicio + pd.Timedelta(days=dias_trat)
                            hoy = pd.Timestamp(date.today())
                            if f_inicio <= hoy <= f_fin:
                                dias_restantes = (f_fin - hoy).days
                                if dias_restantes <= 2:
                                    enfermedad = trat['Detalle 1'].split('|')[1] if '|' in trat['Detalle 1'] else "Tratamiento"
                                    alertas_generadas.append({
                                        "tipo": "Atención Sanitaria", "animal": f"ID: {trat['ID Animal']}",
                                        "msg": f"{enfermedad} termina en {dias_restantes} día(s). Revisar evolución.",
                                        "icon": "💊", "color": "#388e3c"
                                    })
                    except: pass

            # Renderizar Alertas
            if alertas_generadas:
                for alerta in alertas_generadas:
                    st.markdown(f"""
                    <div class="alerta-card" style="border-left-color: {alerta['color']};">
                        <div class="alerta-icon">{alerta['icon']}</div>
                        <div class="alerta-content">
                            <div class="alerta-title" style="color: {alerta['color']};">{alerta['tipo']}</div>
                            <p class="alerta-desc"><span class="alerta-animal">{alerta['animal']}</span> - {alerta['msg']}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("✅ Todo al día. No hay alertas pendientes de parto, destete o sanidad.")

        # ==========================================
        # 7. MÓDULO DE REPORTES Y EXPORTACIÓN
        # ==========================================
        with tab_reportes:
            st.header("📑 Reportes y Exportación")
            st.write("Genera y descarga informes de la finca en formato compatible con Excel (.csv) o PDF clínico.")
            
            col_rep1, col_rep2 = st.columns(2)
            
            with col_rep1:
                st.markdown('<div class="dash-card">', unsafe_allow_html=True)
                st.subheader("1. Inventario Activo")
                st.write("Descarga la lista completa de todos los animales actualmente en la finca.")
                if not df_activos.empty:
                    csv_inventario = df_activos.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Descargar Inventario (CSV)",
                        data=csv_inventario,
                        file_name=f"Inventario_Finca_{date.today()}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.warning("No hay animales activos para exportar.")
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="dash-card">', unsafe_allow_html=True)
                st.subheader("3. Producción Consolidada")
                st.write("Exporta todos los registros de pesajes y producción de leche.")
                if not df_hist.empty:
                    df_prod = df_hist[df_hist['Tipo Evento'].isin(['PESAJE', 'PRODUCCION_LECHE'])]
                    if not df_prod.empty:
                        csv_prod = df_prod.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Descargar Producción (CSV)",
                            data=csv_prod,
                            file_name=f"Produccion_Total_{date.today()}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    else:
                        st.warning("No hay registros de producción.")
                else:
                    st.info("No hay historial disponible.")
                st.markdown('</div>', unsafe_allow_html=True)

            with col_rep2:
                st.markdown('<div class="dash-card">', unsafe_allow_html=True)
                st.subheader("2. Historial Clínico (PDF)")
                st.write("Genera un reporte médico detallado de un animal en formato PDF.")
                
                animal_reporte = st.selectbox("Seleccione el animal:", lista_ids_todos, key="sel_rep_animal")
                
                if animal_reporte and not df.empty and not df_hist.empty:
                    try:
                        info_animal = df[df['ID'] == animal_reporte].iloc[0]
                        hist_animal = df_hist[df_hist['ID Animal'] == str(animal_reporte)]
                        hist_medico = hist_animal[hist_animal['Tipo Evento'].isin(['TRATAMIENTO', 'VACUNACION', 'MASTITIS', 'MUERTE'])]
                        
                        if st.button("📄 Generar PDF Clínico", type="primary", use_container_width=True):
                            pdf = FPDF()
                            pdf.add_page()
                            
                            pdf.set_font("Arial", 'B', 16)
                            pdf.cell(200, 10, txt="HISTORIAL CLINICO VETERINARIO", ln=True, align='C')
                            pdf.ln(5)
                            
                            pdf.set_font("Arial", 'B', 12)
                            pdf.cell(200, 8, txt=f"FECHA DE REPORTE: {date.today()}", ln=True)
                            pdf.set_font("Arial", '', 12)
                            pdf.cell(200, 8, txt=f"ANIMAL: {info_animal['Nombre']} (ID: {info_animal['ID']})", ln=True)
                            pdf.cell(200, 8, txt=f"RAZA: {info_animal['Raza']} | SEXO: {info_animal['Sexo']} | NAC: {info_animal['Nacimiento']}", ln=True)
                            pdf.cell(200, 8, txt=f"ESTADO ACTUAL: {info_animal['Estado']}", ln=True)
                            pdf.ln(5)
                            
                            pdf.set_font("Arial", 'B', 14)
                            pdf.cell(200, 10, txt="REGISTROS MEDICOS:", ln=True)
                            
                            if hist_medico.empty:
                                pdf.set_font("Arial", '', 12)
                                pdf.cell(200, 8, txt="No se encontraron registros medicos para este animal.", ln=True)
                            else:
                                for _, ev in hist_medico.iterrows():
                                    pdf.set_font("Arial", 'B', 12)
                                    pdf.cell(200, 8, txt=f"[{ev['Fecha']}] {ev['Tipo Evento']}", ln=True)
                                    pdf.set_font("Arial", '', 12)
                                    pdf.multi_cell(0, 8, txt=f"Detalle: {ev['Detalle 1']} | {ev['Detalle 2']}")
                                    if str(ev['Notas']).strip():
                                        pdf.multi_cell(0, 8, txt=f"Notas: {ev['Notas']}")
                                    pdf.ln(2)
                            
                            pdf_bytes = pdf.output(dest='S').encode('latin-1')
                            
                            st.success("✅ PDF Generado con éxito.")
                            st.download_button(
                                label="⬇️ Haz clic aquí para descargar el PDF",
                                data=pdf_bytes,
                                file_name=f"Historial_{info_animal['Nombre']}_{info_animal['ID']}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                    except Exception as e:
                        st.error(f"Error al generar PDF: {e}")
                st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
