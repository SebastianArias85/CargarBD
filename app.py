import tkinter as tk
from tkinter import messagebox
import pyodbc
import pandas as pd
from tkinter import ttk

# Función para conectarse a la base de datos SQL Server
def obtener_conexion():
    try:
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                              'SERVER=localhost\\SQLEXPRESS;'
                              'DATABASE=DB_MASCOTAS;'
                              'Trusted_Connection=yes;')
        return conn
    except Exception as e:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos: {e}")
        return None

# Función para obtener los nombres de las mascotas desde la base de datos
def obtener_nombres():
    conn = obtener_conexion()
    if not conn:
        return []
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Nombre FROM Mascotas")
        nombres = cursor.fetchall()
        conn.close()
        return [nombre[0] for nombre in nombres]
    except Exception as e:
        messagebox.showerror("Error", f"Error al obtener nombres: {e}")
        conn.close()
        return []

# Función para obtener los detalles de la mascota seleccionada, incluyendo el nombre del amo
def obtener_detalles(nombre):
    conn = obtener_conexion()
    if not conn:
        return None
    cursor = conn.cursor()
    try:
        # Obtener los detalles de la mascota y el nombre del Amo desde la tabla Amos
        cursor.execute("""
            SELECT M.Iosfa, M.Nombre, M.Edad, M.Descripcion, A.Amo
            FROM Mascotas M
            JOIN Amos A ON M.Iosfa = A.Iosfa
            WHERE M.Nombre = ?
        """, nombre)
        detalle = cursor.fetchone()
        conn.close()
        return detalle
    except Exception as e:
        messagebox.showerror("Error", f"Error al obtener detalles: {e}")
        conn.close()
        return None

# Función para eliminar una mascota
def eliminar_mascota():
    nombre = combo_nombres.get()
    if not nombre or nombre == "Seleccione un nombre":  # Verificar si no se seleccionó un nombre
        messagebox.showwarning("Selección vacía", "Por favor, seleccione un registro para eliminar.")
        return
    
    # Preguntar si realmente desea eliminar el registro
    respuesta = messagebox.askyesno("Confirmar eliminación", f"¿Estás seguro de que quieres eliminar la mascota: {nombre}?")
    
    if respuesta:
        conn = obtener_conexion()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Mascotas WHERE Nombre = ?", nombre)
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", f"Se ha eliminado la mascota: {nombre}")
            # Limpiar el combobox y actualizar la lista de nombres
            combo_nombres.set("Seleccione un nombre")
            combo_nombres['values'] = obtener_nombres()
        except Exception as e:
            messagebox.showerror("Error al eliminar", f"Hubo un problema al eliminar el registro: {e}")
            conn.close()
    else:
        messagebox.showinfo("Cancelado", "La eliminación ha sido cancelada.")

# Función para exportar los datos a un archivo Excel
def exportar_a_excel(nombre):
    detalle = obtener_detalles(nombre)
    if detalle:
        try:
            # Crear un DataFrame con los datos de la mascota
            df = pd.DataFrame([list(detalle)], columns=['Iosfa', 'Nombre', 'Edad', 'Descripcion', 'Amo'])
            # Exportar a Excel
            df.to_excel(f'{nombre}_detalle_mascota.xlsx', index=False)
            messagebox.showinfo("Éxito", f"Los detalles de {nombre} han sido exportados a Excel.")
        except Exception as e:
            messagebox.showerror("Error al exportar", f"Hubo un problema al exportar los datos: {e}")
    else:
        messagebox.showerror("Error", "No se encontraron detalles para la mascota seleccionada.")

# Función para ver los detalles de la mascota
def mostrar_detalles():
    nombre = combo_nombres.get()
    if nombre and nombre != "Seleccione un nombre":
        detalle = obtener_detalles(nombre)
        if detalle:
            # Crear una nueva ventana para mostrar los detalles
            ventana_detalle = tk.Toplevel(ventana_principal)
            ventana_detalle.title(f"Detalles de {nombre}")

            # Crear el widget Notebook (solapas)
            notebook = ttk.Notebook(ventana_detalle)
            notebook.pack(padx=10, pady=10, expand=True)

            # Crear las pestañas para cada tipo de información
            tab_detalles = ttk.Frame(notebook)
            tab_amo = ttk.Frame(notebook)

            # Añadir las pestañas al Notebook
            notebook.add(tab_detalles, text="Detalles de la Mascota")
            notebook.add(tab_amo, text="Detalles del Amo")

            ########################################################################################################
            ########################################################################################################

            # Datos de la mascota en la primera pestaña
            tk.Label(tab_detalles, text="DATOS GENERALES:").pack(pady=10)
            tk.Label(tab_detalles, text=f"Nombre: {detalle[1]}").pack(pady=5)
            tk.Label(tab_detalles, text=f"Edad: {detalle[2]}").pack(pady=5)
            tk.Label(tab_detalles, text=f"Descripción: {detalle[3]}").pack(pady=5)
            tk.Label(tab_detalles, text=f"Iosfa: {detalle[0]}").pack(pady=5)

            ########################################################################################################
            ########################################################################################################

            # Datos del amo en la segunda pestaña
            tk.Label(tab_amo, text="EL AMO ES:").pack(pady=10)
            tk.Label(tab_amo, text=f"Amo: {detalle[4]}").pack(pady=5)

            ########################################################################################################
            ########################################################################################################

            # Botón para exportar los detalles a Excel
            btn_exportar = tk.Button(ventana_detalle, text="Exportar a Excel", 
                                     command=lambda: exportar_a_excel(nombre))
            btn_exportar.pack(pady=10)

        else:
            messagebox.showerror("Error", "No se encontraron detalles para la mascota seleccionada.")
    else:
        messagebox.showwarning("Selección vacía", "Por favor, seleccione un nombre de la lista.")

# Función para agregar un nuevo registro de mascota
def agregar_mascota():
    def guardar_mascota():
        iosfa = entry_iosfa.get()
        nombre = entry_nombre.get()
        edad = entry_edad.get()
        descripcion = entry_descripcion.get()

        if not iosfa or not nombre or not edad or not descripcion:
            messagebox.showwarning("Campos vacíos", "Por favor, complete todos los campos.")
            return

        conn = obtener_conexion()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            # Verificar si el iosfa ya existe
            cursor.execute("SELECT COUNT(*) FROM Mascotas WHERE Iosfa = ?", iosfa)
            if cursor.fetchone()[0] > 0:
                messagebox.showwarning("Error", "El iosfa ya está en uso. Por favor, ingrese otro.")
                conn.close()
                return
            
            # Insertar la mascota en la tabla Mascotas
            cursor.execute("INSERT INTO Mascotas (Iosfa, Nombre, Edad, Descripcion) VALUES (?, ?, ?, ?)", iosfa, nombre, edad, descripcion)
            conn.commit()
            
            # Ahora, ingresar el nombre del Amo en la tabla Amos
            amo = entry_amo.get()
            if amo:
                cursor.execute("INSERT INTO Amos (Iosfa, Amo) VALUES (?, ?)", iosfa, amo)
                conn.commit()

            conn.close()
            messagebox.showinfo("Éxito", f"Se ha agregado la mascota: {nombre}")
            ventana_agregar.destroy()
            # Actualizar la lista de nombres en la ventana principal
            combo_nombres['values'] = obtener_nombres()
        except Exception as e:
            messagebox.showerror("Error al agregar", f"Hubo un problema al agregar la mascota: {e}")
            conn.close()

    # Crear la ventana para agregar una nueva mascota
    ventana_agregar = tk.Toplevel(ventana_principal)
    ventana_agregar.title("Agregar nueva mascota")

    # Campo para ingresar el iosfa
    tk.Label(ventana_agregar, text="Iosfa (ID de la mascota):").pack(pady=5)
    entry_iosfa = tk.Entry(ventana_agregar)
    entry_iosfa.pack(pady=5)

    # Campo para ingresar el nombre del amo
    tk.Label(ventana_agregar, text="Amo (Nombre del Amo):").pack(pady=5)
    entry_amo = tk.Entry(ventana_agregar)
    entry_amo.pack(pady=5)

    # Campos para los demás detalles
    tk.Label(ventana_agregar, text="Nombre:").pack(pady=5)
    entry_nombre = tk.Entry(ventana_agregar)
    entry_nombre.pack(pady=5)

    tk.Label(ventana_agregar, text="Edad:").pack(pady=5)
    entry_edad = tk.Entry(ventana_agregar)
    entry_edad.pack(pady=5)

    tk.Label(ventana_agregar, text="Descripción:").pack(pady=5)
    entry_descripcion = tk.Entry(ventana_agregar)
    entry_descripcion.pack(pady=5)

    # Botón para guardar la nueva mascota
    btn_guardar = tk.Button(ventana_agregar, text="Guardar", command=guardar_mascota)
    btn_guardar.pack(pady=10)

# Función para modificar los detalles de una mascota seleccionada
def modificar_mascota():
    nombre = combo_nombres.get()
    if nombre and nombre != "Seleccione un nombre":
        detalle = obtener_detalles(nombre)
        if detalle:
            # Crear la ventana de modificación
            ventana_modificar = tk.Toplevel(ventana_principal)
            ventana_modificar.title(f"Modificar {nombre}")

            # Entradas para los detalles de la mascota
            tk.Label(ventana_modificar, text="Nombre:").pack(pady=5)
            entry_nombre = tk.Entry(ventana_modificar)
            entry_nombre.insert(0, detalle[1])  # Mostrar el nombre actual
            entry_nombre.pack(pady=5)

            tk.Label(ventana_modificar, text="Edad:").pack(pady=5)
            entry_edad = tk.Entry(ventana_modificar)
            entry_edad.insert(0, detalle[2])  # Mostrar la edad actual
            entry_edad.pack(pady=5)

            tk.Label(ventana_modificar, text="Descripción:").pack(pady=5)
            entry_descripcion = tk.Entry(ventana_modificar)
            entry_descripcion.insert(0, detalle[3])  # Mostrar la descripción actual
            entry_descripcion.pack(pady=5)

            tk.Label(ventana_modificar, text="Amo:").pack(pady=5)
            entry_amo = tk.Entry(ventana_modificar)
            entry_amo.insert(0, detalle[4])  # Mostrar el nombre del amo actual
            entry_amo.pack(pady=5)

            def guardar_cambios():
                nuevo_nombre = entry_nombre.get()
                nueva_edad = entry_edad.get()
                nueva_descripcion = entry_descripcion.get()
                nuevo_amo = entry_amo.get()

                if not nuevo_nombre or not nueva_edad or not nueva_descripcion or not nuevo_amo:
                    messagebox.showwarning("Campos vacíos", "Por favor, complete todos los campos.")
                    return

                conn = obtener_conexion()
                if not conn:
                    return
                cursor = conn.cursor()
                try:
                    # Actualizar los datos en la tabla Mascotas
                    cursor.execute("""UPDATE Mascotas 
                                       SET Nombre = ?, Edad = ?, Descripcion = ? 
                                       WHERE Nombre = ?""", 
                                   nuevo_nombre, nueva_edad, nueva_descripcion, nombre)
                    
                    # Actualizar el nombre del amo en la tabla Amos
                    cursor.execute("UPDATE Amos SET Amo = ? WHERE Iosfa = (SELECT Iosfa FROM Mascotas WHERE Nombre = ?)", 
                                   nuevo_amo, nuevo_nombre)
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Éxito", f"Los detalles de {nombre} han sido actualizados.")
                    ventana_modificar.destroy()
                    # Actualizar la lista de nombres en la ventana principal
                    combo_nombres['values'] = obtener_nombres()
                except Exception as e:
                    messagebox.showerror("Error al modificar", f"Hubo un problema al modificar los datos: {e}")
                    conn.close()

            # Botón para guardar los cambios
            btn_guardar = tk.Button(ventana_modificar, text="Guardar cambios", command=guardar_cambios)
            btn_guardar.pack(pady=10)

        else:
            messagebox.showerror("Error", "No se encontraron detalles para la mascota seleccionada.")
    else:
        messagebox.showwarning("Selección vacía", "Por favor, seleccione un nombre de la lista.")

# Crear la ventana principal
ventana_principal = tk.Tk()
ventana_principal.title("Aplicación de Mascotas")

# Combobox para seleccionar el nombre de la mascota
nombres = obtener_nombres()
if not nombres:
    messagebox.showerror("Error", "No se pudieron cargar los nombres de las mascotas.")
    ventana_principal.quit()

combo_nombres = ttk.Combobox(ventana_principal, values=nombres, state="readonly")
combo_nombres.set("Seleccione un nombre")
combo_nombres.pack(pady=20)

# Botón para mostrar los detalles
btn_mostrar = tk.Button(ventana_principal, text="Mostrar Detalles", command=mostrar_detalles)
btn_mostrar.pack(pady=10)

# Botón para agregar un nuevo registro
btn_agregar = tk.Button(ventana_principal, text="Agregar Nueva Mascota", command=agregar_mascota)
btn_agregar.pack(pady=10)

# Botón para modificar los detalles de una mascota
btn_modificar = tk.Button(ventana_principal, text="Modificar Mascota", command=modificar_mascota)
btn_modificar.pack(pady=10)

# Botón para eliminar una mascota
btn_eliminar = tk.Button(ventana_principal, text="Eliminar Mascota", command=eliminar_mascota)
btn_eliminar.pack(pady=10)

# Iniciar la interfaz gráfica
ventana_principal.mainloop()
