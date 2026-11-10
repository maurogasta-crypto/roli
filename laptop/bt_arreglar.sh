#!/bin/bash
# Evita que la laptop apague sola el Bluetooth. Es reversible (se guardan copias).
# Uso:  sudo bash bt_arreglar.sh      y despues REINICIA la laptop.
set -e
if [ "$EUID" -ne 0 ]; then echo "Ejecutalo con sudo:  sudo bash bt_arreglar.sh"; exit 1; fi
COPIA=/root/bt_roli_copias; mkdir -p "$COPIA"

# 1) El modulo btusb no se suspende por ahorro de energia
echo "options btusb enable_autosuspend=n" > /etc/modprobe.d/btusb-roli.conf
echo "[1] btusb sin autosuspend: /etc/modprobe.d/btusb-roli.conf"

# 2) Los adaptadores Bluetooth USB quedan siempre con energia
cat > /etc/udev/rules.d/50-bluetooth-roli.rules <<'RULE'
ACTION=="add|change", SUBSYSTEM=="usb", ATTR{bDeviceClass}=="e0", TEST=="power/control", ATTR{power/control}="on"
RULE
echo "[2] Energia siempre encendida para el adaptador: /etc/udev/rules.d/50-bluetooth-roli.rules"

# 3) El Bluetooth arranca encendido
if [ -f /etc/bluetooth/main.conf ]; then
  cp -n /etc/bluetooth/main.conf "$COPIA/main.conf.orig"
  if grep -q -E "^\s*#?\s*AutoEnable" /etc/bluetooth/main.conf; then
    sed -i -E 's/^\s*#?\s*AutoEnable.*/AutoEnable=true/' /etc/bluetooth/main.conf
  else
    sed -i '/^\[Policy\]/a AutoEnable=true' /etc/bluetooth/main.conf || true
  fi
  echo "[3] AutoEnable=true en /etc/bluetooth/main.conf (copia en $COPIA)"
fi

# 4) Aviso si hay TLP
if systemctl is-active --quiet tlp; then
  echo "[!] TLP esta activo. Agrega en /etc/tlp.conf:  USB_AUTOSUSPEND=0   y corre: sudo tlp start"
fi

udevadm control --reload-rules
echo
echo "Listo. REINICIA la laptop ahora (no reinicies servicios a mano)."
echo "Para deshacer: sudo rm /etc/modprobe.d/btusb-roli.conf /etc/udev/rules.d/50-bluetooth-roli.rules"
echo "y restaura $COPIA/main.conf.orig en /etc/bluetooth/main.conf"
