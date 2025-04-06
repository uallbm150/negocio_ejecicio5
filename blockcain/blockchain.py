# blockchain.py

import hashlib
import time
import json
import secrets
from typing import List, Dict

class Transaccion:
    def __init__(self, emisor: str, receptor: str, cantidad: float, firma: str = None):
        self.emisor = emisor
        self.receptor = receptor
        self.cantidad = cantidad
        self.firma = firma or "Sin firma"
        self.timestamp = time.time()

    def to_dict(self) -> Dict:
        return {
            "emisor": self.emisor,
            "receptor": self.receptor,
            "cantidad": self.cantidad,
            "firma": self.firma,
            "timestamp": self.timestamp
        }

    def __str__(self):
        return f"{self.emisor} -> {self.receptor}: {self.cantidad:.2f} (firma: {self.firma[:8]}...)"

class Usuario:
    def __init__(self, nombre: str):
        self.nombre = nombre
        self.clave_privada = secrets.token_hex(16)
        self.clave_publica = hashlib.sha256(self.clave_privada.encode()).hexdigest()

    def firmar_transaccion(self, transaccion: Transaccion) -> str:
        datos = f"{transaccion.emisor}{transaccion.receptor}{transaccion.cantidad}"
        return hashlib.sha256((datos + self.clave_privada).encode()).hexdigest()

class ArbolMerkle:
    def __init__(self, transacciones: List[Transaccion]):
        self.transacciones = transacciones
        self.hojas = [self.hash_transaccion(tx) for tx in transacciones]
        self.niveles = [self.hojas]
        self.raiz = self.construir_arbol()

    def hash_transaccion(self, transaccion: Transaccion) -> str:
        cadena = json.dumps(transaccion.to_dict(), sort_keys=True)
        return hashlib.sha256(cadena.encode()).hexdigest()

    def construir_arbol(self):
        nivel = self.hojas
        if not nivel:
            return hashlib.sha256("".encode()).hexdigest()
        while len(nivel) > 1:
            nuevo_nivel = []
            for i in range(0, len(nivel), 2):
                a = nivel[i]
                b = nivel[i + 1] if i + 1 < len(nivel) else a
                combinado = a + b
                nuevo_nivel.append(hashlib.sha256(combinado.encode()).hexdigest())
            self.niveles.append(nuevo_nivel)
            nivel = nuevo_nivel
        return nivel[0]

    def mostrar_arbol(self) -> str:
        if not self.hojas:
            return "Árbol de Merkle vacío."
        res = "Árbol de Merkle:\n"
        for i, hoja in enumerate(self.niveles[0]):
            res += f"  Hoja {i + 1}: {hoja[:8]}...\n"
        for nivel_idx, nivel in enumerate(self.niveles[1:], 1):
            res += f"  Nivel {nivel_idx}:\n"
            for j, nodo in enumerate(nivel):
                res += f"    Nodo {j + 1}: {nodo[:8]}...\n"
        res += f"  Raíz: {self.raiz[:8]}...\n"
        return res

class Bloque:
    def __init__(self, indice: int, transacciones: List[Transaccion], timestamp: float, hash_anterior: str):
        self.indice = indice
        self.transacciones = transacciones
        self.timestamp = timestamp
        self.hash_anterior = hash_anterior
        self.nonce = 0
        self.merkle = ArbolMerkle(transacciones)
        self.hash = self.calcular_hash()

    def calcular_hash(self):
        contenido = f"{self.indice}{self.timestamp}{self.hash_anterior}{self.nonce}{self.merkle.raiz}"
        return hashlib.sha256(contenido.encode()).hexdigest()

    def minar(self, dificultad: int):
        objetivo = "0" * dificultad
        while not self.hash.startswith(objetivo):
            self.nonce += 1
            self.hash = self.calcular_hash()

class Blockchain:
    def __init__(self):
        self.cadena: List[Bloque] = [self.crear_bloque_genesis()]
        self.dificultad = 4
        self.transacciones_pendientes: List[Transaccion] = []
        self.usuarios: Dict[str, Usuario] = {}

    def crear_bloque_genesis(self):
        trans = Transaccion("Sistema", "Génesis", 0.0, "Bloque inicial")
        return Bloque(0, [trans], time.time(), "0")

    def registrar_usuario(self, nombre: str) -> Usuario:
        usuario = Usuario(nombre)
        self.usuarios[nombre] = usuario
        return usuario

    def agregar_transaccion(self, emisor: str, receptor: str, cantidad: float) -> bool:
        if emisor not in self.usuarios or receptor not in self.usuarios:
            return False
        tx = Transaccion(emisor, receptor, cantidad)
        tx.firma = self.usuarios[emisor].firmar_transaccion(tx)
        self.transacciones_pendientes.append(tx)
        return True

    def minar_transacciones_pendientes(self):
        if not self.transacciones_pendientes:
            return False
        ultimo = self.cadena[-1]
        bloque = Bloque(ultimo.indice + 1, self.transacciones_pendientes, time.time(), ultimo.hash)
        bloque.minar(self.dificultad)
        self.cadena.append(bloque)
        self.transacciones_pendientes = []
        return True

    def es_valida(self):
        for i in range(1, len(self.cadena)):
            actual = self.cadena[i]
            anterior = self.cadena[i - 1]
            if actual.hash != actual.calcular_hash():
                return False
            if actual.hash_anterior != anterior.hash:
                return False
        return True