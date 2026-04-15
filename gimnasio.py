from datetime import datetime, timedelta

# PRECIOS (Constantes)
PRECIO_MES, PRECIO_DIA, PRECIO_TARJETA = 25.00, 3.00, 13.50

# BASES DE DATOS (Globales)
mensualidades, tarjetas_10 = {}, {}
historial_movimientos = [] 
total_tickets_dia = 0 

def iniciar_sistema():
    global total_tickets_dia, historial_movimientos
    
    print("=========================================")
    print("       SISTEMA DE GESTIÓN OLYMPUS GYM    ")
    print("=========================================")
    
    while True:
        try:
            fondo_caja = float(input("--- APERTURA DE CAJA ---\nIngrese efectivo inicial (sencillo): $"))
            break
        except ValueError:
            print("Error: Ingrese un número válido.")

    efectivo_ventas = 0.0
    gastos_totales = 0.0
    transferencias_osmany = 0.0

    while True:
        print("\n" + "="*40)
        print(f"         OLYMPUS GYM - CAJA ABIERTA")
        print("="*40)
        print("1. Registrar Pago (Mensualidad/Día/Tarjeta)")
        print("2. Registrar Gasto de Caja")
        print("3. Ver Reporte y Cierre de Turno")
        print("4. Consultar Base de Datos (Socios/Tarjetas)")
        print("5. Salir")
        
        opc = input("Seleccione opción: ")

        if opc == "1":
            print(f"\n1. Mes (${PRECIO_MES}) | 2. Tarjeta 10 (${PRECIO_TARJETA}) | 3. Día (${PRECIO_DIA})")
            p_opc = input("Producto: ")
            monto = {"1": PRECIO_MES, "2": PRECIO_TARJETA, "3": PRECIO_DIA}.get(p_opc, 0)

            if monto > 0:
                print("1. Efectivo | 2. Transferencia (Osmany)")
                m_opc = input("Método: ")
                
                hoy = datetime.now()
                if m_opc == "1":
                    efectivo_ventas += monto
                    metodo = "EFECTIVO"
                elif m_opc == "2":
                    transferencias_osmany += monto
                    metodo = "TRANSFERENCIA"
                else:
                    print("Método no válido"); continue

                detalle = "Ticket Diario"
                if p_opc == "1":
                    n = input("Nombre del socio: ").upper()
                    vencimiento = hoy + timedelta(days=30)
                    mensualidades[n] = vencimiento
                    detalle = f"Mes - {n} (Vence: {vencimiento.strftime('%d/%m/%Y')})"
                    print(f"¡Socio registrado! Vencimiento: {vencimiento.strftime('%d/%m/%Y')}")
                elif p_opc == "2":
                    n = input("Nombre para tarjeta: ").upper()
                    tarjetas_10[n] = {"fecha": hoy, "usos": 10}
                    detalle = f"Tarjeta - {n}"
                    print(f"¡Tarjeta de 10 días creada para {n}!")
                else:
                    total_tickets_dia += 1
                    detalle = "Pase Diario"

                historial_movimientos.append(f"{hoy.strftime('%H:%M')} | INGRESO: {detalle} | ${monto} ({metodo})")

        elif opc == "2":
            print("\n--- REGISTRAR GASTO ---")
            motivo = input("Concepto del gasto: ").upper()
            try:
                monto_gasto = float(input(f"Monto a retirar para '{motivo}': $"))
                if monto_gasto <= (fondo_caja + efectivo_ventas):
                    gastos_totales += monto_gasto
                    historial_movimientos.append(f"{datetime.now().strftime('%H:%M')} | GASTO: {motivo} | -${monto_gasto}")
                    print(f"Gasto de ${monto_gasto} descontado de caja.")
                else:
                    print("Error: Fondos insuficientes en efectivo.")
            except ValueError:
                print("Error: Monto no válido.")

        elif opc == "3":
            efectivo_final = fondo_caja + efectivo_ventas - gastos_totales
            print("\n" + "X"*45)
            print(f"      CORTE DE CAJA - OLYMPUS GYM")
            print(f"      FECHA: {datetime.now().strftime('%d/%m/%Y')}")
            print("X"*45)
            print(f"(+) Fondo Inicial:        ${fondo_caja:.2f}")
            print(f"(+) Ventas Efectivo:      ${efectivo_ventas:.2f}")
            print(f"(-) Gastos de Turno:      ${gastos_totales:.2f}")
            print(f"(=) EFECTIVO EN MANO:     ${efectivo_final:.2f}")
            print("-" * 45)
            print(f"TRANSFERENCIAS (OSMANY):  ${transferencias_osmany:.2f}")
            print("-" * 45)
            print(f"INGRESOS TOTALES (VENTA): ${efectivo_ventas + transferencias_osmany:.2f}")
            print("=" * 45)
            if historial_movimientos:
                print("\nÚLTIMOS MOVIMIENTOS:")
                for m in historial_movimientos[-5:]:
                    print(f" > {m}")
            print("X"*45)

        elif opc == "4":
            print("\n" + " " * 10 + "--- BASE DE DATOS ACTUAL ---")
            print("-" * 45)
            print("MENSUALIDADES ACTIVAS:")
            if not mensualidades: print(" (No hay mensualidades registradas)")
            for socio, fecha in mensualidades.items():
                print(f" • {socio.ljust(20)} | Vence: {fecha.strftime('%d/%m/%Y')}")
            
            print("\nTARJETAS DE 10 DÍAS:")
            if not tarjetas_10: print(" (No hay tarjetas registradas)")
            for socio, data in tarjetas_10.items():
                print(f" • {socio.ljust(20)} | Días restantes: {data['usos']} | Creada: {data['fecha'].strftime('%d/%m/%Y')}")
            print("-" * 45)

        elif opc == "5":
            confirmar = input("¿Cerrar sistema de Olympus Gym? (S/N): ").upper()
            if confirmar == "S":
                break

# Ejecutar el programa
if __name__ == "__main__":
    iniciar_sistema()