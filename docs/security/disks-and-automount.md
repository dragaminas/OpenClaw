# Discos y Automontaje

## Objetivo

Evitar que `OpenClaw`, ejecutandose como usuario normal, vea discos que no
forman parte del entorno de trabajo.

## Idea clave

No usar `root` ayuda, pero no basta.

Si un disco esta montado y el usuario de trabajo tiene permisos sobre el punto
de montaje, un proceso lanzado por `OpenClaw` podra leerlo.

## Medidas recomendadas

1. No declarar discos sensibles en `fstab` salvo que exista una necesidad muy clara.
2. No montarlos manualmente durante el uso normal del sistema.
3. Desactivar automontaje y autoapertura de GNOME.
4. Verificar montajes activos antes de poner el sistema en servicio.
5. Ejecutar OpenClaw como usuario no privilegiado.

## GNOME

Los ajustes relevantes son:

```bash
gsettings set org.gnome.desktop.media-handling automount false
gsettings set org.gnome.desktop.media-handling automount-open false
```

Verificacion:

```bash
gsettings get org.gnome.desktop.media-handling automount
gsettings get org.gnome.desktop.media-handling automount-open
```

Ambos valores deben devolver `false`.

## Scripts del repo

- `scripts/hardening/check-mounts.sh`
- `scripts/hardening/disable-gnome-automount.sh`
- `scripts/bootstrap/apply-workstation.sh`

## Variables relacionadas

- `DISABLE_GNOME_AUTOMOUNT`
- `VERIFY_INTERNAL_NVME_UNMOUNTED`
- `CHECK_DANGEROUS_GROUPS`

## Validacion manual

1. Conectar el disco.
2. Confirmar que GNOME no lo monta automaticamente.
3. Ejecutar `scripts/hardening/check-mounts.sh`.
4. Verificar que no aparezca ninguna particion sensible montada.
