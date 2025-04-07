"""
Adding new languages for better user preferences

To add a new language, create a new class that inherits from the Translation base class
and update the get_translations function to include the new language.
The class should contain all the translations for the new language.

Usage in tab files:
    from utils.translations import Translation

    class SomeTab(Gtk.Box):
        def __init__(self, logging: Logger, txt: Translation):
            # Use txt for translations
"""

import os
from logging import Logger
from typing import Protocol

from utils.logger import LogLevel


class Translation(Protocol):
    """Base protocol for all translations in the application.

    This provides type hints without needing to import all language classes.
    All language classes should implement these properties and methods.
    """
    # Common properties that all translations must have
    msg_desc: str
    msg_app_url: str
    msg_usage: str

    # Tab names
    msg_tab_volume: str
    msg_tab_wifi: str
    msg_tab_bluetooth: str
    msg_tab_battery: str
    msg_tab_display: str
    msg_tab_power: str
    msg_tab_autostart: str
    msg_tab_usbguard: str

    # Common UI elements
    loading: str
    loading_tabs: str
    close: str
    enable: str
    disable: str


class English:
    """English language translation for the application"""
    def __init__(self):
        # app description
        self.msg_desc = "A sleek GTK-themed control panel for Linux."
        
        # USB notifications
        self.usb_connected = "{device} connected."
        self.usb_disconnected = "{device} disconnected." 
        self.permission_allowed = "USB permission granted"
        self.permission_blocked = "USB permission blocked"
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
        self.msg_tab_usbguard = "USBGuard"
        self.usbguard_title = "USB Device Control"
        self.refresh = "Refresh"
        self.allow = "Allow"
        self.block = "Block"
        self.allowed = "Allowed"
        self.blocked = "Blocked"
        self.rejected = "Rejected"
        self.policy = "View Policy"
        self.usbguard_error = "Error accessing USBGuard"
        self.usbguard_not_installed = "USBGuard not installed"
        self.usbguard_not_running = "USBGuard service not running"
        self.no_devices = "No USB devices connected"
        self.operation_failed = "Operation failed"
        self.policy_error = "Failed to load policy"
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
        self.msg_tab_usbguard = "USBGuard"
        self.usbguard_title = "Control de Dispositivos USB"
        self.refresh = "Actualizar"
        self.allow = "Permitir"
        self.block = "Bloquear"
        self.policy = "Ver Política"
        self.usbguard_error = "Error al acceder a USBGuard"
        self.usbguard_not_installed = "USBGuard no está instalado"
        self.usbguard_not_running = "Servicio USBGuard no está en ejecución"
        self.no_devices = "No hay dispositivos USB conectados"
        self.operation_failed = "Operación fallida"
        self.policy_error = "Error al cargar la política"
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
        self.msg_tab_usbguard = "USBGuard"
        self.usbguard_title = "Controle de Dispositivos USB"
        self.refresh = "Atualizar"
        self.allow = "Permitir"
        self.block = "Bloquear"
        self.policy = "Ver Política"
        self.usbguard_error = "Erro ao acessar USBGuard"
        self.usbguard_not_installed = "USBGuard não instalado"
        self.usbguard_not_running = "Serviço USBGuard não está em execução"
        self.no_devices = "Nenhum dispositivo USB conectado"
        self.operation_failed = "Operação falhou"
        self.policy_error = "Falha ao carregar política"
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

class French:
    """French language translation for the application"""
    def __init__(self):
        # app description
        self.msg_desc = "Un panneau de contrôle élégant avec thème GTK pour Linux."
        self.msg_app_url = "https://github.com/quantumvoid0/better-control"
        self.msg_usage = "Utilisation"

        # for args
        self.msg_args_help = "Affiche ce message"
        self.msg_args_autostart = "Démarre avec l'onglet de démarrage automatique ouvert"
        self.msg_args_battery = "Démarre avec l'onglet de batterie ouvert"
        self.msg_args_bluetooth = "Démarre avec l'onglet bluetooth ouvert"
        self.msg_args_display = "Démarre avec l'onglet d'affichage ouvert"
        self.msg_args_force = "Force l'application à démarrer sans toutes les dépendances"
        self.msg_args_power = "Démarre avec l'onglet d'alimentation ouvert"
        self.msg_args_volume = "Démarre avec l'onglet de volume ouvert"
        self.msg_args_volume_v = "Démarre également avec l'onglet de volume ouvert"
        self.msg_args_wifi = "Démarre avec l'onglet Wi-Fi ouvert"

        self.msg_args_log = "Le programme enregistrera dans un fichier si un chemin est fourni,\n ou affichera sur stdout selon le niveau de journalisation si une valeur entre 0 et 3 est donnée."
        self.msg_args_redact = "Masque les informations sensibles des journaux (noms de réseau, identifiants d'appareils, etc.)"
        self.msg_args_size = "Définit une taille de fenêtre personnalisée"

        # commonly used
        self.connect = "Connecter"
        self.connected = "Connecté"
        self.connecting = "Connexion..."
        self.disconnect = "Déconnecter"
        self.disconnected = "Déconnecté"
        self.disconnecting = "Déconnexion..."
        self.enable = "Activer"
        self.disable = "Désactiver"
        self.close = "Fermer"
        self.show = "Afficher"
        self.loading = "Chargement..."
        self.loading_tabs = "Chargement des onglets..."

        # for tabs
        self.msg_tab_autostart = "Démarrage Auto"
        self.msg_tab_usbguard = "USBGuard"
        self.usbguard_title = "Contrôle des Périphériques USB"
        self.refresh = "Actualiser"
        self.allow = "Autoriser"
        self.block = "Bloquer"
        self.policy = "Voir la Politique"
        self.usbguard_error = "Erreur d'accès à USBGuard"
        self.usbguard_not_installed = "USBGuard non installé"
        self.usbguard_not_running = "Service USBGuard non démarré"
        self.no_devices = "Aucun périphérique USB connecté"
        self.operation_failed = "Échec de l'opération"
        self.policy_error = "Échec du chargement de la politique"
        self.msg_tab_battery = "Batterie"
        self.msg_tab_bluetooth = "Bluetooth"
        self.msg_tab_display = "Affichage"
        self.msg_tab_power = "Alimentation"
        self.msg_tab_volume = "Volume"
        self.msg_tab_wifi = "Wi-Fi"

        # Autostart tab translations
        self.autostart_title = "Applications au Démarrage"
        self.autostart_session = "Session"
        self.autostart_show_system_apps = "Afficher les applications système"
        self.autostart_configured_applications = "Applications Configurées"
        self.autostart_tooltip_rescan = "Rescanner les applications"

        # Battery tab translations
        self.battery_title = "Tableau de Bord de la Batterie"
        self.battery_power_saving = "Économie d'Énergie"
        self.battery_balanced = "Équilibré"
        self.battery_performance = "Performance"
        self.battery_batteries = "Batteries"
        self.battery_overview = "Aperçu"
        self.battery_details = "Détails"
        self.battery_tooltip_refresh = "Actualiser les Informations de la Batterie"
        self.battery_no_batteries = "Aucune batterie détectée"

        # Bluetooth tab translations
        self.bluetooth_title = "Appareils Bluetooth"
        self.bluetooth_scan_devices = "Rechercher des Appareils"
        self.bluetooth_scanning = "Recherche..."
        self.bluetooth_power = "Bluetooth"
        self.bluetooth_available_devices = "Appareils Disponibles"
        self.bluetooth_tooltip_refresh = "Rechercher des Appareils"
        self.bluetooth_connect_failed = "Échec de la connexion à l'appareil"
        self.bluetooth_disconnect_failed = "Échec de la déconnexion de l'appareil"
        self.bluetooth_try_again = "Veuillez réessayer plus tard."

        # Display tab translations
        self.display_title = "Paramètres d'Affichage"
        self.display_brightness = "Luminosité de l'Écran"
        self.display_blue_light = "Lumière Bleue"

        # Power tab translations
        self.power_title = "Gestion de l'Alimentation"
        self.power_tooltip_menu = "Configurer le Menu d'Alimentation"
        self.power_menu_buttons = "Boutons"
        self.power_menu_commands = "Commandes"
        self.power_menu_colors = "Couleurs"
        self.power_menu_show_hide_buttons = "Afficher/Masquer les Boutons"
        self.power_menu_shortcuts_tab_label = "Raccourcis"
        self.power_menu_visibility = "Boutons"
        self.power_menu_keyboard_shortcut = "Raccourcis Clavier"
        self.power_menu_show_keyboard_shortcut = "Afficher les Raccourcis Clavier"
        self.power_menu_lock = "Verrouiller"
        self.power_menu_logout = "Déconnexion"
        self.power_menu_suspend = "Mettre en Veille"
        self.power_menu_hibernate = "Hiberner"
        self.power_menu_reboot = "Redémarrer"
        self.power_menu_shutdown = "Éteindre"
        self.power_menu_apply = "Appliquer"
        self.power_menu_tooltip_lock = "Verrouiller l'écran"
        self.power_menu_tooltip_logout = "Se déconnecter de la session actuelle"
        self.power_menu_tooltip_suspend = "Mettre le système en veille"
        self.power_menu_tooltip_hibernate = "Hiberner le système"
        self.power_menu_tooltip_reboot = "Redémarrer l'écran"
        self.power_menu_tooltip_shutdown = "Éteindre l'écran"

        # Volume tab translations
        self.volume_title = "Paramètres de Volume"
        self.volume_speakers = "Haut-parleurs"
        self.volume_tab_tooltip = "Paramètres des Haut-parleurs"
        self.volume_output_device = "Périphérique de Sortie"
        self.volume_device = "Périphérique"
        self.volume_output = "Sortie"
        self.volume_speaker_volume = "Volume des Haut-parleurs"
        self.volume_mute_speaker = "Couper les Haut-parleurs"
        self.volume_unmute_speaker = "Activer les Haut-parleurs"
        self.volume_quick_presets = "Préréglages Rapides"
        self.volume_output_combo_tooltip = "Sélectionner le périphérique de sortie pour cette application"

        # Volume tab microphone translations
        self.microphone_tab_microphone = "Microphone"
        self.microphone_tab_input_device = "Périphérique d'Entrée"
        self.microphone_tab_volume = "Volume du Microphone"
        self.microphone_tab_mute_microphone = "Couper le Microphone"
        self.microphone_tab_unmute_microphone = "Activer le Microphone"
        self.microphone_tab_tooltip = "Paramètres du Microphone"

        # Volume tab App output translations
        self.app_output_title = "Sortie d'Applications"
        self.app_output_volume = "Volume de Sortie d'Applications"
        self.app_output_mute = "Couper"
        self.app_output_unmute = "Activer"
        self.app_output_tab_tooltip = "Paramètres de Sortie d'Applications"
        self.app_output_no_apps = "Aucune application ne joue de l'audio"
        self.app_output_dropdown_tooltip = "Sélectionner le périphérique de sortie pour cette application"

        # Volume tab App input translations
        self.app_input_title = "Entrée d'Applications"
        self.app_input_volume = "Volume d'Entrée d'Applications"
        self.app_input_mute = "Couper le Microphone pour cette application"
        self.app_input_unmute = "Activer le Microphone pour cette application"
        self.app_input_tab_tooltip = "Paramètres du Microphone d'Applications"
        self.app_input_no_apps = "Aucune application n'utilise le microphone"

        # WiFi tab translations
        self.wifi_title = "Réseaux Wi-Fi"
        self.wifi_refresh_tooltip = "Actualiser les Réseaux"
        self.wifi_power = "Wi-Fi"
        self.wifi_speed = "Vitesse de Connexion"
        self.wifi_download = "Téléchargement"
        self.wifi_upload = "Envoi"
        self.wifi_available = "Réseaux Disponibles"
        self.wifi_forget = "Oublier"
        self.wifi_share_title = "Partager le Réseau"
        self.wifi_share_scan = "Scanner pour se connecter"
        self.wifi_network_name = "Nom du Réseau"
        self.wifi_password = "Mot de passe"
        self.wifi_loading_networks = "Chargement des Réseaux..."

        # Settings tab translations
        self.settings_title = "Paramètres"
        self.settings_tab_settings = "Paramètres des Onglets"
        self.settings_language = "Langue"
        self.settings_language_changed_restart = "Veuillez redémarrer l'application pour que le changement de langue prenne effet."
        self.settings_language_changed = "Langue modifiée"

class Indonesian:
    """English language translation for the application"""
    def __init__(self):
        # app description
        self.msg_desc = "Panel kontrol GTK yang unik untuk Linux"
        self.msg_app_url = "https://github.com/quantumvoid0/better-control"
        self.msg_usage = "Penggunaan"

        # for args
        self.msg_args_help = "Mencetak pesan ini"
        self.msg_args_autostart = "Memulai aplikasi dengan tab Autostart terbuka"
        self.msg_args_battery = "Memulai aplikasi dengan tab Baterai terbuka"
        self.msg_args_bluetooth = "Memulai aplikasi dengan tab Blueetooth terbuka"
        self.msg_args_display = "Memulai aplikasi the tab Tampilan terbuka"
        self.msg_args_force = "Memaksa aplikasi untuk mengecek semua ketergantungan"
        self.msg_args_power = "Memulai aplikasi dengan tab Power terbuka"
        self.msg_args_volume = "Memulai aplikasi dengan tab Volume terbuka"
        self.msg_args_volume_v = "Juga memulai aplikasit dengan tab Volume terbuka"
        self.msg_args_wifi = "Memulai aplikasi dengan tab WiFI terbuka"

        self.msg_args_log = "Aplikasi akan mengeluarkan log ke sebuah file jika diberi sebuah file path,\n atau mengeluarkan output ke stdout jika diberikan nilai antara 0, dan 3."
        self.msg_args_redact = "Menyunting informasi sensitif dari log. (nama jaringan, ID perankat, dst.)"
        self.msg_args_size = "Menetapkan ukuran Window kustom"

        # commonly used
        self.connect = "Sambungkan"
        self.connected = "Tersambung"
        self.connecting = "Manyambungkan..."
        self.disconnect = "Putuskan sambungan"
        self.disconnected = "Tidak tersambung"
        self.disconnecting = "Memutuskan sambungan..."
        self.enable = "Aktifan"
        self.disable = "Nonaktifkan"
        self.close = "Tutup"
        self.show = "Tampilkan"
        self.loading = "Memuat..."
        self.loading_tabs = "Memuat tab..."

        # for tabs
        self.msg_tab_autostart = "Autostart"
        self.msg_tab_usbguard = "USBGuard"
        self.usbguard_title = "USB Device Control"
        self.refresh = "Perbarui"
        self.allow = "Izinkan"
        self.block = "Blokir"
        self.policy = "Lihat kebijakan"
        self.usbguard_error = "Error mengakses USBGuard"
        self.usbguard_not_installed = "USBGuard tidak terinstall"
        self.usbguard_not_running = "layanan USBGuard tidak berjalan"
        self.no_devices = "Tidak ada USB yang tersambung"
        self.operation_failed = "Operasi gagal"
        self.policy_error = "Gagal memuat kebijakan"
        self.msg_tab_battery = "Baterai"
        self.msg_tab_bluetooth = "Bluetooth"
        self.msg_tab_display = "Tampilan"
        self.msg_tab_power = "Power"
        self.msg_tab_volume = "Volume"
        self.msg_tab_wifi = "Wi-Fi"

        # Autostart tab translations
        self.autostart_title = "Aplikasi Autostart"
        self.autostart_session = "Sesi"
        self.autostart_show_system_apps = "Tunjukan aplikasi autostart sistem"
        self.autostart_configured_applications = "Aplikasi terkonfigurasi"
        self.autostart_tooltip_rescan = "Pindai ulang aplikasi autostart"

        # Battery tab translations
        self.battery_title = "Dasbor Baterai"
        self.battery_power_saving = "Hemat Daya"
        self.battery_balanced = "Seimbang"
        self.battery_performance = "Performa"
        self.battery_batteries = "Baterai"
        self.battery_overview = "Gambaran Umum"
        self.battery_details = "Detail"
        self.battery_tooltip_refresh = "Pindai ulang informasi baterai"
        self.battery_no_batteries = "Tidak ada baterai yang terdeteksi"

        # Bluetooth tab translations
        self.bluetooth_title = "Perangkat Bluetooth"
        self.bluetooth_scan_devices = "Pindai perangkat"
        self.bluetooth_scanning = "Memindai..."
        self.bluetooth_power = "Bluetooth"
        self.bluetooth_available_devices = "Perangkat yang tersedia"
        self.bluetooth_tooltip_refresh = "Pindai perangkat"
        self.bluetooth_connect_failed = "Gagal untuk menyambung ke perangkat"
        self.bluetooth_disconnect_failed = "Gagal untuk memutus sambungan ke perangkat"
        self.bluetooth_try_again = "Mohon coba lagi."

        # Display tab translations
        self.display_title = "Pengaturan Tampilan"
        self.display_brightness = "Kecerahan Layar"
        self.display_blue_light = "Anti Radiasi"

        # Power tab translations
        self.power_title = "Pengelolaan Daya"
        self.power_tooltip_menu = "Konfigurasi Menu Daya"
        self.power_menu_buttons = "Tombol"
        self.power_menu_commands = "Perintah"
        self.power_menu_colors = "Warna"
        self.power_menu_show_hide_buttons = "Tunjukkan/Sembunyikan Tombol"
        self.power_menu_shortcuts_tab_label = "Pintasan"
        self.power_menu_visibility = "Tombol"
        self.power_menu_keyboard_shortcut = "Pintasan Keyboard"
        self.power_menu_show_keyboard_shortcut = "Tunjukkan Pintasan Keyboard"
        self.power_menu_lock = "Kunci"
        self.power_menu_logout = "Logout"
        self.power_menu_suspend = "Tidur"
        self.power_menu_hibernate = "Hibernasi"
        self.power_menu_reboot = "Reboot"
        self.power_menu_shutdown = "Matikan"
        self.power_menu_apply = "Terapkan"
        self.power_menu_tooltip_lock = "Kunci layar"
        self.power_menu_tooltip_logout = "Keluar dari sesi saat ini"
        self.power_menu_tooltip_suspend = "Menidurkan sistem"
        self.power_menu_tooltip_hibernate = "Menghibernasikan sistem"
        self.power_menu_tooltip_reboot = "Merestart sistem"
        self.power_menu_tooltip_shutdown = "Mematikan perangkat"


        # Volume tab translations
        self.volume_title = "Pengaturan Volume"
        self.volume_speakers = "Speaker"
        self.volume_tab_tooltip = "Pengatures Speaker"
        self.volume_output_device = "Perangkat Output"
        self.volume_device = "Perangkat"
        self.volume_output = "Output"
        self.volume_speaker_volume = "Volume Speaker"
        self.volume_mute_speaker = "Bisukan Speaker"
        self.volume_unmute_speaker = "Menyalakan Speakers"
        self.volume_quick_presets = "Preset Cepat"
        self.volume_output_combo_tooltip = "Piling perangkat output untuk aplikasi ini"

        # Volume tab microphone translations
        self.microphone_tab_microphone = "Mikrofon"
        self.microphone_tab_input_device = "Perangkat Input"
        self.microphone_tab_volume = "Volume Mikrofon"
        self.microphone_tab_mute_microphone = "Bisukan Mikrofon"
        self.microphone_tab_unmute_microphone = "Nyalakn Microphone"
        self.microphone_tab_tooltip = "Pengaturan Mikrofon"

        # Volume tab App output translations
        self.app_output_title = "Output Aplikasi"
        self.app_output_volume = "Volume Output Aplikasi"
        self.app_output_mute = "Bisukan"
        self.app_output_unmute = "Nyalakan"
        self.app_output_tab_tooltip = "Pengaturan Output Aplikasi"
        self.app_output_no_apps = "Tidak ada aplikasi yang mengeluarkan suara"
        self.app_output_dropdown_tooltip = "Pilih perangkat output untuk aplikasi ini"

        # Volume tab App input translations
        self.app_input_title = "Input aplikasi"
        self.app_input_volume = "Volume Input Aplikasi"
        self.app_input_mute = "Bisukan Mikrofon untuk aplikasi ini"
        self.app_input_unmute = "Nyalakan Mikrofon untuk aplikasi ini"
        self.app_input_tab_tooltip = "Pengaturan Mikrofon Aplikasi"
        self.app_input_no_apps = "Tidak ada aplikasi yang menggunakan mikrofon"

        # WiFi tab translations
        self.wifi_title = "Jaringan Wi-Fi"
        self.wifi_refresh_tooltip = "Pindai Ulang Jaringan"
        self.wifi_power = "Wi-Fi"
        self.wifi_speed = "Kecepatan Koneksi"
        self.wifi_download = "Download"
        self.wifi_upload = "Upload"
        self.wifi_available = "Jaringan yang Tersedia"
        self.wifi_forget = "Lupakan"
        self.wifi_share_title = "Bagikan Jaringan"
        self.wifi_share_scan = "Pindai untuk menyambungkan"
        self.wifi_network_name = "Nama Jaringan"
        self.wifi_password = "Password"
        self.wifi_loading_networks = "Memuat Networks..."

        # Settings tab translations
        self.settings_title = "Pengaturan"
        self.settings_tab_settings = "Pengaturan Tab"
        self.settings_language = "Bahasa"
        self.settings_language_changed_restart = "Mulai ulang aplikasi agar perubahan bahasa diterapkan."
        self.settings_language_changed = "Bahasa telah diubah"

def get_translations(logging: Logger = None, lang: str = "en") -> Translation:
    """Load the language according to the selected language

    Args:
        lang (str): Language code ('en', 'es', 'pt', 'fr', 'id', 'default')
                   'default' will use the system's $LANG environment variable

    Returns:
        English|Spanish|Portuguese|French: Translation for the selected language
    """
    # Handle 'default' option by checking system's LANG environment variable
    if lang == "default":
        system_lang = os.environ.get("LANG").split("_")[0].lower()
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
        elif system_lang.startswith("fr"):
            lang = "fr"
            if logging:
                logging.log(LogLevel.Info, f"System language '{system_lang}' mapped to French (fr)")
        elif system_lang.startswith("id"):
            lang = "id"
            if logging:
                logging.log(LogLevel.Info, f"System language '{system_lang}' mapped to Indonesian (id)")
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
    elif lang == "fr":
        return French()
    elif lang == "id":
        return Indonesian()
    return English()

