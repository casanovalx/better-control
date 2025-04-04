"""
Adding new languages for better user preferences

To add a new language, create a new class with the same name as the language
 and update the get_translations function to include the new language.
The class should contain all the translations for the new language.

Also update all other tabs to use the new language class.
eg :
    class SettingsTab(Gtk.Box):
        def __init__(self, logging: Logger, txt: English|Spanish|Portuguese|NEW_LANGUAGE):
"""

import os
from logging import Logger

from utils.logger import LogLevel


class English:
    """English language translation for the application"""
    def __init__(self):
        # app description
        self.msg_desc = "A sleek GTK-themed control panel for Linux."
        self.msg_app_url = "https://github.com/quantumvoid0/better-control"
        self.msg_usage = "Usage"

        # for args
        self.msg_args_help = "Prints this message"
        self.msg_args_autostart = "Starts with the autostart tab open"
        self.msg_args_battery = "Starts with the battery tab open"
        self.msg_args_bluetooth = "Starts with the bluetooth tab open"
        self.msg_args_display = "Starts with the display tab open"
        self.msg_args_force = "Makes the app force to have all dependencies installed"
        self.msg_args_power = "Starts with the power tab open"
        self.msg_args_volume = "Starts with the volume tab open"
        self.msg_args_volume_v = "Also starts with the volume tab open"
        self.msg_args_wifi = "Starts with the wifi tab open"

        self.msg_args_log = "The program will either log to a file if given a file path,\n or output to stdout based on the log level if given a value between 0, and 3."
        self.msg_args_redact = "Redact sensitive information from logs (network names, device IDs, etc.)"
        self.msg_args_size = "Sets a custom window size"

        # commonly used
        self.connect = "Connect"
        self.connected = "Connected"
        self.connecting = "Connecting..."
        self.disconnect = "Disconnect"
        self.disconnected = "Disconnected"
        self.disconnecting = "Disconnecting..."
        self.enable = "Enable"
        self.disable = "Disable"
        self.close = "Close"
        self.show = "Show"
        self.loading = "Loading..."
        self.loading_tabs = "Loading tabs..."

        # for tabs
        self.msg_tab_autostart = "Autostart"
        self.msg_tab_battery = "Battery"
        self.msg_tab_bluetooth = "Bluetooth"
        self.msg_tab_display = "Display"
        self.msg_tab_power = "Power"
        self.msg_tab_volume = "Volume"
        self.msg_tab_wifi = "Wi-Fi"

        # Autostart tab translations
        self.autostart_title = "Autostart Applications"
        self.autostart_session = "Session"
        self.autostart_show_system_apps = "Show system autostart applications"
        self.autostart_configured_applications = "Configured Applications"
        self.autostart_tooltip_rescan = "Rescan autostart apps"

        # Battery tab translations
        self.battery_title = "Battery Dashboard"
        self.battery_power_saving = "Power Saving"
        self.battery_balanced = "Balanced"
        self.battery_performance = "Performance"
        self.battery_batteries = "Batteries"
        self.battery_overview = "Overview"
        self.battery_details = "Details"
        self.battery_tooltip_refresh = "Refresh Battery Information"
        self.battery_no_batteries = "No battery detected"

        # Bluetooth tab translations
        self.bluetooth_title = "Bluetooth Devices"
        self.bluetooth_scan_devices = "Scan for Devices"
        self.bluetooth_scanning = "Scanning..."
        self.bluetooth_power = "Bluetooth"
        self.bluetooth_available_devices = "Available Devices"
        self.bluetooth_tooltip_refresh = "Scan for Devices"
        self.bluetooth_connect_failed = "Failed to connect to device"
        self.bluetooth_disconnect_failed = "Failed to disconnect from device"
        self.bluetooth_try_again = "Please try again later."

        # Display tab translations
        self.display_title = "Display Settings"
        self.display_brightness = "Screen Brightness"
        self.display_blue_light = "Blue Light"

        # Power tab translations
        self.power_title = "Power Management"
        self.power_tooltip_menu = "Configure Power Menu"
        self.power_menu_buttons = "Buttons"
        self.power_menu_commands = "Commands"
        self.power_menu_colors = "Colors"
        self.power_menu_show_hide_buttons = "Show/Hide Buttons"
        self.power_menu_shortcuts_tab_label = "Shortcuts"
        self.power_menu_visibility = "Buttons"
        self.power_menu_keyboard_shortcut = "Keyboard Shortcuts"
        self.power_menu_show_keyboard_shortcut = "Show Keyboard Shortcuts"
        self.power_menu_lock = "Lock"
        self.power_menu_logout = "Logout"
        self.power_menu_suspend = "Suspend"
        self.power_menu_hibernate = "Hibernate"
        self.power_menu_reboot = "Reboot"
        self.power_menu_shutdown = "Shutdown"
        self.power_menu_apply = "Apply"
        self.power_menu_tooltip_lock = "Lock the screen"
        self.power_menu_tooltip_logout = "Log out of the current session"
        self.power_menu_tooltip_suspend = "Suspend the system (sleep)"
        self.power_menu_tooltip_hibernate = "Hibernate the system"
        self.power_menu_tooltip_reboot = "Restart the screen"
        self.power_menu_tooltip_shutdown = "Power off the screen"


        # Volume tab translations
        self.volume_title = "Volume Settings"
        self.volume_speakers = "Speakers"
        self.volume_tab_tooltip = "Speakers Settings"
        self.volume_output_device = "Output Device"
        self.volume_device = "Device"
        self.volume_output = "Output"
        self.volume_speaker_volume = "Speaker Volume"
        self.volume_mute_speaker = "Mute Speakers"
        self.volume_unmute_speaker = "Unmute Speakers"
        self.volume_quick_presets = "Quick Presets"
        self.volume_output_combo_tooltip = "Select output device for this application"

        # Volume tab microphone translations
        self.microphone_tab_microphone = "Microphone"
        self.microphone_tab_input_device = "Input Device"
        self.microphone_tab_volume = "Microphone Volume"
        self.microphone_tab_mute_microphone = "Mute Microphone"
        self.microphone_tab_unmute_microphone = "Unmute Microphone"
        self.microphone_tab_tooltip = "Microphone Settings"

        # Volume tab App output translations
        self.app_output_title = "App Output"
        self.app_output_volume = "Application Output Volume"
        self.app_output_mute = "Mute"
        self.app_output_unmute = "Unmute"
        self.app_output_tab_tooltip = "Application Output Settings"
        self.app_output_no_apps = "No applications playing audio"
        self.app_output_dropdown_tooltip = "Select output device for this application"

        # Volume tab App input translations
        self.app_input_title = "App Input"
        self.app_input_volume = "Application Input Volume"
        self.app_input_mute = "Mute Microphone for this application"
        self.app_input_unmute = "Unmute Microphone for this application"
        self.app_input_tab_tooltip = "Application Microphone Settings"
        self.app_input_no_apps = "No applications using microphone"

        # WiFi tab translations
        self.wifi_title = "Wi-Fi Networks"
        self.wifi_refresh_tooltip = "Refresh Networks"
        self.wifi_power = "Wi-Fi"
        self.wifi_speed = "Connection Speed"
        self.wifi_download = "Download"
        self.wifi_upload = "Upload"
        self.wifi_available = "Available Networks"
        self.wifi_forget = "Forget"
        self.wifi_share_title = "Share Network"
        self.wifi_share_scan = "Scan to connect"
        self.wifi_network_name = "Network Name"
        self.wifi_password = "Password"
        self.wifi_loading_networks = "Loading Networks..."

        # Settings tab translations
        self.settings_title = "Settings"
        self.settings_tab_settings = "Tab Settings"
        self.settings_language = "Language"
        self.settings_language_changed_restart = "Please restart the application for the language change to take effect."
        self.settings_language_changed = "Language changed"

class Spanish:
    """Spanish language translation for the application"""
    def __init__(self):
        # app description
        self.msg_desc = "Un elegante panel de control con tema GTK para Linux."
        self.msg_app_url = "https://github.com/quantumvoid0/better-control"
        self.msg_usage = "Uso"

        # for args
        self.msg_args_help = "Muestra este mensaje"
        self.msg_args_autostart = "Inicia con la pestaña de inicio automático abierta"
        self.msg_args_battery = "Inicia con la pestaña de batería abierta"
        self.msg_args_bluetooth = "Inicia con la pestaña de bluetooth abierta"
        self.msg_args_display = "Inicia con la pestaña de pantalla abierta"
        self.msg_args_force = "Fuerza la aplicación a iniciar sin todas las dependencias"
        self.msg_args_power = "Inicia con la pestaña de energía abierta"
        self.msg_args_volume = "Inicia con la pestaña de volumen abierta"
        self.msg_args_volume_v = "También inicia con la pestaña de volumen abierta"
        self.msg_args_wifi = "Inicia con la pestaña de wifi abierta"

        self.msg_args_log = "El programa registrará en un archivo si se proporciona una ruta,\n o mostrará en stdout según el nivel de registro si se da un valor entre 0 y 3."
        self.msg_args_redact = "Oculta información sensible de los registros (nombres de red, IDs de dispositivos, etc.)"
        self.msg_args_size = "Establece un tamaño de ventana personalizado"

        # commonly used
        self.connect = "Conectar"
        self.connected = "Conectado"
        self.connecting = "Conectando..."
        self.disconnect = "Desconectar"
        self.disconnected = "Desconectado"
        self.disconnecting = "Desconectando..."
        self.disable = "Deshabilitar"
        self.enable = "Habilitar"
        self.close = "Cerrar"
        self.show = "Mostrar"
        self.loading = "Cargando..."
        self.loading_tabs = "Cargando pestañas..."

        #for tabs
        self.msg_tab_autostart = "Inicio Automático"
        self.msg_tab_battery = "Batería"
        self.msg_tab_bluetooth = "Bluetooth"
        self.msg_tab_display = "Pantalla"
        self.msg_tab_power = "Energía"
        self.msg_tab_volume = "Volumen"
        self.msg_tab_wifi = "Wi-Fi"

        # Autostart tab translations
        self.autostart_title = "Aplicaciones de Inicio Automático"
        self.autostart_session = "Sesión"
        self.autostart_show_system_apps = "Mostrar aplicaciones del sistema"
        self.autostart_configured_applications = "Aplicaciones Configuradas"
        self.autostart_tooltip_rescan = "Volver a buscar aplicaciones"

        # Battery tab translations
        self.battery_title = "Panel de Batería"
        self.battery_power_saving = "Ahorro de Energía"
        self.battery_balanced = "Equilibrado"
        self.battery_performance = "Rendimiento"
        self.battery_batteries = "Baterías"
        self.battery_overview = "Resumen"
        self.battery_details = "Detalles"
        self.battery_tooltip_refresh = "Actualizar Información de Batería"
        self.battery_no_batteries = "No se detectó ninguna batería"

        # Bluetooth tab translations
        self.bluetooth_title = "Dispositivos Bluetooth"
        self.bluetooth_scan_devices = "Buscar dispositivos"
        self.bluetooth_scanning = "Buscando..."
        self.bluetooth_power = "Bluetooth"
        self.bluetooth_available_devices = "Dispositivos Disponibles"
        self.bluetooth_tooltip_refresh = "Buscar Dispositivos"
        self.bluetooth_connect_failed = "Error al conectar el dispositivo"
        self.bluetooth_disconnect_failed = "Error al desconectar el dispositivo"
        self.bluetooth_try_again = "Por favor, inténtelo de nuevo más tarde."

        # Display tab translations
        self.display_title = "Configuración de Pantalla"
        self.display_brightness = "Brillo de Pantalla"
        self.display_blue_light = "Luz Azul"

        # Power tab translations
        self.power_title = "Gestión de Energía"
        self.power_tooltip_menu = "Configurar Menú de Energía"
        self.power_menu_buttons = "Botones"
        self.power_menu_commands = "Comandos"
        self.power_menu_colors = "Colores"
        self.power_menu_show_hide_buttons = "Mostrar/Ocultar Botones"
        self.power_menu_shortcuts_tab_label = "Atajos"
        self.power_menu_visibility = "Botones"
        self.power_menu_keyboard_shortcut = "Atajos de Teclado"
        self.power_menu_show_keyboard_shortcut = "Mostrar Atajos de Teclado"
        self.power_menu_lock = "Bloquear"
        self.power_menu_logout = "Cerrar Sesión"
        self.power_menu_suspend = "Suspender"
        self.power_menu_hibernate = "Hibernar"
        self.power_menu_reboot = "Reiniciar"
        self.power_menu_shutdown = "Apagar"
        self.power_menu_apply = "Aplicar"
        self.power_menu_tooltip_lock = "Bloquear la pantalla"
        self.power_menu_tooltip_logout = "Cerrar sesión de la sesión actual"
        self.power_menu_tooltip_suspend = "Suspender el sistema (sueño)"
        self.power_menu_tooltip_hibernate = "Hibernar el sistema"
        self.power_menu_tooltip_reboot = "Reiniciar la pantalla"
        self.power_menu_tooltip_shutdown = "Apagar la pantalla"

        # Volume tab translations
        self.volume_title = "Configuración de Volumen"
        self.volume_speakers = "Altavoces"
        self.volume_tab_tooltip = "Configuración de Altavoces"
        self.volume_output_device = "Dispositivo de Salida"
        self.volume_device = "Dispositivo"
        self.volume_output = "Salida"
        self.volume_speaker_volume = "Volumen de Altavoces"
        self.volume_mute_speaker = "Silenciar Altavoces"
        self.volume_unmute_speaker = "Activar Altavoces"
        self.volume_output_combo_tooltip = "Seleccionar dispositivo de salida para esta aplicación"
        self.volume_quick_presets = "Preajustes Rápidos"

        # Volume tab microphone translations
        self.microphone_tab_microphone = "Micrófono"
        self.microphone_tab_input_device = "Dispositivo de Entrada"
        self.microphone_tab_volume = "Volumen de Micrófono"
        self.microphone_tab_mute_microphone = "Silenciar Micrófono"
        self.microphone_tab_unmute_microphone = "Activar Micrófono"
        self.microphone_tab_tooltip = "Configuración de Micrófono"

        # Volume tab App output translations
        self.app_output_title = "Salida de Aplicaciones"
        self.app_output_volume = "Volumen de Salida de Aplicaciones"
        self.app_output_mute = "Silenciar"
        self.app_output_unmute = "Activar"
        self.app_output_tab_tooltip = "Configuración de Salida de Aplicaciones"
        self.app_output_no_apps = "No hay aplicaciones reproduciendo audio"
        self.app_output_dropdown_tooltip = "Seleccionar dispositivo de salida para esta aplicación"

        # Volume tab App input translations
        self.app_input_title = "Entrada de Aplicaciones"
        self.app_input_volume = "Volumen de Entrada de Aplicaciones"
        self.app_input_mute = "Silenciar Micrófono para esta aplicación"
        self.app_input_unmute = "Activar Micrófono para esta aplicación"
        self.app_input_tab_tooltip = "Configuración del Micrófono de Aplicaciones"
        self.app_input_no_apps = "No hay aplicaciones usando el micrófono"

        # WiFi tab translations
        self.wifi_title = "Redes Wi-Fi"
        self.wifi_refresh_tooltip = "Actualizar Redes"
        self.wifi_power = "Wi-Fi"
        self.wifi_speed = "Velocidad de Conexión"
        self.wifi_download = "Descarga"
        self.wifi_upload = "Subida"
        self.wifi_available = "Redes Disponibles"
        self.wifi_forget = "Olvidar"
        self.wifi_share_title = "Compartir Red"
        self.wifi_share_scan = "Escanear para conectar"
        self.wifi_network_name = "Nombre de Red"
        self.wifi_password = "Contraseña"
        self.wifi_loading_networks = "Cargando Redes..."

        # Settings tab translations
        self.settings_title = "Configuraciones"
        self.settings_tab_settings = "Configuraciones de Pestaña"
        self.settings_language = "Idioma"
        self.settings_language_changed_restart = "Por favor reinicie la aplicación para que el cambio de idioma tenga efecto."
        self.settings_language_changed = "Idioma cambiado"

class Portuguese:
    """Portuguese language translation for the application"""
    def __init__(self):
        # app description
        self.msg_desc = "Um elegante painel de controle com tema GTK para Linux."
        self.msg_app_url = "https://github.com/quantumvoid0/better-control"
        self.msg_usage = "Uso"

        # for args
        self.msg_args_help = "Mostra esta mensagem"
        self.msg_args_autostart = "Inicia com a aba de inicialização automática aberta"
        self.msg_args_battery = "Inicia com a aba de bateria aberta"
        self.msg_args_bluetooth = "Inicia com a aba de bluetooth aberta"
        self.msg_args_display = "Inicia com a aba de tela aberta"
        self.msg_args_force = "Força o aplicativo a iniciar sem todas as dependências"
        self.msg_args_power = "Inicia com a aba de energia aberta"
        self.msg_args_volume = "Inicia com a aba de volume aberta"
        self.msg_args_volume_v = "Também inicia com a aba de volume aberta"
        self.msg_args_wifi = "Inicia com a aba de wifi aberta"

        self.msg_args_log = "O programa registrará em um arquivo se fornecido um caminho,\n ou mostrará no stdout com base no nível de registro se fornecido um valor entre 0 e 3."
        self.msg_args_redact = "Oculta informações sensíveis dos registros (nomes de rede, IDs de dispositivos, etc.)"
        self.msg_args_size = "Define um tamanho de janela personalizado"

        # commonly used
        self.connect = "Conectar"
        self.connected = "Conectado"
        self.connecting = "Conectando..."
        self.disconnect = "Desconectar"
        self.disconnected = "Desconectado"
        self.disconnecting = "Desconectando..."
        self.enable = "Ativar"
        self.disable = "Desativar"
        self.close = "Fechar"
        self.show = "Mostrar"
        self.loading = "Carregando..."
        self.loading_tabs = "Carregando abas..."

        # for tabs
        self.msg_tab_autostart = "Inicialização"
        self.msg_tab_battery = "Bateria"
        self.msg_tab_bluetooth = "Bluetooth"
        self.msg_tab_display = "Tela"
        self.msg_tab_power = "Energia"
        self.msg_tab_volume = "Volume"
        self.msg_tab_wifi = "Wi-Fi"

        # Autostart tab translations
        self.autostart_title = "Aplicativos de Inicialização Automática"
        self.autostart_session = "Sessão"
        self.autostart_show_system_apps = "Mostrar aplicativos do sistema"
        self.autostart_configured_applications = "Aplicativos Configurados"
        self.autostart_tooltip_rescan = "Verificar aplicativos novamente"

        # Battery tab translations
        self.battery_title = "Painel da Bateria"
        self.battery_power_saving = "Economia de Energia"
        self.battery_balanced = "Equilibrado"
        self.battery_performance = "Desempenho"
        self.battery_batteries = "Baterias"
        self.battery_overview = "Visão Geral"
        self.battery_details = "Detalhes"
        self.battery_tooltip_refresh = "Atualizar Informações da Bateria"
        self.battery_no_batteries = "Nenhuma bateria detectada"

        # Bluetooth tab translations
        self.bluetooth_title = "Dispositivos Bluetooth"
        self.bluetooth_scan_devices = "Buscar Dispositivos"
        self.bluetooth_scanning = "Buscando..."
        self.bluetooth_power = "Bluetooth"
        self.bluetooth_available_devices = "Dispositivos Disponíveis"
        self.bluetooth_tooltip_refresh = "Buscar Dispositivos"
        self.bluetooth_connect_failed = "Falha ao conectar ao dispositivo"
        self.bluetooth_disconnect_failed = "Falha ao desconectar do dispositivo"
        self.bluetooth_try_again = "Por favor, tente novamente mais tarde."

        # Display tab translations
        self.display_title = "Configurações de Tela"
        self.display_brightness = "Brilho da Tela"
        self.display_blue_light = "Luz Azul"

        # Power tab translations
        self.power_title = "Gerenciamento de Energia"
        self.power_tooltip_menu = "Configurar Menu de Energia"
        self.power_menu_buttons = "Botões"
        self.power_menu_commands = "Comandos"
        self.power_menu_colors = "Cores"
        self.power_menu_show_hide_buttons = "Mostrar/Ocultar Botões"
        self.power_menu_shortcuts_tab_label = "Atalhos"
        self.power_menu_visibility = "Botões"
        self.power_menu_keyboard_shortcut = "Atalhos de Teclado"
        self.power_menu_show_keyboard_shortcut = "Mostrar Atalhos de Teclado"
        self.power_menu_lock = "Bloquear"
        self.power_menu_logout = "Sair"
        self.power_menu_suspend = "Suspender"
        self.power_menu_hibernate = "Hibernar"
        self.power_menu_reboot = "Reiniciar"
        self.power_menu_shutdown = "Desligar"
        self.power_menu_apply = "Aplicar"
        self.power_menu_tooltip_lock = "Bloquear a tela"
        self.power_menu_tooltip_logout = "Sair da sessão atual"
        self.power_menu_tooltip_suspend = "Suspender o sistema (dormir)"
        self.power_menu_tooltip_hibernate = "Hibernar o sistema"
        self.power_menu_tooltip_reboot = "Reiniciar a tela"
        self.power_menu_tooltip_shutdown = "Desligar a tela"

        # Volume tab translations
        self.volume_title = "Configurações de Volume"
        self.volume_speakers = "Alto-falantes"
        self.volume_tab_tooltip = "Configurações de Alto-falantes"
        self.volume_output_device = "Dispositivo de Saída"
        self.volume_device = "Dispositivo"
        self.volume_output = "Saída"
        self.volume_speaker_volume = "Volume dos Alto-falantes"
        self.volume_mute_speaker = "Silenciar Alto-falantes"
        self.volume_unmute_speaker = "Ativar Alto-falantes"
        self.volume_quick_presets = "Predefinições Rápidas"
        self.volume_output_combo_tooltip = "Selecionar dispositivo de saída para este aplicativo"

        # Volume tab microphone translations
        self.microphone_tab_microphone = "Microfone"
        self.microphone_tab_input_device = "Dispositivo de Entrada"
        self.microphone_tab_volume = "Volume do Microfone"
        self.microphone_tab_mute_microphone = "Silenciar Microfone"
        self.microphone_tab_unmute_microphone = "Ativar Microfone"
        self.microphone_tab_tooltip = "Configurações do Microfone"

        # Volume tab App output translations
        self.app_output_title = "Saída de Aplicativos"
        self.app_output_volume = "Volume de Saída de Aplicativos"
        self.app_output_mute = "Silenciar"
        self.app_output_unmute = "Ativar"
        self.app_output_tab_tooltip = "Configurações de Saída de Aplicativos"
        self.app_output_no_apps = "Nenhum aplicativo reproduzindo áudio"
        self.app_output_dropdown_tooltip = "Selecionar dispositivo de saída para este aplicativo"

        # Volume tab App input translations
        self.app_input_title = "Entrada de Aplicativos"
        self.app_input_volume = "Volume de Entrada de Aplicativos"
        self.app_input_mute = "Silenciar Microfone para este aplicativo"
        self.app_input_unmute = "Ativar Microfone para este aplicativo"
        self.app_input_tab_tooltip = "Configurações do Microfone de Aplicativos"
        self.app_input_no_apps = "Nenhum aplicativo usando o microfone"

        # WiFi tab translations
        self.wifi_title = "Redes Wi-Fi"
        self.wifi_refresh_tooltip = "Atualizar Redes"
        self.wifi_power = "Wi-Fi"
        self.wifi_speed = "Velocidade de Conexão"
        self.wifi_download = "Download"
        self.wifi_upload = "Upload"
        self.wifi_available = "Redes Disponíveis"
        self.wifi_forget = "Esquecer"
        self.wifi_share_title = "Compartilhar Rede"
        self.wifi_share_scan = "Escanear para conectar"
        self.wifi_network_name = "Nome da Rede"
        self.wifi_password = "Senha"
        self.wifi_loading_networks = "Carregando Redes..."

        # Settings tab translations
        self.settings_title = "Configurações"
        self.settings_tab_settings = "Configurações de Abas"
        self.settings_language = "Idioma"
        self.settings_language_changed_restart = "Por favor reinicie o aplicativo para que a mudança de idioma tenha efeito."
        self.settings_language_changed = "Idioma alterado"

def get_translations(logging: Logger = None, lang: str = "en") -> English|Spanish|Portuguese:
    """Load the language according to the selected language

    Args:
        lang (str): Language code ('en', 'es', 'pt', 'default')
                   'default' will use the system's $LANG environment variable

    Returns:
        English|Spanish|Portuguese: Translation for the selected language
    """
    # Handle 'default' option by checking system's LANG environment variable
    if lang == "default":
        system_lang = os.environ.get("LANG", "en_US.UTF-8").split("_")[0].lower()
        if logging:
            logging.log(LogLevel.Info, f"Using system language: {system_lang} from $LANG={os.environ.get('LANG', 'not set')}")

        # Map system language code to our supported languages
        if system_lang.startswith("es"):
            lang = "es"
            if logging:
                logging.log(LogLevel.Info, f"System language '{system_lang}' mapped to Spanish (es)")
        elif system_lang.startswith("pt"):
            lang = "pt"
            if logging:
                logging.log(LogLevel.Info, f"System language '{system_lang}' mapped to Portuguese (pt)")
        else:
            # Default to English for unsupported languages
            lang = "en"
            if logging:
                logging.log(LogLevel.Info, f"System language '{system_lang}' not supported, falling back to English (en)")

    if logging:
        logging.log(LogLevel.Info, f"Using language: {lang}")

    if lang == "es":
        return Spanish()
    elif lang == "pt":
        return Portuguese()
    return English()

