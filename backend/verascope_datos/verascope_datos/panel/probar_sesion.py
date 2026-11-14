"""Comprueba que el usuario y la contraseña de NASA Earthdata funcionan (lo usa el botón «Probar mi cuenta» del panel)."""
import sys

from ..fuentes import earthdata


def main():
    try:
        earthdata.iniciar_sesion()
    except Exception as e:
        print(f"✘ {e}")
        return 1
    print("✔ Tu cuenta de NASA Earthdata funciona. Ya puedes bajar las variables de satélite (V8–V12).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
