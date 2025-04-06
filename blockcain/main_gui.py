# main_gui.py
import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
import time
from blockchain import Blockchain

# Inicializamos la blockchain
blockchain = Blockchain()

# Ventana principal
root = tk.Tk()
root.title("Prototipo de Blockchain - Interfaz Gráfica")
root.geometry("900x700")

# === FUNCIONES ===

def registrar_usuario():
    nombre = simpledialog.askstring("Registro", "Nombre del nuevo usuario:")
    if nombre:
        usuario = blockchain.registrar_usuario(nombre)
        messagebox.showinfo("Usuario registrado", f"Clave pública: {usuario.clave_publica[:8]}...")
        actualizar_log(f"👤 Usuario '{nombre}' registrado.")

def agregar_transaccion():
    emisor = entry_emisor.get()
    receptor = entry_receptor.get()
    cantidad = entry_cantidad.get()

    if not (emisor and receptor and cantidad):
        messagebox.showwarning("Campos vacíos", "Completa todos los campos.")
        return

    try:
        cantidad = float(cantidad)
    except ValueError:
        messagebox.showerror("Error", "Cantidad no válida.")
        return

    exito = blockchain.agregar_transaccion(emisor, receptor, cantidad)
    if exito:
        actualizar_log(f"💸 Transacción: {emisor} → {receptor} ({cantidad})")
        entry_emisor.delete(0, tk.END)
        entry_receptor.delete(0, tk.END)
        entry_cantidad.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Usuarios no registrados. Regístralos primero.")

def minar_transacciones():
    actualizar_log("⛏️ Minando bloque...")
    resultado = blockchain.minar_transacciones_pendientes()
    if resultado:
        messagebox.showinfo("Bloque minado", "Transacciones minadas y bloque añadido a la cadena.")
        actualizar_log("✅ Bloque minado con éxito.")
        mostrar_blockchain()
    else:
        messagebox.showwarning("Nada que minar", "No hay transacciones pendientes.")


def mostrar_blockchain():
    text_area.delete(1.0, tk.END)
    if not blockchain.cadena:
        text_area.insert(tk.END, "La blockchain está vacía.")
        return

    for bloque in blockchain.cadena:
        text_area.insert(tk.END, f"\n📦 Bloque #{bloque.indice}\n")
        text_area.insert(tk.END, f"  ⏱️ Tiempo: {time.ctime(bloque.timestamp)}\n")
        text_area.insert(tk.END, f"  🔗 Hash anterior: {bloque.hash_anterior[:8]}...\n")
        text_area.insert(tk.END, f"  🔒 Hash: {bloque.hash[:8]}...\n")
        text_area.insert(tk.END, f"  🔁 Nonce: {bloque.nonce}\n")
        text_area.insert(tk.END, f"  📄 Transacciones:\n")
        for t in bloque.transacciones:
            text_area.insert(tk.END, f"    - {t}\n")
        text_area.insert(tk.END, bloque.merkle.mostrar_arbol())
        text_area.insert(tk.END, "=" * 60 + "\n")
    text_area.insert(tk.END, f"\n🔗 Total de bloques: {len(blockchain.cadena)}\n")

def verificar_cadena():
    if blockchain.es_valida():
        messagebox.showinfo("Cadena válida", "✅ La cadena de bloques es válida.")
        actualizar_log("✅ Verificación correcta de la cadena.")
    else:
        messagebox.showerror("Cadena inválida", "❌ La cadena ha sido alterada.")

# === WIDGETS ===
frame_form = tk.Frame(root)
frame_form.pack(pady=10)

entry_emisor = tk.Entry(frame_form, width=20)
entry_emisor.grid(row=0, column=1, padx=5)
tk.Label(frame_form, text="Emisor:").grid(row=0, column=0)

entry_receptor = tk.Entry(frame_form, width=20)
entry_receptor.grid(row=0, column=3, padx=5)
tk.Label(frame_form, text="Receptor:").grid(row=0, column=2)

entry_cantidad = tk.Entry(frame_form, width=10)
entry_cantidad.grid(row=0, column=5, padx=5)
tk.Label(frame_form, text="Cantidad:").grid(row=0, column=4)

btn_transaccion = tk.Button(root, text="Agregar transacción", command=agregar_transaccion)
btn_transaccion.pack(pady=5)

btn_minar = tk.Button(root, text="Minar transacciones", command=minar_transacciones)
btn_minar.pack(pady=5)

btn_mostrar = tk.Button(root, text="Mostrar Blockchain", command=mostrar_blockchain)
btn_mostrar.pack(pady=5)

btn_verificar = tk.Button(root, text="Verificar cadena", command=verificar_cadena)
btn_verificar.pack(pady=5)

btn_usuario = tk.Button(root, text="Registrar nuevo usuario", command=registrar_usuario)
btn_usuario.pack(pady=5)

text_area = scrolledtext.ScrolledText(root, width=110, height=25)
text_area.pack(pady=10)

def actualizar_log(mensaje):
    text_area.insert(tk.END, f"{mensaje}\n")
    text_area.see(tk.END)

# Mostrar blockchain inicial
mostrar_blockchain()

# Iniciar aplicación
tk.Label(root, text="🧱 Blockchain inicializada").pack()
root.mainloop()