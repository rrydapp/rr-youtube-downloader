import tkinter as tk
from tkinter import filedialog
import subprocess
import os
import sys
import ctypes  
import webbrowser  
from PIL import Image, ImageTk  

# =========================================================
# PALETA DE COLORES
# =========================================================

COLOR_BG_PRINCIPAL = "#1a1a1a"
COLOR_BG_PANEL = "#262626"
COLOR_TEXTO_MAIN = "#e6e6e6"
COLOR_TEXTO_MUTED = "#999999"
COLOR_ACCENTO = "#4a90e2"
COLOR_ACCENTO_HOVER = "#357abd"
COLOR_INPUT_BG = "#1f1f1f"
COLOR_BOTON_VERDE = "#2d7d46"
COLOR_BOTON_VERDE_HOVER = "#225e35"
COLOR_DONAR_TEXTO = "#ffb3c1" 
COLOR_ERROR = "#d9534f"

# =========================================================
# FUENTES GENERALES Y ESCALA DE POPUPS / DIÁLOGOS
# =========================================================

FONT_TITULO = ("Segoe UI", 14, "bold")
FONT_LABEL = ("Segoe UI", 11, "bold")
FONT_NORMAL = ("Segoe UI", 11)
FONT_BOTON = ("Segoe UI", 10, "bold")
FONT_BOTON_GRANDE = ("Segoe UI", 13, "bold")

# ESCALA AUMENTADA UNIFICADA PARA VENTANAS EMERGENTES (POPUP & HELP)
FONT_POPUP_TITULO = ("Segoe UI", 17, "bold")
FONT_POPUP_NORMAL = ("Segoe UI", 13)
FONT_POPUP_BOTON = ("Segoe UI", 12, "bold")

# NUEVA FUENTE DESTACADA PARA LA VERSIÓN
FONT_VERSION = ("Segoe UI", 11, "bold")

# =========================================================

ruta_descarga = os.path.join(os.path.expanduser("~"), "Music")

if not os.path.exists(ruta_descarga):
    ruta_descarga = os.getcwd()


def obtener_ruta_interna(nombre_archivo):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, nombre_archivo)
    return os.path.join(os.getcwd(), nombre_archivo)


def mostrar_pantalla_bienvenida():
    iniciar_app_principal()


def crear_menu_contextual(elemento_texto):
    menu = tk.Menu(
        elemento_texto,
        tearoff=0,
        bg=COLOR_BG_PANEL,
        fg=COLOR_TEXTO_MAIN,
        activebackground=COLOR_ACCENTO,
        activeforeground="white",
        bd=1
    )

    def pegar():
        try:
            texto = elemento_texto.clipboard_get()
            elemento_texto.insert(tk.INSERT, texto)
        except tk.TclError:
            pass

    menu.add_command(label="Paste URL", command=pegar)

    def mostrar_menu(event):
        menu.tk_popup(event.x_root, event.y_root)
        return "break"

    elemento_texto.bind("<Button-3>", mostrar_menu)


# =========================================================
# APP PRINCIPAL
# =========================================================

def iniciar_app_principal():
    root = tk.Tk()

    # FIX WINDOWS DPI
    root.tk.call('tk', 'scaling', 1.0)
    root.title("R&R Youtube Downloader")
    root.geometry("640x440")  # Aumentado el alto a 440 para dar espacio limpio a la versión
    root.resizable(False, False)
    root.configure(bg=COLOR_BG_PRINCIPAL)

    # -----------------------------------------------------
    # MODIFICACIÓN: FORZAR MODO OSCURO EN LA BARRA DE WINDOWS
    # -----------------------------------------------------
    try:
        root.update()
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        # El atributo 20 aplica el Immersive Dark Mode nativo en Windows 10 y 11
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(ctypes.c_int(1)), 4)
    except Exception:
        pass  # Si no es Windows o falla, se ignora de forma segura

    formato_var = tk.StringVar(value="Audio (MP3)")
    calidad_var = tk.StringVar(value="Best (320 kbps)")

    # =====================================================
    # COMPONENTES GRÁFICOS PARA VENTANAS EMERGENTES 
    # =====================================================

    def mostrar_alerta_custom(titulo, mensaje, tipo="info"):
        """Ventana emergente personalizada con escala de letra aumentada."""
        color_titulo = COLOR_ACCENTO
        if tipo == "error":
            color_titulo = COLOR_ERROR
        elif tipo == "success":
            color_titulo = COLOR_BOTON_VERDE

        dialogo = tk.Toplevel(root)
        dialogo.title(titulo)
        dialogo.configure(bg=COLOR_BG_PANEL)
        dialogo.resizable(False, False)
        
        ancho_window, alto_window = 580, 320
        x = root.winfo_x() + (640 - ancho_window) // 2
        y = root.winfo_y() + (440 - alto_window) // 2
        dialogo.geometry(f"{ancho_window}x{alto_window}+{x}+{y}")

        try:  # Forzar barra oscura también en este popup
            dialogo.update()
            hwnd_popup = ctypes.windll.user32.GetParent(dialogo.winfo_id())
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd_popup, 20, ctypes.byref(ctypes.c_int(1)), 4)
        except Exception:
            pass

        lbl_titulo = tk.Label(dialogo, text=titulo.upper(), font=FONT_POPUP_TITULO, bg=COLOR_BG_PANEL, fg=color_titulo)
        lbl_titulo.pack(pady=(22, 10))

        lbl_msg = tk.Label(dialogo, text=mensaje, font=FONT_POPUP_NORMAL, bg=COLOR_BG_PANEL, fg=COLOR_TEXTO_MAIN, justify="center", wraplength=520)
        lbl_msg.pack(pady=10, padx=25, fill="both", expand=True)

        btn_ok = tk.Button(
            dialogo, text="OK", font=FONT_POPUP_BOTON, bg=COLOR_ACCENTO, fg="white", 
            activebackground=COLOR_ACCENTO_HOVER, activeforeground="white", bd=0, command=dialogo.destroy
        )
        btn_ok.pack(pady=(10, 22), ipadx=35, ipady=8)

        dialogo.grab_set()
        root.wait_window(dialogo)

    def mostrar_pregunta_custom(titulo, mensaje):
        """Ventana emergente de confirmación (Donación) con escala de letra aumentada."""
        resultado = tk.BooleanVar(value=False)

        dialogo = tk.Toplevel(root)
        dialogo.title(titulo)
        dialogo.configure(bg=COLOR_BG_PANEL)
        dialogo.resizable(False, False)
        
        ancho_window, alto_window = 580, 340
        x = root.winfo_x() + (640 - ancho_window) // 2
        y = root.winfo_y() + (440 - alto_window) // 2
        dialogo.geometry(f"{ancho_window}x{alto_window}+{x}+{y}")

        try:  # Forzar barra oscura también en este popup
            dialogo.update()
            hwnd_popup = ctypes.windll.user32.GetParent(dialogo.winfo_id())
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd_popup, 20, ctypes.byref(ctypes.c_int(1)), 4)
        except Exception:
            pass

        lbl_titulo = tk.Label(dialogo, text=titulo.upper(), font=FONT_POPUP_TITULO, bg=COLOR_BG_PANEL, fg=COLOR_DONAR_TEXTO)
        lbl_titulo.pack(pady=(22, 8))

        lbl_msg = tk.Label(dialogo, text=mensaje, font=FONT_POPUP_NORMAL, bg=COLOR_BG_PANEL, fg=COLOR_TEXTO_MAIN, justify="center", wraplength=520)
        lbl_msg.pack(pady=5, padx=25, fill="both", expand=True)

        frame_btn = tk.Frame(dialogo, bg=COLOR_BG_PANEL)
        frame_btn.pack(pady=(10, 22))

        def al_aceptar():
            resultado.set(True)
            dialogo.destroy()

        def al_cancelar():
            resultado.set(False)
            dialogo.destroy()

        btn_si = tk.Button(
            frame_btn, text="YES, GO", font=FONT_POPUP_BOTON, bg=COLOR_BOTON_VERDE, fg="white", 
            activebackground=COLOR_BOTON_VERDE_HOVER, activeforeground="white", bd=0, command=al_aceptar
        )
        btn_si.pack(side="left", padx=15, ipadx=25, ipady=8)

        btn_no = tk.Button(
            frame_btn, text="NOT NOW", font=FONT_POPUP_BOTON, bg=COLOR_BG_PRINCIPAL, fg=COLOR_TEXTO_MUTED, 
            activebackground=COLOR_INPUT_BG, activeforeground="white", bd=1, relief="solid", command=al_cancelar
        )
        btn_no.pack(side="left", padx=15, ipadx=25, ipady=8)

        dialogo.grab_set()
        root.wait_window(dialogo)
        return resultado.get()

    # =====================================================
    # PREPARAR LOGO PORTÁTIL
    # =====================================================
    ruta_logo = obtener_ruta_interna("R&R2.jpg")
    img_logo_tk = None

    if os.path.exists(ruta_logo):
        try:
            img_original = Image.open(ruta_logo)
            img_redimensionada = img_original.resize((80, 37), Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.BICUBIC)
            img_logo_tk = ImageTk.PhotoImage(img_redimensionada)
        except Exception as e:
            print(f"No se pudo cargar el logo: {e}")

    # =====================================================
    # CAMBIAR Y ABRIR RUTA
    # =====================================================

    def cambiar_ruta_destino():
        global ruta_descarga
        carpeta = filedialog.askdirectory(title="Select Output Folder")
        if carpeta:
            ruta_descarga = carpeta
            lbl_ruta_visible.config(text=ruta_descarga)

    def abrir_carpeta_destino():
        try:
            if os.path.exists(ruta_descarga):
                os.startfile(ruta_descarga)
            else:
                mostrar_alerta_custom("Error", "The specified folder does not exist.", "error")
        except Exception as e:
            mostrar_alerta_custom("Error", f"Could not open folder:\n{e}", "error")

    # =====================================================
    # ENLACE DE DONACIÓN CON MENSAJE MOTIVACIONAL 
    # =====================================================

    def abrir_pagina_donacion():
        mensaje_incentivo = (
            "This application is 100% free and ad-free.\n\n"
            "If it saves you time and you love using it, please consider supporting its development. "
            "Your contributions help me dedicate more time to adding new features, fixing bugs, "
            "and keeping the download engine always updated.\n\n"
            "Would you like to visit the support page now?"
        )
        
        quiere_donar = mostrar_pregunta_custom("Support Project Development", mensaje_incentivo)
        
        if quiere_donar:
            url_donacion = "https://rrydapp.netlify.app/#donation"
            try:
                webbrowser.open(url_donacion)
            except Exception as e:
                mostrar_alerta_custom("Error", f"Could not open the website:\n{e}", "error")

    # =====================================================
    # PEGAR PORTAPAPELES
    # =====================================================

    def pegar_del_portapapeles():
        try:
            texto = root.clipboard_get().strip()
            if texto.startswith(("http://", "https://")):
                entry_url.delete(0, tk.END)
                entry_url.insert(0, texto)
        except tk.TclError:
            pass

    # =====================================================
    # SMART PASTE BUTTON
    # =====================================================

    def verificar_portapapeles_bucle():
        try:
            texto = root.clipboard_get().strip()
            if texto.startswith(("http://", "https://")):
                btn_pegar.pack(
                    side="right",
                    padx=(8, 0),
                    ipadx=14,
                    ipady=5
                )
            else:
                btn_pegar.pack_forget()
        except tk.TclError:
            btn_pegar.pack_forget()

        root.after(500, verificar_portapapeles_bucle)

    # =====================================================
    # ACTUALIZAR CALIDADES
    # =====================================================

    def actualizar_opciones_calidad(*args):
        formato = formato_var.get()
        if formato == "Audio (MP3)":
            nuevas_opciones = [
                "Best (320 kbps)",
                "Standard (192 kbps)",
                "Light (128 kbps)"
            ]
        else:
            nuevas_opciones = [
                "4K (2160p)",
                "2K (1440p)",
                "1080p (Full HD)",
                "720p (HD)",
                "480p (SD)"
            ]

        menu_calidad['menu'].delete(0, 'end')
        for opcion in nuevas_opciones:
            menu_calidad['menu'].add_command(
                label=opcion,
                command=lambda value=opcion: calidad_var.set(value)
            )

        calidad_var.set(nuevas_opciones[0])

    # =====================================================
    # VENTANA HELP (ESCALA DE LETRA E INTERFAZ AUMENTADA)
    # =====================================================

    def abrir_ayuda_modal():
        ventana_ayuda = tk.Toplevel(root)
        ventana_ayuda.title("Application Help & Quick Guide")
        
        ventana_ayuda.geometry("700x580")
        ventana_ayuda.resizable(False, False)
        ventana_ayuda.configure(bg=COLOR_BG_PANEL)

        x_main = root.winfo_x()
        y_main = root.winfo_y()
        ventana_ayuda.geometry(f"+{x_main - 30}+{y_main - 50}")

        try:  # Forzar barra oscura también en la ventana de ayuda
            ventana_ayuda.update()
            hwnd_ayuda = ctypes.windll.user32.GetParent(ventana_ayuda.winfo_id())
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd_ayuda, 20, ctypes.byref(ctypes.c_int(1)), 4)
        except Exception:
            pass

        ruta_audio = obtener_ruta_interna("R&R.mp3")
        audio_activo = False

        if os.path.exists(ruta_audio):
            try:
                ctypes.windll.winmm.mciSendStringW(f'open "{ruta_audio}" type mpegvideo alias help_sound', None, 0, 0)
                ctypes.windll.winmm.mciSendStringW('play help_sound repeat', None, 0, 0)
                audio_activo = True
            except Exception as e:
                print(f"Error al iniciar el audio: {e}")

        def cerrar_ayuda_limpio():
            if audio_activo:
                try:
                    ctypes.windll.winmm.mciSendStringW('stop help_sound', None, 0, 0)
                    ctypes.windll.winmm.mciSendStringW('close help_sound', None, 0, 0)
                except:
                    pass
            ventana_ayuda.destroy()

        ventana_ayuda.protocol("WM_DELETE_WINDOW", cerrar_ayuda_limpio)

        lbl_ayuda_titulo = tk.Label(
            ventana_ayuda,
            text="📋 APPLICATION HELP",
            font=FONT_POPUP_TITULO,
            bg=COLOR_BG_PANEL,
            fg=COLOR_ACCENTO
        )
        lbl_ayuda_titulo.pack(pady=(22, 12))

        texto_ayuda_en = (
            "SOURCE URL:\n"
            "Paste the YouTube video link you want to download here. "
            "You can use the [PASTE] button or right-click to paste easily.\n\n"
            "SMART PASTE BUTTON:\n"
            "The [PASTE] button automatically appears only when a valid web link "
            "(http/https) is detected in your clipboard.\n\n"
            "STORAGE PATH:\n"
            "Shows where your media files will be saved. "
            "Press [CHANGE] to modify this folder.\n\n"
            "TARGET FORMAT:\n"
            "Choose between extracting only the audio track "
            "(Audio MP3) or downloading the full video (Video MP4).\n\n"
            "QUALITY & RESOLUTION:\n"
            "Set your desired resolution. If you choose a quality higher than "
            "the original video supports (e.g. 4K), the engine automatically "
            "downloads the best available real quality without any error.\n\n"
        )

        frame_texto = tk.Frame(ventana_ayuda, bg=COLOR_BG_PANEL)
        frame_texto.pack(padx=30, pady=5, fill="both", expand=True)

        txt_ayuda_cuerpo = tk.Text(
            frame_texto,
            font=FONT_POPUP_NORMAL,
            bg=COLOR_BG_PANEL,
            fg=COLOR_TEXTO_MAIN,
            bd=0,
            relief="flat",
            wrap="word",
            cursor="arrow",
            spacing2=5,
            spacing3=10,
            padx=15,
            pady=10,
            highlightthickness=0
        )
        txt_ayuda_cuerpo.pack(fill="both", expand=True)
        txt_ayuda_cuerpo.insert("1.0", texto_ayuda_en)
        txt_ayuda_cuerpo.config(state="disabled")

        def on_mouse_wheel(event):
            txt_ayuda_cuerpo.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        txt_ayuda_cuerpo.bind("<MouseWheel>", on_mouse_wheel)

        btn_cerrar_ayuda = tk.Button(
            ventana_ayuda,
            text="CLOSE HELP",
            command=cerrar_ayuda_limpio,
            bg=COLOR_ACCENTO,
            fg="white",
            activebackground=COLOR_ACCENTO_HOVER,
            activeforeground="white",
            bd=0,
            font=FONT_POPUP_BOTON
        )
        btn_cerrar_ayuda.pack(pady=(12, 24), ipadx=30, ipady=8)
        ventana_ayuda.grab_set()

    # =====================================================
    # TOP BAR (BARRA SUPERIOR)
    # =====================================================

    frame_top = tk.Frame(root, bg=COLOR_BG_PRINCIPAL)
    frame_top.pack(fill="x", padx=25, pady=(18, 0))

    if img_logo_tk:
        lbl_logo_icono = tk.Label(frame_top, image=img_logo_tk, bg=COLOR_BG_PRINCIPAL)
        lbl_logo_icono.image = img_logo_tk  
        lbl_logo_icono.pack(side="left")

    btn_ayuda = tk.Button(
        frame_top,
        text="❓ HELP",
        command=abrir_ayuda_modal,
        bg=COLOR_BG_PANEL,
        fg=COLOR_TEXTO_MUTED,
        activebackground=COLOR_INPUT_BG,
        activeforeground="white",
        bd=1,
        relief="solid",
        font=FONT_BOTON
    )
    btn_ayuda.pack(side="right", ipadx=10, ipady=4)

    btn_donar = tk.Button(
        frame_top,
        text="💖 SUPPORT DEVELOPMENT",
        command=abrir_pagina_donacion,
        bg=COLOR_BG_PANEL,
        fg=COLOR_DONAR_TEXTO,
        activebackground=COLOR_INPUT_BG,
        activeforeground="white",
        bd=1,
        relief="solid",
        font=FONT_BOTON
    )
    btn_donar.pack(side="right", ipadx=10, ipady=4, padx=(0, 8))

    # =====================================================
    # SOURCE URL
    # =====================================================

    tk.Label(
        root,
        text="SOURCE URL",
        font=FONT_LABEL,
        bg=COLOR_BG_PRINCIPAL,
        fg=COLOR_TEXTO_MAIN
    ).pack(anchor="w", padx=25, pady=(10, 5))

    frame_url = tk.Frame(root, bg=COLOR_BG_PRINCIPAL)
    frame_url.pack(fill="x", padx=25)

    entry_url = tk.Entry(
        frame_url,
        font=FONT_NORMAL,
        bg=COLOR_INPUT_BG,
        fg=COLOR_TEXTO_MAIN,
        insertbackground="white",
        bd=1,
        relief="solid"
    )
    entry_url.pack(side="left", fill="x", expand=True, ipady=7)
    entry_url.focus()
    crear_menu_contextual(entry_url)

    btn_pegar = tk.Button(
        frame_url,
        text="📋 PASTE",
        command=pegar_del_portapapeles,
        bg=COLOR_ACCENTO,
        fg="white",
        activebackground=COLOR_ACCENTO_HOVER,
        activeforeground="white",
        bd=0,
        font=FONT_BOTON
    )

    # =====================================================
    # STORAGE PATH
    # =====================================================

    tk.Label(
        root,
        text="STORAGE PATH",
        font=FONT_LABEL,
        bg=COLOR_BG_PRINCIPAL,
        fg=COLOR_TEXTO_MAIN
    ).pack(anchor="w", padx=25, pady=(16, 5))

    frame_ruta = tk.Frame(root, bg=COLOR_BG_PRINCIPAL)
    frame_ruta.pack(fill="x", padx=25)

    lbl_ruta_visible = tk.Label(
        frame_ruta,
        text=ruta_descarga,
        font=FONT_NORMAL,
        bg=COLOR_INPUT_BG,
        fg=COLOR_TEXTO_MUTED,
        anchor="w",
        bd=1,
        relief="solid"
    )

    btn_abrir_ruta = tk.Button(
        frame_ruta,
        text="📂 OPEN",
        command=abrir_carpeta_destino,
        bg=COLOR_BG_PANEL,
        fg=COLOR_TEXTO_MAIN,
        activebackground=COLOR_INPUT_BG,
        activeforeground="white",
        bd=1,
        relief="solid",
        font=FONT_BOTON
    )

    btn_cambiar_ruta = tk.Button(
        frame_ruta,
        text="⚙ CHANGE",
        command=cambiar_ruta_destino,
        bg=COLOR_BG_PANEL,
        fg=COLOR_TEXTO_MAIN,
        activebackground=COLOR_INPUT_BG,
        activeforeground="white",
        bd=1,
        relief="solid",
        font=FONT_BOTON
    )

    btn_abrir_ruta.pack(side="right", ipadx=10, ipady=5)
    btn_cambiar_ruta.pack(side="right", ipadx=10, ipady=5, padx=(0, 8))
    lbl_ruta_visible.pack(side="left", fill="x", expand=True, ipady=7, padx=(0, 8))

    # =====================================================
    # OPCIONES
    # =====================================================

    frame_opciones = tk.Frame(root, bg=COLOR_BG_PRINCIPAL)
    frame_opciones.pack(fill="x", padx=25, pady=20)

    # FORMATO
    frame_row_formato = tk.Frame(frame_opciones, bg=COLOR_BG_PRINCIPAL)
    frame_row_formato.pack(fill="x", pady=6)

    lbl_fmt = tk.Label(
        frame_row_formato,
        text="TARGET FORMAT",
        font=FONT_LABEL,
        bg=COLOR_BG_PRINCIPAL,
        fg=COLOR_TEXTO_MAIN,
        width=16,
        anchor="w"
    )
    lbl_fmt.pack(side="left")

    menu_formato = tk.OptionMenu(frame_row_formato, formato_var, "Audio (MP3)", "Video (MP4)")
    menu_formato.configure(
        bg=COLOR_BG_PANEL, fg=COLOR_TEXTO_MAIN, activebackground=COLOR_INPUT_BG,
        activeforeground="white", bd=1, relief="solid", highlightthickness=0,
        font=FONT_NORMAL, width=20, anchor="w"
    )
    menu_formato["menu"].configure(bg=COLOR_INPUT_BG, fg=COLOR_TEXTO_MAIN, activebackground=COLOR_ACCENTO, font=FONT_NORMAL)
    menu_formato.pack(side="left")
    formato_var.trace_add("write", actualizar_opciones_calidad)

    # CALIDAD
    frame_row_calidad = tk.Frame(frame_opciones, bg=COLOR_BG_PRINCIPAL)
    frame_row_calidad.pack(fill="x", pady=6)

    lbl_qlty = tk.Label(
        frame_row_calidad,
        text="QUALITY",
        font=FONT_LABEL,
        bg=COLOR_BG_PRINCIPAL,
        fg=COLOR_TEXTO_MAIN,
        width=16,
        anchor="w"
    )
    lbl_qlty.pack(side="left")

    menu_calidad = tk.OptionMenu(frame_row_calidad, calidad_var, "Best (320 kbps)")
    menu_calidad.configure(
        bg=COLOR_BG_PANEL, fg=COLOR_TEXTO_MAIN, activebackground=COLOR_INPUT_BG,
        activeforeground="white", bd=1, relief="solid", highlightthickness=0,
        font=FONT_NORMAL, width=20, anchor="w"
    )
    menu_calidad["menu"].configure(bg=COLOR_INPUT_BG, fg=COLOR_TEXTO_MAIN, activebackground=COLOR_ACCENTO, font=FONT_NORMAL)
    menu_calidad.pack(side="left")

    actualizar_opciones_calidad()
    root.after(1000, verificar_portapapeles_bucle)

    # =====================================================
    # DESCARGA
    # =====================================================

    def procesar_descarga():
        url = entry_url.get().strip()
        formato_elegido = formato_var.get()
        calidad_elegida = calidad_var.get()

        if not url:
            mostrar_alerta_custom("Warning", "Please paste a valid YouTube link.", "warning")
            return

        ytdlp_completo = obtener_ruta_interna("yt-dlp.exe")
        ffmpeg_completo = obtener_ruta_interna("ffmpeg.exe")
        carpeta_temporal_ffmpeg = os.path.dirname(ffmpeg_completo)

        if not os.path.exists(ytdlp_completo):
            mostrar_alerta_custom("Critical Error", "Internal engine (yt-dlp) not found.", "error")
            return

        btn_descargar.config(state="disabled", text="PROCESSING DOWNLOAD...", bg=COLOR_BG_PANEL)
        root.update()

        comando = [
            ytdlp_completo,
            "--no-playlist",
            "--ffmpeg-location", carpeta_temporal_ffmpeg,
            "-P", ruta_descarga
        ]

        if formato_elegido == "Audio (MP3)":
            vbr_quality = "0"
            if "192 kbps" in calidad_elegida: vbr_quality = "5"
            elif "128 kbps" in calidad_elegida: vbr_quality = "9"

            comando.extend(["-x", "--audio-format", "mp3", "--audio-quality", vbr_quality])
            comando.extend(["--print", "after_move:audio_bitrate"])
        else:
            res = "2160"
            if "2K" in calidad_elegida: res = "1440"
            elif "1080p" in calidad_elegida: res = "1080"
            elif "720p" in calidad_elegida: res = "720"
            elif "480p" in calidad_elegida: res = "480"

            comando.extend(["-f", f"bv*[height<={res}][ext=mp4]+ba[ext=m4a]/b[height<={res}][ext=mp4]"])
            comando.extend(["--print", "after_move:%(resolution)s"])

        comando.append(url)

        try:
            resultado = subprocess.run(comando, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if resultado.returncode == 0:
                salida_lineas = resultado.stdout.strip().split('\n')
                calidad_real = salida_lineas[-1] if salida_lineas else "Unknown"

                if formato_elegido == "Audio (MP3)":
                    calidad_final_msg = f"{calidad_real} kbps" if calidad_real.isdigit() else calidad_elegida
                    mensaje_exito = f"Audio successfully converted to MP3.\nReal Output Quality: {calidad_final_msg}"
                else:
                    mensaje_exito = f"Video successfully downloaded as MP4.\nReal Output Resolution: {calidad_real}"

                mostrar_alerta_custom("Success", f"{mensaje_exito}\n\nLocation: {ruta_descarga}", "success")
                entry_url.delete(0, tk.END)
            else:
                mostrar_alerta_custom("Engine Error", f"Details:\n{resultado.stderr}", "error")
        except Exception as e:
            mostrar_alerta_custom("Critical Error", "Execution failed:\n" + str(e), "error")
        finally:
            btn_descargar.config(state="normal", text="RENDER & DOWNLOAD", bg=COLOR_BOTON_VERDE)

    # =====================================================
    # BOTÓN DESCARGA
    # =====================================================

    btn_descargar = tk.Button(
        root,
        text="RENDER & DOWNLOAD",
        command=procesar_descarga,
        bg=COLOR_BOTON_VERDE,
        fg="white",
        activebackground=COLOR_BOTON_VERDE_HOVER,
        activeforeground="white",
        bd=0,
        font=FONT_BOTON_GRANDE
    )
    btn_descargar.pack(fill="x", padx=25, pady=(10, 0), ipady=12)

    # =====================================================
    # MODIFICACIÓN: IMPLEMENTACIÓN DE LA VERSIÓN DESTACADA
    # =====================================================
    lbl_version = tk.Label(
        root, 
        text="v1.0", 
        font=FONT_VERSION, 
        bg=COLOR_BG_PRINCIPAL, 
        fg=COLOR_TEXTO_MUTED
    )
    lbl_version.pack(side="bottom", anchor="e", padx=25, pady=(10, 12))

    root.mainloop()


# =========================================================

if __name__ == "__main__":
    mostrar_pantalla_bienvenida()