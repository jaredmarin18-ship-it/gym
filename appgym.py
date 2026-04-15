import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import os

# 1. CONFIGURACIÓN Y LOGO
st.set_page_config(page_title="Olympus Gym - Control", page_icon="🏋️‍♂️")

try:
    st.image("logo.png", width=250)
except:
    st.title("🏋️‍♂️ OLYMPUS GYM")

# 2. ARCHIVO DE BASE DE DATOS
ARCHIVO = "datos_olympus_web.json"

# 3. FUNCIÓN PARA CARGAR DATOS
def cargar_datos():
    estructura_limpia = {
        "socios": {}, 
        "caja_efectivo": 0.0, 
        "transferencias": 0.0, 
        "gastos_totales": 0.0,
        "historial": []
    }
    if os.path.exists(ARCHIVO):
        try:
            with open(ARCHIVO, "r") as f:
                datos = json.load(f)
                for llave in estructura_limpia:
                    if llave not in datos:
                        datos[llave] = estructura_limpia[llave]
                return datos
        except:
            return estructura_limpia
    return estructura_limpia

if "datos" not in st.session_state:
    st.session_state.datos = cargar_datos()

def guardar():
    with open(ARCHIVO, "w") as f:
        json.dump(st.session_state.datos, f, indent=4)

# --- INTERFAZ ---
st.sidebar.header("Menú Olympus")
menu = st.sidebar.selectbox("Seleccione acción", 
    ["Registrar Pago", "Registrar Gasto", "Ver Reporte y Caja", "Lista de Socios", "Ajustes de Caja"])

if menu == "Registrar Pago":
    st.subheader("📝 Nuevo Registro de Pago")
    tipo = st.selectbox("Producto", ["Mes ($25)", "Tarjeta 10 ($13.50)", "Día ($3)"])
    metodo = st.radio("Método de Pago", ["Efectivo", "Transferencia (Osmany)"])
    nombre = st.text_input("Nombre del Cliente").upper().strip()

    if st.button("Confirmar Pago"):
        if nombre or tipo == "Día ($3)":
            hoy = datetime.now()
            
            # --- VALIDACIÓN DE NOMBRE DUPLICADO ---
            if "Mes" in tipo:
                socios_actuales = st.session_state.datos.get("socios", {})
                if nombre in socios_actuales:
                    fecha_venc_str = socios_actuales[nombre]
                    fecha_venc = datetime.strptime(fecha_venc_str, "%d/%m/%Y")
                    
                    if fecha_venc > hoy:
                        st.error(f"❌ ERROR: {nombre} ya tiene una mensualidad activa que vence el {fecha_venc_str}.")
                        st.info("No se puede registrar de nuevo hasta que venza el mes.")
                        st.stop() # Detiene la ejecución para que no guarde el pago

            # Si pasa la validación, procedemos:
            precios = {"Mes ($25)": 25.0, "Tarjeta 10 ($13.50)": 13.50, "Día ($3)": 3.0}
            monto = precios[tipo]
            
            if metodo == "Efectivo": st.session_state.datos["caja_efectivo"] += monto
            else: st.session_state.datos["transferencias"] += monto
            
            if "Mes" in tipo:
                venc = (hoy + timedelta(days=30)).strftime("%d/%m/%Y")
                st.session_state.datos["socios"][nombre] = venc
                detalle_historial = f"INGRESO: {nombre} - Mes (Vence: {venc})"
            else:
                nombre_final = nombre if nombre else "CLIENTE DIARIO"
                detalle_historial = f"INGRESO: {nombre_final} - {tipo}"
            
            st.session_state.datos["historial"].append(f"{hoy.strftime('%H:%M')} - {detalle_historial} ({metodo})")
            guardar()
            st.success(f"✅ ¡Registro completado con éxito!")
        else:
            st.warning("⚠️ Por favor, ingresá el nombre del cliente.")

elif menu == "Registrar Gasto":
    st.subheader("💸 Salida de Dinero")
    motivo = st.text_input("Concepto del Gasto").upper()
    monto_gasto = st.number_input("Monto ($)", min_value=0.0, step=0.50)
    
    if st.button("Confirmar Gasto"):
        if motivo and monto_gasto > 0:
            if monto_gasto <= st.session_state.datos["caja_efectivo"]:
                st.session_state.datos["caja_efectivo"] -= monto_gasto
                st.session_state.datos["gastos_totales"] += monto_gasto
                st.session_state.datos["historial"].append(f"{datetime.now().strftime('%H:%M')} - GASTO: {motivo} (-${monto_gasto:.2f})")
                guardar()
                st.success("✅ Gasto registrado.")
            else: st.error("❌ No hay suficiente efectivo en caja.")

elif menu == "Ver Reporte y Caja":
    st.subheader("💰 Resumen de Caja")
    efectivo = st.session_state.datos.get("caja_efectivo", 0.0)
    banco = st.session_state.datos.get("transferencias", 0.0)
    gastos = st.session_state.datos.get("gastos_totales", 0.0)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Efectivo", f"${efectivo:.2f}")
    c2.metric("Banco", f"${banco:.2f}")
    c3.metric("Gastos", f"${gastos:.2f}")
    
    st.divider()
    st.write("### Historial de hoy:")
    for mov in reversed(st.session_state.datos.get("historial", [])):
        st.write(f"• {mov}")

elif menu == "Lista de Socios":
    st.subheader("📋 Socios Activos")
    socios = st.session_state.datos.get("socios", {})
    if socios:
        # Mostramos quiénes están activos y quiénes ya vencieron
        hoy = datetime.now()
        lista_tabla = []
        for s, f in socios.items():
            fv = datetime.strptime(f, "%d/%m/%Y")
            estado = "✅ ACTIVO" if fv > hoy else "🛑 VENCIDO"
            lista_tabla.append({"Socio": s, "Vencimiento": f, "Estado": estado})
        
        df = pd.DataFrame(lista_tabla)
        st.table(df)
    else: st.info("No hay socios registrados.")

elif menu == "Ajustes de Caja":
    st.subheader("🔧 Corrección Manual de Caja")
    col_ajuste1, col_ajuste2 = st.columns(2)
    nuevo_efectivo = col_ajuste1.number_input("Corregir Efectivo a:", value=st.session_state.datos["caja_efectivo"])
    nuevo_banco = col_ajuste2.number_input("Corregir Banco a:", value=st.session_state.datos["transferencias"])
    razon = st.text_input("Motivo del ajuste")

    if st.button("Aplicar Cambios Manuales"):
        if razon:
            st.session_state.datos["caja_efectivo"] = nuevo_efectivo
            st.session_state.datos["transferencias"] = nuevo_banco
            st.session_state.datos["historial"].append(f"{datetime.now().strftime('%H:%M')} - ⚠️ AJUSTE MANUAL: {razon}")
            guardar()
            st.success("✅ Caja actualizada.")
            st.rerun()
        else: st.error("⚠️ Debes poner una razón.")