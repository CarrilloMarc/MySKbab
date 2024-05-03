import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog

def create_database():
    conn = sqlite3.connect('kebab_shop.db')
    c = conn.cursor()

    # Crear tabla de Ingredientes
    c.execute('''
    CREATE TABLE IF NOT EXISTS Ingredientes (
        id_ingrediente INTEGER PRIMARY KEY,
        nombre_ingrediente TEXT NOT NULL,
        tipo TEXT NOT NULL,
        stock INTEGER DEFAULT 0
    )''')

    # Crear tabla de Compras
    c.execute('''
    CREATE TABLE IF NOT EXISTS Compra (
        id_compra INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_compra TEXT NOT NULL,
        proveedor TEXT NOT NULL,
        monto REAL NOT NULL,
        cantidad INTEGER NOT NULL,
        id_ingrediente INTEGER,
        FOREIGN KEY (id_ingrediente) REFERENCES Ingredientes (id_ingrediente)
    )''')

    # Crear tabla de Kebabs
    c.execute('''
    CREATE TABLE IF NOT EXISTS Kebab (
        id_kebab INTEGER PRIMARY KEY,
        nombre_kebab TEXT NOT NULL,
        precio REAL NOT NULL,
        descripcion TEXT
    )''')

    # Crear tabla de Ventas
    c.execute('''
    CREATE TABLE IF NOT EXISTS Venta (
        id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
        id_kebab INTEGER,
        fecha_venta TEXT NOT NULL,
        cantidad INTEGER NOT NULL,
        monto_total REAL NOT NULL,
        FOREIGN KEY (id_kebab) REFERENCES Kebab (id_kebab)
    )''')

    conn.commit()
    conn.close()

create_database()

def check_credentials(username, password):
    if username == "amigo" and password == "kebab":
        return "admin"
    elif username == "vendedor" and password == "dekebabs":
        return "vendedor"
    else:
        return None

def main_menu(root, user_type):
    root.title("Menú Principal")
    
    # Definir el fondo de la ventana principal
    root.configure(bg="#f0f0f0")

    # Crear un marco para contener los botones
    frame = tk.Frame(root, bg="#f0f0f0")
    frame.pack(padx=20, pady=20)

    # Función para crear botones con opciones
    def create_button(text, command, bg_color):
        button = tk.Button(frame, text=text, command=command, width=25, height=2, bg=bg_color)
        button.pack(side=tk.TOP if bg_color == "#6fa4e7" else tk.BOTTOM, padx=10, pady=5)
        
    # Crear botones según el tipo de usuario
    if user_type == "admin":
        create_button("Realizar compra", realizar_compra, "#ff6666")  # Rojo
        create_button("Editar Kebabs", editar_kebabs, "#ff6666")  # Rojo
        create_button("Realizar venta", realizar_venta, "#6fa4e7")  # Azul
        create_button("Consultar stock de ingredientes", consultar_stock, "#6fa4e7")  # Azul
    else:
        create_button("Realizar venta", realizar_venta, "#6fa4e7")  # Azul
        create_button("Consultar ingredientes", consultar_stock, "#6fa4e7")  # Azul

def login(root):
    login_window = tk.Toplevel()
    login_window.title("Inicio de Sesión")

    label_username = tk.Label(login_window, text="Usuario:")
    label_username.grid(row=0, column=0)
    entry_username = tk.Entry(login_window)
    entry_username.grid(row=0, column=1)

    label_password = tk.Label(login_window, text="Contraseña:")
    label_password.grid(row=1, column=0)
    entry_password = tk.Entry(login_window, show="*")
    entry_password.grid(row=1, column=1)

    def submit():
        username = entry_username.get()
        password = entry_password.get()
        user_type = check_credentials(username, password)
        if user_type:
            main_menu(root, user_type)
            login_window.destroy()
        else:
            messagebox.showerror("Error", "Credenciales incorrectas. Por favor, inténtelo de nuevo.")
            entry_username.delete(0, tk.END)
            entry_password.delete(0, tk.END)

    button_submit = tk.Button(login_window, text="Iniciar Sesión", command=submit)
    button_submit.grid(row=2, columnspan=2)

def realizar_compra():
    conn = sqlite3.connect('kebab_shop.db')
    c = conn.cursor()

    # Obtener lista de ingredientes y su stock actual
    ingredientes = [
        ("Ternera", 50),
        ("Pollo", 50),
        ("Lechuga", None),
        ("Cebolla", None),
        ("Queso", None),
        ("Tomate", None),
        ("Masa", None),
        ("Salsa Blanca", None),
        ("Salsa Picante", None)
    ]

    # Crear ventana para seleccionar ingredientes y cantidades
    compra_window = tk.Toplevel()
    compra_window.title("Realizar Compra")

    # Función para agregar ingredientes al carrito
    def agregar_al_carrito(ingrediente, cantidad_str):
        if cantidad_str.strip() == '':
            # Aquí podrías mostrar un mensaje de error al usuario indicando que el campo está vacío
            return
        try:
            cantidad = int(cantidad_str)
        except ValueError:
            # Aquí podrías mostrar un mensaje de error al usuario indicando que el valor ingresado no es válido
            return
        if ingrediente in carrito:
            carrito[ingrediente] += cantidad
        else:
            carrito[ingrediente] = cantidad
        actualizar_carrito()

    # Función para actualizar el carrito de compras
    def actualizar_carrito():
        listbox_carrito.delete(0, tk.END)
        for ingrediente, cantidad in carrito.items():
            listbox_carrito.insert(tk.END, f"{ingrediente}: {cantidad}")

    # Función para confirmar la compra
    def confirmar_compra():
        total = sum(carrito.values())
        confirmar = messagebox.askyesno("Confirmar compra", f"Total de productos seleccionados: {total}\n¿Desea confirmar la compra?")
        if confirmar:
            conn = sqlite3.connect('kebab_shop.db')
            c = conn.cursor()
            # Actualizar el stock en la base de datos
            for ingrediente, cantidad in carrito.items():
                c.execute("UPDATE Ingredientes SET stock = stock - ? WHERE nombre_ingrediente = ?", (cantidad, ingrediente))
            conn.commit()
            conn.close()
            messagebox.showinfo("Compra realizada", "Compra realizada con éxito.")
            compra_window.destroy()
            # Después de confirmar la compra, actualizar la información de stock
            consultar_stock()  # Llamada a la función que muestra el stock actualizado

    # Listbox para mostrar ingredientes disponibles y botones para agregar
    for ingrediente, limite in ingredientes:
        frame = tk.Frame(compra_window)
        frame.pack(padx=10, pady=5, fill="x")

        label_nombre = tk.Label(frame, text=ingrediente)
        label_nombre.pack(side="left", padx=5)

        stock = c.execute("SELECT stock FROM Ingredientes WHERE nombre_ingrediente = ?", (ingrediente,)).fetchone()
        stock = stock[0] if stock is not None else 0  # Si no se encuentra, el stock será 0
        label_stock = tk.Label(frame, text=f"Stock: {stock}")
        label_stock.pack(side="left", padx=5)

        if limite is None or ingrediente in ["Ternera", "Pollo"]:
            entry_cantidad = tk.Entry(frame, width=5)
            entry_cantidad.pack(side="left", padx=5)
            button_set = tk.Button(frame, text="Añadir", command=lambda ingrediente=ingrediente, entry=entry_cantidad: agregar_al_carrito(ingrediente, entry.get().strip()))
            button_set.pack(side="left", padx=5)
        else:
            button_add = tk.Button(frame, text="+", command=lambda ingrediente=ingrediente: agregar_al_carrito(ingrediente, 1 if limite is None else limite))
            button_add.pack(side="left", padx=5)

    # Listbox para mostrar el carrito de compras
    listbox_carrito = tk.Listbox(compra_window)
    listbox_carrito.pack(padx=10, pady=5)

    # Botón para confirmar la compra
    button_confirmar = tk.Button(compra_window, text="Confirmar compra", command=confirmar_compra)
    button_confirmar.pack(padx=10, pady=5)

    # Diccionario para mantener el carrito de compras
    carrito = {}

    conn.close()

    # Función para agregar ingredientes al carrito
    # Función para agregar ingredientes al carrito
    def agregar_al_carrito(ingrediente, cantidad_str):
        if cantidad_str.strip() == '':
            # Aquí podrías mostrar un mensaje de error al usuario indicando que el campo está vacío
            return
        try:
            cantidad = int(cantidad_str)
        except ValueError:
            # Aquí podrías mostrar un mensaje de error al usuario indicando que el valor ingresado no es válido
            return
        if ingrediente in carrito:
            carrito[ingrediente] += cantidad
        else:
            carrito[ingrediente] = cantidad
        actualizar_carrito()


    # Función para actualizar el carrito de compras
    def actualizar_carrito():
        listbox_carrito.delete(0, tk.END)
        for ingrediente, cantidad in carrito.items():
            listbox_carrito.insert(tk.END, f"{ingrediente}: {cantidad}")

    # Función para confirmar la compra
# Modifica la función confirmar_compra para aceptar un cursor como parámetro
    def confirmar_compra():
        total = sum(carrito.values())
        confirmar = messagebox.askyesno("Confirmar compra", f"Total de productos seleccionados: {total}\n¿Desea confirmar la compra?")
        if confirmar:
            conn = sqlite3.connect('kebab_shop.db')
            c = conn.cursor()
            # Actualizar el stock en la base de datos
            for ingrediente, cantidad in carrito.items():
                c.execute("UPDATE Ingredientes SET stock = stock - ? WHERE nombre_ingrediente = ?", (cantidad, ingrediente))
            conn.commit()
            conn.close()
            messagebox.showinfo("Compra realizada", "Compra realizada con éxito.")
            compra_window.destroy()
            # Después de confirmar la compra, actualizar la información de stock
            consultar_stock()  # Llamada a la función que muestra el stock actualizado

    def agregar_al_carrito(ingrediente, cantidad_str):
        if cantidad_str.strip() == '':
            # Aquí podrías mostrar un mensaje de error al usuario indicando que el campo está vacío
            return
        try:
            cantidad = int(cantidad_str)
        except ValueError:
            # Aquí podrías mostrar un mensaje de error al usuario indicando que el valor ingresado no es válido
            return
        if ingrediente in carrito:
            carrito[ingrediente] += cantidad
        else:
            carrito[ingrediente] = cantidad
        actualizar_carrito()

    def realizar_compra():
        conn = sqlite3.connect('kebab_shop.db')
        c = conn.cursor()

    # Obtener lista de ingredientes y su stock actual
    ingredientes = [
        ("Ternera", 50),
        ("Pollo", 50),
        ("Lechuga", None),
        ("Cebolla", None),
        ("Queso", None),
        ("Tomate", None),
        ("Masa", None),
        ("Salsa Blanca", None),
        ("Salsa Picante", None)
    ]

    # Crear ventana para seleccionar ingredientes y cantidades
    compra_window = tk.Toplevel()
    compra_window.title("Realizar Compra")

    # Función para actualizar el carrito de compras
    def actualizar_carrito():
        listbox_carrito.delete(0, tk.END)
        for ingrediente, cantidad in carrito.items():
            listbox_carrito.insert(tk.END, f"{ingrediente}: {cantidad}")

    # Función para confirmar la compra

def realizar_venta():
    conn = sqlite3.connect('kebab_shop.db')
    c = conn.cursor()

    # Mostrar kebabs disponibles
    c.execute("SELECT id_kebab, nombre_kebab, precio FROM Kebab")
    kebabs = c.fetchall()
    for kebab in kebabs:
        print(f"ID: {kebab[0]}, Kebab: {kebab[1]}, Precio: {kebab[2]}")

    try:
        id_kebab = simpledialog.askinteger("Realizar venta", "Ingrese el ID del kebab que desea vender:")
        cantidad = simpledialog.askinteger("Realizar venta", "Ingrese la cantidad de kebabs:")
        fecha_venta = simpledialog.askstring("Realizar venta", "Ingrese la fecha de venta (YYYY-MM-DD):")

        # Verificar stock de ingredientes antes de confirmar venta
        if verificar_stock(c, id_kebab, cantidad):
            # Registrar venta
            precio = c.execute("SELECT precio FROM Kebab WHERE id_kebab = ?", (id_kebab,)).fetchone()[0]
            monto_total = precio * cantidad
            c.execute("INSERT INTO Venta (id_kebab, fecha_venta, cantidad, monto_total) VALUES (?, ?, ?, ?)",
                      (id_kebab, fecha_venta, cantidad, monto_total))
            conn.commit()
            messagebox.showinfo("Venta realizada", "Venta realizada con éxito.")
        else:
            messagebox.showerror("Error", "Stock insuficiente para realizar la venta.")
    except (ValueError, TypeError):
        messagebox.showerror("Error", "Debe ingresar un número válido.")
    except sqlite3.Error as e:
        messagebox.showerror("Error de base de datos", f"Error de la base de datos: {e}")

    conn.close()

def verificar_stock(cursor, id_kebab, cantidad):
    # Obtener los ingredientes necesarios para el kebab seleccionado
    cursor.execute("""
    SELECT ing.id_ingrediente, ing.stock
    FROM KebabIngredientes AS ki
    JOIN Ingredientes AS ing ON ki.id_ingrediente = ing.id_ingrediente
    WHERE ki.id_kebab = ?
    """, (id_kebab,))

    ingredientes_necesarios = cursor.fetchall()

    if not ingredientes_necesarios:
        messagebox.showerror("Error", "No hay ingredientes asociados a este kebab o el kebab no existe.")
        return False

    # Verificar si hay suficiente stock para cada ingrediente
    for id_ingrediente, stock_actual in ingredientes_necesarios:
        if stock_actual < cantidad:
            messagebox.showerror("Error", f"No hay suficiente stock para el ingrediente ID {id_ingrediente}. Necesario: {cantidad}, Disponible: {stock_actual}")
            return False

    # Si todo está en orden, procedemos a actualizar el stock
    for id_ingrediente, _ in ingredientes_necesarios:
        nuevo_stock = stock_actual - cantidad
        cursor.execute("UPDATE Ingredientes SET stock = ? WHERE id_ingrediente = ?", (nuevo_stock, id_ingrediente))

    messagebox.showinfo("Operación exitosa", "Stock actualizado correctamente.")
    return True

def editar_kebabs():
    conn = sqlite3.connect('kebab_shop.db')
    c = conn.cursor()

    # Mostrar kebabs actuales
    c.execute("SELECT id_kebab, nombre_kebab, descripcion FROM Kebab")
    kebabs = c.fetchall()
    for kebab in kebabs:
        print(f"ID: {kebab[0]}, Nombre: {kebab[1]}, Descripción: {kebab[2]}")

    try:
        id_kebab = simpledialog.askinteger("Editar Kebabs", "Ingrese el ID del kebab que desea editar:")
        nuevo_nombre = simpledialog.askstring("Editar Kebabs", "Ingrese el nuevo nombre del kebab:")
        nueva_descripcion = simpledialog.askstring("Editar Kebabs", "Ingrese la nueva descripción del kebab:")

        # Actualizar la información del kebab
        c.execute("UPDATE Kebab SET nombre_kebab = ?, descripcion = ? WHERE id_kebab = ?",
                  (nuevo_nombre, nueva_descripcion, id_kebab))
        conn.commit()
        messagebox.showinfo("Operación exitosa", "Kebab actualizado correctamente.")
    except (ValueError, TypeError):
        messagebox.showerror("Error", "Debe ingresar valores válidos.")
    except sqlite3.Error as e:
        messagebox.showerror("Error de base de datos", f"Error de la base de datos: {e}")

    conn.close()

def consultar_stock():
    conn = sqlite3.connect('kebab_shop.db')
    c = conn.cursor()

    # Ejecutar consulta SQL para obtener el stock actualizado
    c.execute("SELECT nombre_ingrediente, stock FROM Ingredientes")
    rows = c.fetchall()
    stock_info = ""
    for row in rows:
        stock_info += f"Ingrediente: {row[0]}, Stock: {row[1]}\n"
    messagebox.showinfo("Stock de Ingredientes", stock_info)

    conn.close()

def main():
    root = tk.Tk()
    login(root)
    root.mainloop()

if __name__ == "__main__":
    main()
