Created: 2026 June 24

# solax-modbus — Raspberry Pi Zero 2W Setup

---

## Table of Contents

[1.0 Hardware](<#1.0 hardware>)
[2.0 Operating System](<#2.0 operating system>)
[3.0 Boot Configuration](<#3.0 boot configuration>)
[4.0 solax-modbus Installation](<#4.0 solax-modbus installation>)
[5.0 Development Access](<#5.0 development access>)
[5.1 Hardware](<#5.1 hardware>)
[5.2 Pi Configuration](<#5.2 pi configuration>)
[5.3 Laptop Connection](<#5.3 laptop connection>)
[5.4 Verification](<#5.4 verification>)
[Version History](<#version history>)

---

## 1.0 Hardware

| Component | Specification |
|---|---|
| SBC | Raspberry Pi Zero 2W |
| Role | Headless Modbus TCP client |

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Operating System

**Debian GNU/Linux 12 (Bookworm), 64-bit.**

Use Raspberry Pi Imager to write the image to a microSD card. Select: *Raspberry Pi OS (other)* → *Raspberry Pi OS Lite (64-bit)* — verify the image reports Bookworm before writing.

**Imager settings to configure before writing:**

- Hostname: `solax`
- Enable SSH: yes
- Username / password: as required
- Wi-Fi credentials: as required

**Note:** The boot configuration directory in Bookworm is `/boot/firmware/`, not `/boot/`. All configuration file paths in this document use the Bookworm location.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Boot Configuration

`/boot/firmware/config.txt` — append the following to enable USB OTG device mode.

```ini
# USB OTG — development access
dtoverlay=dwc2
```

**Note:** Do not add `otg_mode=1` under `[cm4]`. That setting enables host mode and disables device mode. It is only applicable to Compute Module 4 hardware.

[Return to Table of Contents](<#table of contents>)

---

## 4.0 solax-modbus Installation

With the Pi booted and accessible, install solax-modbus:

```bash
curl -fsSL https://raw.githubusercontent.com/William12556/solax-modbus/main/bin/install.sh | sudo bash
```

See the project `README.md` for full installation and deployment documentation.

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Development Access

**For development use only.** Not required for normal solax-modbus operation.

The Pi Zero 2W USB OTG port provides a virtual Ethernet connection to a development laptop. This is the recommended method for SSH access when the Pi is deployed at the inverter location, where no network infrastructure may be available.

[Return to Table of Contents](<#table of contents>)

---

### 5.1 Hardware

| Connection | Port |
|---|---|
| Power supply | `PWR IN` (left micro-USB) |
| Laptop | `USB` (right micro-USB, OTG) |

Both ports may be used simultaneously. The `PWR IN` port is power only. The `USB` port carries data and may also supply power from the laptop.

[Return to Table of Contents](<#table of contents>)

---

### 5.2 Pi Configuration

One-time setup. Requires SSH access to the Pi before in-field deployment.

**1. Enable DWC2 overlay**

Append to `/boot/firmware/config.txt` (see [§3.0](<#3.0 boot configuration>)).

**2. Load USB gadget modules**

Append to `/etc/modules`:

```
dwc2
g_ether
```

**3. Reboot**

```bash
sudo reboot
```

**4. Create NetworkManager connection profile**

Bookworm uses NetworkManager. Unlike Bullseye (dhcpcd), `usb0` requires an explicit connection profile to obtain a link-local IPv4 address.

```bash
nmcli connection add type ethernet ifname usb0 con-name usb0 \
  ipv4.method link-local \
  ipv6.method ignore
```

**5. Bring up the interface**

```bash
nmcli connection up usb0
```

This profile persists across reboots. `usb0` activates automatically when a USB host is connected.

[Return to Table of Contents](<#table of contents>)

---

### 5.3 Laptop Connection

Connect a data-capable micro-USB cable to the Pi `USB` (OTG) port. A charge-only cable will not work — the cable must carry data lines.

macOS detects the Pi as a USB Ethernet device. A new network interface appears in System Settings → Network, with a self-assigned link-local address (`169.254.x.x`).

SSH to the Pi by IP address:

```bash
# Obtain Pi IP from: ip -brief a (on Pi)
ssh admin@169.254.x.x
```

Or by hostname if avahi-daemon is running:

```bash
ssh admin@solax.local
```

**Internet access:** The laptop's WiFi connection is unaffected. macOS routes internet traffic over WiFi and Pi traffic over the USB interface independently.

[Return to Table of Contents](<#table of contents>)

---

### 5.4 Verification

```bash
# On Pi — confirm usb0 is up with a link-local address
ip -brief a

# Expected:
# usb0   UP   169.254.x.x/16   fe80::...

# On Mac — confirm reachability
ping -c 3 169.254.x.x
ssh admin@169.254.x.x
```

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 0.1 | 2026-06-24 | Initial draft — hardware, OS, boot configuration, OTG development access for Debian 12 Bookworm |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
