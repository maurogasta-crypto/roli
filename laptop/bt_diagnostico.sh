#!/bin/bash
# Junta datos del Bluetooth de la laptop en ~/Roli/bt_diagnostico.txt
# Uso:  bash bt_diagnostico.sh      (pide la clave de administrador una vez)
OUT="$HOME/Roli/bt_diagnostico.txt"
mkdir -p "$HOME/Roli"
{
echo "=== Fecha ==="; date
echo; echo "=== Kernel ==="; uname -r
echo; echo "=== Adaptador (USB) ==="; lsusb | grep -i -E "bluetooth|realtek|mediatek|intel|qualcomm|broadcom|csr"
echo; echo "=== Red/Bluetooth (PCI) ==="; lspci -nn 2>/dev/null | grep -i -E "network|wireless"
echo; echo "=== rfkill ==="; rfkill list
echo; echo "=== bluetoothctl show ==="; bluetoothctl show 2>&1 | head -25
echo; echo "=== Servicio bluetooth ==="; systemctl status bluetooth --no-pager 2>&1 | head -15
echo; echo "=== btusb autosuspend (Y = puede apagarse solo) ==="; cat /sys/module/btusb/parameters/enable_autosuspend 2>&1
echo; echo "=== Energia de dispositivos USB tipo Bluetooth (auto = puede apagarse) ==="
for d in /sys/bus/usb/devices/*; do
  if [ "$(cat "$d/bDeviceClass" 2>/dev/null)" = "e0" ]; then
    echo "$d  $(cat "$d/product" 2>/dev/null)  control=$(cat "$d/power/control" 2>/dev/null)"
  fi
done
echo; echo "=== TLP / gestores de energia ==="; systemctl is-active tlp 2>&1; systemctl is-active power-profiles-daemon 2>&1
echo; echo "=== Registro de bluetooth (ultimo arranque) ==="; journalctl -u bluetooth -b --no-pager 2>&1 | tail -60
echo; echo "=== Mensajes del nucleo sobre Bluetooth/USB ==="
sudo dmesg 2>&1 | grep -i -E "bluetooth|btusb|hci0|firmware|rtl|usb.*(disconnect|reset|error)|xhci" | tail -80
} > "$OUT" 2>&1
echo "Listo: $OUT"
echo "Pasame el contenido de ese archivo."
