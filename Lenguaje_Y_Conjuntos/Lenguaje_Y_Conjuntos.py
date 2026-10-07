import tkinter as tk
from tkinter import ttk, messagebox
import re
import itertools


# =====================================================================
# CAPA LOGICA: MODULO A - MOTOR DEL COMPILADOR (DSL)
# =====================================================================
class RecetarioCompiler:
    def __init__(self):
        self.token_patterns = {
            "AGREGAR": re.compile(
                r"^AGREGAR\s+(\d+(?:\.\d+)?)\s*([a-zA-Z]+)\s+DE\s+([a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+)$",
                re.IGNORECASE
            ),
            
            "CORTE": re.compile(
                r"^(PICAR|CORTAR)\s+([a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+)$",
                re.IGNORECASE
            ),
            
            "MEZCLAR": re.compile(
                r"^MEZCLAR\s+([a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+)\s+Y\s+([a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+)$",
                re.IGNORECASE
            ),
            
            "TERMICO": re.compile(
                r"^(CALENTAR|HORNEAR)\s+A\s+(\d+)\s*grados\s+POR\s+(\d+)\s*minutos$",
                re.IGNORECASE
            ),
            
            "SERVIR": re.compile(
                r"^SERVIR$",
                re.IGNORECASE
            )
        }

    def analizar_linea(self, linea, num_linea):
        linea = linea.strip()

        # Ignorar líneas vacías
        if not linea:
            return None, None

        # Revisar cada patrón
        for token_type, pattern in self.token_patterns.items():
            match = pattern.match(linea)

            if match:

                # -----------------------------------------------------
                # AGREGAR
                # -----------------------------------------------------
                if token_type == "AGREGAR":
                    cant, unidad, ingrediente = match.groups()

                    asm = (
                        f"; --- Linea {num_linea}: {linea} ---\n"
                        f"MOV R1, {cant}\n"
                        f"MOV R2, '{unidad.strip()}'\n"
                        f"MOV R3, '{ingrediente.strip()}'\n"
                        f"CALL sys_agregar\n"
                    )

                    return asm, None

                # -----------------------------------------------------
                # PICAR / CORTAR
                # -----------------------------------------------------
                elif token_type == "CORTE":
                    accion, ingrediente = match.groups()

                    asm = (
                        f"; --- Linea {num_linea}: {linea} ---\n"
                        f"MOV R1, '{ingrediente.strip()}'\n"
                        f"CALL sys_{accion.lower()}\n"
                    )

                    return asm, None

                # -----------------------------------------------------
                # MEZCLAR
                # -----------------------------------------------------
                elif token_type == "MEZCLAR":
                    ing1, ing2 = match.groups()

                    asm = (
                        f"; --- Linea {num_linea}: {linea} ---\n"
                        f"MOV R1, '{ing1.strip()}'\n"
                        f"MOV R2, '{ing2.strip()}'\n"
                        f"CALL sys_mezclar\n"
                    )

                    return asm, None

                # -----------------------------------------------------
                # CALENTAR / HORNEAR
                # -----------------------------------------------------
                elif token_type == "TERMICO":
                    accion, temp, tiempo = match.groups()

                    asm = (
                        f"; --- Linea {num_linea}: {linea} ---\n"
                        f"MOV R1, {temp}\n"
                        f"MOV R2, {tiempo}\n"
                        f"CALL sys_{accion.lower()}\n"
                    )

                    return asm, None

                # -----------------------------------------------------
                # SERVIR
                # -----------------------------------------------------
                elif token_type == "SERVIR":
                    asm = (
                        f"; --- Linea {num_linea}: {linea} ---\n"
                        f"CALL sys_servir\n"
                        f"HALT\n"
                    )

                    return asm, None

        # -------------------------------------------------------------
        # ERROR SINTACTICO
        # -------------------------------------------------------------
        err_msg = (
            f"Linea {num_linea}: Estructura invalida o parametros "
            f"erroneos en: '{linea.upper()}'"
        )

        return None, err_msg

    def compilar(self, texto_fuente):
        lineas = texto_fuente.splitlines()

        codigo_objeto = ""
        tabla_errores = []

        for idx, linea in enumerate(lineas, 1):
            asm, err = self.analizar_linea(linea, idx)

            if err:
                tabla_errores.append(err)

            elif asm:
                codigo_objeto += asm + "\n"

        return codigo_objeto, tabla_errores


# =====================================================================
# CAPA LOGICA: MODULO B - COMPUTO FORMAL MATEMATICO
# =====================================================================
class AnalizadorMatematico:

    @staticmethod
    def limpiar_y_convertir_conjunto(entrada_texto):
        if not entrada_texto.strip():
            return set()

        return {
            elem.strip()
            for elem in entrada_texto.split(",")
            if elem.strip()
        }

    @staticmethod
    def clasificar_en_dominios_numericos(conjunto_datos):
        dominios = {
            "N": set(),
            "Z": set(),
            "Q": set(),
            "TXT": set()
        }

        for item in conjunto_datos:

            # ---------------------------------------------------------
            # ENTEROS
            # ---------------------------------------------------------
            try:
                valor_int = int(item)

                dominios["Z"].add(valor_int)

                if valor_int >= 0:
                    dominios["N"].add(valor_int)

                dominios["Q"].add(float(valor_int))

                continue

            except ValueError:
                pass

            # ---------------------------------------------------------
            # DECIMALES
            # ---------------------------------------------------------
            try:
                valor_float = float(item)

                dominios["Q"].add(valor_float)

                continue

            except ValueError:
                pass

            # ---------------------------------------------------------
            # TEXTO
            # ---------------------------------------------------------
            dominios["TXT"].add(item)

        return dominios

    @staticmethod
    def generar_clausura_kleene(alfabeto, max_longitud=3):
        # epsilon
        clausura = ["eps"]

        # Generar cadenas de longitud 1, 2, 3...
        for r in range(1, max_longitud + 1):

            combinaciones = itertools.product(
                sorted(alfabeto),
                repeat=r
            )

            for comb in combinaciones:
                clausura.append("".join(comb))

        return clausura


# =====================================================================
# CAPA DE PRESENTACION: INTERFAZ GRAFICA DE USUARIO (GUI)
# =====================================================================
class AppVentanaPrincipal(tk.Tk):

    def __init__(self):
        super().__init__()

        # -------------------------------------------------------------
        # CONFIGURACION DE LA VENTANA
        # -------------------------------------------------------------
        self.title(
            "Teoria Matematica de la Computacion - Practica de Laboratorio"
        )

        self.geometry("950x700")
        self.minsize(800, 600)

        # -------------------------------------------------------------
        # MOTOR DEL COMPILADOR
        # -------------------------------------------------------------
        self.compilador_dsl = RecetarioCompiler()

        # -------------------------------------------------------------
        # NOTEBOOK / PESTAÑAS
        # -------------------------------------------------------------
        self.pestanas_control = ttk.Notebook(self)

        self.pestanas_control.pack(
            fill="both",
            expand=True
        )

        # Crear módulos
        self.crear_entorno_modulo_a()
        self.crear_entorno_modulo_b()


    # =================================================================
    # MODULO A
    # =================================================================
    def crear_entorno_modulo_a(self):

        frame_a = ttk.Frame(self.pestanas_control)

        self.pestanas_control.add(
            frame_a,
            text="Modulo A: Compilador DSL"
        )

        # -------------------------------------------------------------
        # TITULO
        # -------------------------------------------------------------
        lbl_instrucciones = ttk.Label(
            frame_a,
            text="Editor del Codigo Fuente de la Receta:",
            font=("Arial", 10, "bold")
        )

        lbl_instrucciones.pack(
            anchor="w",
            padx=15,
            pady=5
        )

        # -------------------------------------------------------------
        # PANEL DIVIDIDO
        # -------------------------------------------------------------
        panel_dividido = ttk.PanedWindow(
            frame_a,
            orient=tk.HORIZONTAL
        )

        panel_dividido.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=5
        )

        # -------------------------------------------------------------
        # PANEL IZQUIERDO
        # -------------------------------------------------------------
        box_izquierda = ttk.Frame(panel_dividido)

        self.txt_codigo_fuente = tk.Text(
            box_izquierda,
            font=("Courier New", 10),
            wrap="none",
            width=45
        )

        self.txt_codigo_fuente.pack(
            fill="both",
            expand=True
        )

        # Receta de demostracion
        receta_demo = (
            "AGREGAR 500 g DE HARINA\n"
            "AGREGAR 15 ml DE ACEITE\n"
            "MEZCLAR HARINA Y ACEITE\n"
            "PICAR CEBOLLA\n"
            "CALENTAR A 180 grados POR 15 minutos\n"
            "SERVIR"
        )

        self.txt_codigo_fuente.insert(
            "1.0",
            receta_demo
        )

        panel_dividido.add(
            box_izquierda,
            weight=1
        )

        # -------------------------------------------------------------
        # PANEL DERECHO
        # -------------------------------------------------------------
        box_derecha = ttk.Frame(panel_dividido)

        self.txt_salida_compilador = tk.Text(
            box_derecha,
            font=("Courier New", 10),
            wrap="none",
            bg="#f8f9fa",
            width=50
        )

        self.txt_salida_compilador.pack(
            fill="both",
            expand=True
        )

        panel_dividido.add(
            box_derecha,
            weight=1
        )

        # -------------------------------------------------------------
        # BOTON
        # -------------------------------------------------------------
        btn_ejecutar = ttk.Button(
            frame_a,
            text="Analizar y Sintetizar Receta",
            command=self.ejecutar_compilacion
        )

        btn_ejecutar.pack(
            pady=12
        )


    # =================================================================
    # EJECUTAR COMPILACION
    # =================================================================
    def ejecutar_compilacion(self):

        # Obtener codigo fuente
        fuente = self.txt_codigo_fuente.get(
            "1.0",
            tk.END
        )

        # Compilar
        codigo_objeto, errores = self.compilador_dsl.compilar(
            fuente
        )

        # Limpiar salida
        self.txt_salida_compilador.delete(
            "1.0",
            tk.END
        )

        # -------------------------------------------------------------
        # MOSTRAR ERRORES
        # -------------------------------------------------------------
        if errores:

            self.txt_salida_compilador.insert(
                tk.END,
                "DIAGNOSTICO DE ERRORES SINTACTICOS:\n"
            )

            self.txt_salida_compilador.insert(
                tk.END,
                "=" * 60 + "\n\n"
            )

            for err in errores:

                self.txt_salida_compilador.insert(
                    tk.END,
                    f"{err}\n"
                )

        # -------------------------------------------------------------
        # MOSTRAR CODIGO GENERADO
        # -------------------------------------------------------------
        else:

            self.txt_salida_compilador.insert(
                tk.END,
                "; === CODIGO ENSAMBLADOR GENERADO CON EXITO ===\n"
            )

            self.txt_salida_compilador.insert(
                tk.END,
                "=" * 60 + "\n\n"
            )

            self.txt_salida_compilador.insert(
                tk.END,
                codigo_objeto
            )


    # =================================================================
    # MODULO B
    # =================================================================
    def crear_entorno_modulo_b(self):

        frame_b = ttk.Frame(
            self.pestanas_control
        )

        self.pestanas_control.add(
            frame_b,
            text="Modulo B: Algebra y Lenguajes Formales"
        )

        # -------------------------------------------------------------
        # SECCION DE CONJUNTOS
        # -------------------------------------------------------------
        sub_frame_conjuntos = ttk.LabelFrame(
            frame_b,
            text=" Algebra de Conjuntos y Dominios Numericos "
        )

        sub_frame_conjuntos.pack(
            fill="x",
            padx=15,
            pady=8
        )

        # Conjunto A
        ttk.Label(
            sub_frame_conjuntos,
            text="Conjunto A:"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=10,
            pady=5
        )

        self.input_conjunto_a = ttk.Entry(
            sub_frame_conjuntos,
            width=65
        )

        self.input_conjunto_a.grid(
            row=0,
            column=1,
            padx=10,
            pady=5
        )

        self.input_conjunto_a.insert(
            0,
            "0, 12, -4, 2.718, agua, 5, levadura"
        )

        # Conjunto B
        ttk.Label(
            sub_frame_conjuntos,
            text="Conjunto B:"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=10,
            pady=5
        )

        self.input_conjunto_b = ttk.Entry(
            sub_frame_conjuntos,
            width=65
        )

        self.input_conjunto_b.grid(
            row=1,
            column=1,
            padx=10,
            pady=5
        )

        self.input_conjunto_b.insert(
            0,
            "0, 5, agua, 99"
        )

        # -------------------------------------------------------------
        # BOTON DE CONJUNTOS
        # -------------------------------------------------------------
        btn_calcular_conjuntos = ttk.Button(
            sub_frame_conjuntos,
            text="Calcular Relaciones y Clasificar",
            command=self.ejecutar_calculos_conjuntos
        )

        btn_calcular_conjuntos.grid(
            row=2,
            column=0,
            columnspan=2,
            pady=8
        )

        # -------------------------------------------------------------
        # SECCION DE KLEENE
        # -------------------------------------------------------------
        sub_frame_kleene = ttk.LabelFrame(
            frame_b,
            text=" Teoria de Alfabetos (Clausura de Kleene) "
        )

        sub_frame_kleene.pack(
            fill="x",
            padx=15,
            pady=8
        )

        # Alfabeto
        ttk.Label(
            sub_frame_kleene,
            text="Alfabeto Sigma:"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=10,
            pady=5
        )

        self.input_alfabeto = ttk.Entry(
            sub_frame_kleene,
            width=35
        )

        self.input_alfabeto.grid(
            row=0,
            column=1,
            sticky="w",
            padx=10,
            pady=5
        )

        self.input_alfabeto.insert(
            0,
            "0, 1"
        )

        # -------------------------------------------------------------
        # BOTON KLEENE
        # -------------------------------------------------------------
        btn_calcular_kleene = ttk.Button(
            sub_frame_kleene,
            text="Calcular Sigma*",
            command=self.ejecutar_kleene
        )

        btn_calcular_kleene.grid(
            row=0,
            column=2,
            padx=15,
            pady=5
        )


    # =================================================================
    # CALCULAR RELACIONES Y CLASIFICACION
    # =================================================================
    def ejecutar_calculos_conjuntos(self):

        # Obtener conjuntos
        conjunto_a = (
            AnalizadorMatematico
            .limpiar_y_convertir_conjunto(
                self.input_conjunto_a.get()
            )
        )

        conjunto_b = (
            AnalizadorMatematico
            .limpiar_y_convertir_conjunto(
                self.input_conjunto_b.get()
            )
        )

        # -------------------------------------------------------------
        # OPERACIONES ENTRE CONJUNTOS
        # -------------------------------------------------------------
        interseccion = conjunto_a & conjunto_b
        union = conjunto_a | conjunto_b
        diferencia_ab = conjunto_a - conjunto_b
        diferencia_ba = conjunto_b - conjunto_a

        # -------------------------------------------------------------
        # RELACIONES DE INCLUSION
        # -------------------------------------------------------------
        a_subconjunto_b = conjunto_a.issubset(conjunto_b)
        b_subconjunto_a = conjunto_b.issubset(conjunto_a)

        # -------------------------------------------------------------
        # CLASIFICACION DE A
        # -------------------------------------------------------------
        dominios_a = (
            AnalizadorMatematico
            .clasificar_en_dominios_numericos(
                conjunto_a
            )
        )

        # -------------------------------------------------------------
        # CLASIFICACION DE B
        # -------------------------------------------------------------
        dominios_b = (
            AnalizadorMatematico
            .clasificar_en_dominios_numericos(
                conjunto_b
            )
        )

        # -------------------------------------------------------------
        # CONVERTIR A TEXTO
        # -------------------------------------------------------------
        resultado = ""

        resultado += "RESULTADOS DE CONJUNTOS\n"
        resultado += "=" * 60 + "\n\n"

        resultado += f"A = {conjunto_a}\n"
        resultado += f"B = {conjunto_b}\n\n"

        resultado += "OPERACIONES:\n"
        resultado += "-" * 30 + "\n"

        resultado += f"A ∩ B = {interseccion}\n"
        resultado += f"A ∪ B = {union}\n"
        resultado += f"A - B = {diferencia_ab}\n"
        resultado += f"B - A = {diferencia_ba}\n\n"

        resultado += "RELACIONES:\n"
        resultado += "-" * 30 + "\n"

        resultado += f"A ⊆ B = {a_subconjunto_b}\n"
        resultado += f"B ⊆ A = {b_subconjunto_a}\n\n"

        # -------------------------------------------------------------
        # DOMINIOS DE A
        # -------------------------------------------------------------
        resultado += "DOMINIOS NUMERICOS DE A:\n"
        resultado += "-" * 30 + "\n"

        resultado += f"N = {dominios_a['N']}\n"
        resultado += f"Z = {dominios_a['Z']}\n"
        resultado += f"Q = {dominios_a['Q']}\n"
        resultado += f"TXT = {dominios_a['TXT']}\n\n"

        # -------------------------------------------------------------
        # DOMINIOS DE B
        # -------------------------------------------------------------
        resultado += "DOMINIOS NUMERICOS DE B:\n"
        resultado += "-" * 30 + "\n"

        resultado += f"N = {dominios_b['N']}\n"
        resultado += f"Z = {dominios_b['Z']}\n"
        resultado += f"Q = {dominios_b['Q']}\n"
        resultado += f"TXT = {dominios_b['TXT']}"

        # Mostrar resultados
        messagebox.showinfo(
            "Resultados de Conjuntos",
            resultado
        )


    # =================================================================
    # CALCULAR CLAUSURA DE KLEENE
    # =================================================================
    def ejecutar_kleene(self):

        # Obtener alfabeto
        alfabeto = (
            AnalizadorMatematico
            .limpiar_y_convertir_conjunto(
                self.input_alfabeto.get()
            )
        )

        # -------------------------------------------------------------
        # VALIDAR ALFABETO
        # -------------------------------------------------------------
        if not alfabeto:

            messagebox.showwarning(
                "Advertencia",
                "Debes ingresar al menos un simbolo para el alfabeto."
            )

            return

        # -------------------------------------------------------------
        # GENERAR CLAUSURA
        # -------------------------------------------------------------
        clausura = (
            AnalizadorMatematico
            .generar_clausura_kleene(
                alfabeto,
                max_longitud=3
            )
        )

        # -------------------------------------------------------------
        # MOSTRAR RESULTADO
        # -------------------------------------------------------------
        resultado = ""

        resultado += "CLAUSURA DE KLEENE\n"
        resultado += "=" * 60 + "\n\n"

        resultado += f"Σ = {alfabeto}\n\n"

        resultado += "Σ* hasta longitud 3:\n"
        resultado += "-" * 30 + "\n\n"

        resultado += ", ".join(clausura)

        messagebox.showinfo(
            "Sigma*",
            resultado
        )


# =====================================================================
# INICIO DEL PROGRAMA
# =====================================================================
if __name__ == "__main__":
    app = AppVentanaPrincipal()
    app.mainloop()
