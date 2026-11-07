import streamlit as st
import datetime
import json
import os

# Configuración de la pantalla móvil para internet
st.set_page_config(page_title="Control WISP", page_icon="📶", layout="centered")

# Almacenamiento seguro en la sesión de la nube
ARCHIVO_DATOS = "clientes.json"
PLANES_INTERNET = {
    1: {"megas": "20 Megas", "precio": 500.00},
    2: {"megas": "25 Megas", "precio": 600.00},
    3: {"megas": "100 Megas", "precio": 350.00}
}

# Inicializar la base de datos en la memoria de la nube si no existe
if "lista_clientes" not in st.session_state:
    if os.path.exists(ARCHIVO_DATOS):
        try:
            with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
                st.session_state.lista_clientes = json.load(f)
        except:
            st.session_state.lista_clientes = []
    else:
        # Cliente de prueba inicial si la base está vacía
        st.session_state.lista_clientes = [
            {
                "contrato": 1,
                "nombre": "Juan Vázquez (Prueba Nube)",
                "plan": "20 Megas",
                "mensualidad": 500.00,
                "fecha_corte": "2026-11-24",
                "estado": "Activo"
            }
        ]

lista_clientes = st.session_state.lista_clientes

st.title("📶 Sistema de Control WISP")
st.write("☁️ Servidor Central en la Nube de Internet")

# DISEÑO DE PESTAÑAS MÓVILES
pestana1, pestana2, pestana3 = st.tabs(["📋 Lista de Clientes", "➕ Registrar Nuevo", "💳 Recibir Pago"])

# --- PESTAÑA 1: MOSTRAR Y FILTRAR CLIENTES ---
with pestana1:
    st.subheader("Fichas Técnicas Activas")
    
    if st.button("🔍 Verificar cortes automáticos de hoy", type="primary"):
        hoy_str = datetime.date.today().strftime("%Y-%m-%d")
        hubo_changes = False
        for c in lista_clientes:
            if c["fecha_corte"] <= hoy_str and c["estado"] != "Suspendido":
                c["estado"] = "Suspendido"
                hubo_changes = True
        if hubo_changes:
            with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
                json.dump(lista_clientes, f, indent=4, ensure_ascii=False)
            st.warning("🚨 Se han actualizado nuevos clientes al estado 'Suspendido'.")
        else:
            st.success("✅ Todos los clientes están al día hoy.")

    if not lista_clientes:
        st.info("No hay clientes registrados en el sistema.")
    else:
        for c in lista_clientes:
            f_corte = datetime.datetime.strptime(c["fecha_corte"], "%Y-%m-%d").strftime("%d/%m/%Y")
            color_estado = "🟢 Activo" if c["estado"] == "Activo" else "🔴 Suspendido"
            
            with st.container(border=True):
                st.markdown(f"### **Contrato #{c['contrato']} - {c['nombre']}**")
                st.write(f"**Plan:** {c['plan']} | **Mensualidad:** ${c['mensualidad']}")
                st.write(f"**Próximo Corte:** {f_corte}")
                st.markdown(f"**Estado:** {color_estado}")

# --- PESTAÑA 2: FORMULARIO DE REGISTRO TÁCTIL ---
with pestana2:
    st.subheader("Alta de Nuevo Suscriptor")
    with st.form("formulario_registro", clear_on_submit=True):
        num_contrato = st.number_input("Número de Contrato:", min_value=1, step=1)
        nombre_cliente = st.text_input("Nombre Completo del Cliente:")
        
        opciones_planes = {f"{v['megas']} (${v['precio']})": k for k, v in PLANES_INTERNET.items()}
        plan_seleccionado = st.selectbox("Selecciona el Paquete de Internet:", list(opciones_planes.keys()))
        id_plan = opciones_planes[plan_seleccionado]
        
        dia_corte = st.slider("Día de corte mensual (1 al 28):", min_value=1, max_value=28, value=24)
        enviar_registro = st.form_submit_button("💾 Guardar Cliente en la Nube")
        
        if enviar_registro:
            if any(c["contrato"] == num_contrato for c in lista_clientes):
                st.error("❌ Error: Ese número de contrato ya existe.")
            elif not nombre_cliente:
                st.error("❌ Error: Debes ingresar el nombre del cliente.")
            else:
                plan_info = PLANES_INTERNET[id_plan]
                fecha_actual = datetime.date.today()
                
                if fecha_actual.month == 12:
                    fecha_corte = datetime.date(fecha_actual.year + 1, 1, dia_corte)
                else:
                    fecha_corte = datetime.date(fecha_actual.year, fecha_actual.month + 1, dia_corte)
                
                nuevo = {
                    "contrato": num_contrato,
                    "nombre": nombre_cliente,
                    "plan": plan_info["megas"],
                    "mensualidad": plan_info["precio"],
                    "fecha_corte": fecha_corte.strftime("%Y-%m-%d"),
                    "estado": "Activo"
                }
                lista_clientes.append(nuevo)
                with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
                    json.dump(lista_clientes, f, indent=4, ensure_ascii=False)
                st.success(f"✅ ¡Cliente '{nombre_cliente}' registrado con éxito!")
                st.rerun()

# --- PESTAÑA 3: COBRANZA RÁPIDA ---
with pestana3:
    st.subheader("Registrar Pago Mensual")
    contrato_a_pagar = st.number_input("Ingresa el Contrato a Renovar:", min_value=1, step=1, key="cobro")
    
    if st.button("💳 Registrar Pago y Reactivar Señal", type="primary"):
        encontrado = False
        for cliente in lista_clientes:
            if cliente["contrato"] == contrato_a_pagar:
                f_actual_corte = datetime.datetime.strptime(cliente["fecha_corte"], "%Y-%m-%d").date()
                
                if f_actual_corte.month == 12:
                    nueva_f = datetime.date(f_actual_corte.year + 1, 1, f_actual_corte.day)
                else:
                    nueva_f = datetime.date(f_actual_corte.year, f_actual_corte.month + 1, f_actual_corte.day)
                
                cliente["fecha_corte"] = nueva_f.strftime("%Y-%m-%d")
                cliente["estado"] = "Activo"
                encontrado = True
                break
        
        if encontrado:
            with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
                json.dump(lista_clientes, f, indent=4, ensure_ascii=False)
            st.success(f"💳 ¡Pago aplicado! Contrato #{contrato_a_pagar} reactivado hasta el {nueva_f.strftime('%d/%m/%Y')}")
            st.rerun()
        else:
            st.error("❌ Error: No se encontró ningún contrato con ese número.")