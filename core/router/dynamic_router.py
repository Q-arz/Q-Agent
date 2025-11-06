import os

dynamic_commands = []
dynamic_manifests = []

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
modules_path = os.path.join(project_root, "modules")


def load_all_modules():
    import os
    import importlib.util

    print(f"[Router] Explorando carpeta de módulos: {modules_path}")

    if not os.path.isdir(modules_path):
        print(f"[Router] Carpeta de módulos no encontrada: {modules_path}")
        return

    for folder in os.listdir(modules_path):
        mod_file = os.path.join(modules_path, folder, "module.py")
        if os.path.exists(mod_file):
            print(f"[Router] Cargando módulo: {folder}")
            try:
                spec = importlib.util.spec_from_file_location(
                    f"{folder}_module", mod_file
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Prefer manifest-based API
                if hasattr(module, "get_manifest"):
                    manifest = module.get_manifest()
                    if isinstance(manifest, dict):
                        manifest = dict(manifest)
                        manifest["_module_path"] = os.path.join(modules_path, folder)
                        dynamic_manifests.append(manifest)
                        cmds = manifest.get("commands", [])
                        if isinstance(cmds, list):
                            # normalize into trigger/function for router
                            for c in cmds:
                                trigger = c.get("trigger")
                                handler = c.get("handler")
                                if trigger and callable(handler):
                                    dynamic_commands.append({"trigger": trigger, "function": handler, "_manifest": manifest})
                        print(f"[Router] Manifest '{manifest.get('id', folder)}' loaded with {len(cmds)} commands.")
                    else:
                        print(f"[Router] get_manifest() in {folder} did not return a dict.")
                elif hasattr(module, "get_commands"):
                    cmds = module.get_commands()
                    if isinstance(cmds, list):
                        dynamic_commands.extend(cmds)
                        print(f"[Router] Legacy module '{folder}' loaded with {len(cmds)} commands.")
                    else:
                        print(f"[Router] 'get_commands' in {folder} did not return a list.")
                else:
                    print(f"[Router] Module '{folder}' has no manifest or commands.")
            except Exception as e:
                print(f"[Router] Error al cargar módulo '{folder}': {e}")
