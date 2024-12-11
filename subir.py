import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import pyodbc

# Función para cargar el archivo Excel
def cargar_archivo():
    archivo = filedialog.askopenfilename(filetypes=[("Archivos Excel", "*.xlsx;*.xls")])
    if archivo:
        entry_ruta.delete(0, tk.END)
        entry_ruta.insert(0, archivo)

# Función para insertar los datos en la base de datos
def insertar_datos():
    # Conectar a la base de datos SQL Server
    try:
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                              'SERVER=localhost\\SQLEXPRESS;'
                              'DATABASE=DB_MASCOTAS;'
                              'Trusted_Connection=yes;')  
        cursor = conn.cursor()
    except Exception as e:
        messagebox.showerror("Error de Conexión", f"No se pudo conectar a la base de datos: {e}")
        return
    
    # Leer el archivo Excel
    archivo = entry_ruta.get()
    try:
        df = pd.read_excel(archivo, header=0)  # Asegúrate de leer desde la primera fila (encabezados)
        
        # Imprimir los encabezados para depurar
        print("Encabezados del archivo:", df.columns.tolist())
        
        # Verificar que las columnas estén presentes
        if 'Iosfa' not in df.columns or 'Nombre' not in df.columns or 'Edad' not in df.columns or 'Descripcion' not in df.columns or 'Amo' not in df.columns:
            messagebox.showerror("Error", "El archivo no tiene las columnas correctas. Las columnas esperadas son: 'iosfa', 'Nombre', 'Edad', 'Descripcion', 'Amo'.")
            return
        
        # Insertar los datos en la base de datos
        for _, row in df.iterrows():
            # Insertar datos en la tabla Mascotas
            cursor.execute("INSERT INTO Mascotas (iosfa, nombre, edad, descripcion) VALUES (?, ?, ?, ?)",
                           row['Iosfa'], row['Nombre'], row['Edad'], row['Descripcion'])
            
            # Confirmar la inserción en Mascotas
            conn.commit()

            # Insertar datos en la tabla Amos
            cursor.execute("INSERT INTO Amos (iosfa, amo) VALUES (?, ?)", row['Iosfa'], row['Amo'])
        
        # Confirmar los cambios finales
        conn.commit()
        messagebox.showinfo("Éxito", "Datos insertados correctamente.")
        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", f"Hubo un problema al procesar el archivo: {e}")

# Crear la interfaz de usuario
ventana = tk.Tk()
ventana.title("Importar Datos de Excel a Base de Datos")

# Elementos de la interfaz
frame = tk.Frame(ventana)
frame.pack(padx=20, pady=20)

label_ruta = tk.Label(frame, text="Seleccionar archivo Excel:")
label_ruta.grid(row=0, column=0, padx=10, pady=10)

entry_ruta = tk.Entry(frame, width=50)
entry_ruta.grid(row=0, column=1, padx=10, pady=10)

boton_buscar = tk.Button(frame, text="Buscar", command=cargar_archivo)
boton_buscar.grid(row=0, column=2, padx=10, pady=10)

boton_insertar = tk.Button(ventana, text="Insertar Datos", command=insertar_datos)
boton_insertar.pack(pady=10)

ventana.mainloop()
