"""Plugin CLI."""

from __future__ import annotations

import argparse
import importlib
import json

from computronium.plugins.core.registry import registry


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="comp plugin",
        description="Plugin management for custom extensions",
    )
    sub = parser.add_subparsers(
        dest="plugin_command", metavar="<command>", required=True
    )

    # list
    list_p = sub.add_parser("list", help="List installed plugins")
    list_p.add_argument(
        "--type",
        choices=[
            "objective",
            "substrate",
            "dynamics",
            "geometry",
            "credit",
            "update",
            "plasticity",
        ],
        help="Filter by plugin type",
    )
    list_p.add_argument("--format", choices=["text", "json"], default="text")

    # show
    show_p = sub.add_parser("show", help="Show plugin details")
    show_p.add_argument(
        "type",
        choices=[
            "objective",
            "substrate",
            "dynamics",
            "geometry",
            "credit",
            "update",
            "plasticity",
        ],
    )
    show_p.add_argument("name")
    show_p.add_argument("--format", choices=["text", "json"], default="text")

    # reload
    reload_p = sub.add_parser("reload", help="Hot-reload plugins")
    reload_p.add_argument("--watch", action="append", help="Path to watch for changes")

    # validate
    validate_p = sub.add_parser("validate", help="Validate a plugin class")
    validate_p.add_argument("module", help="Module path to plugin class")
    validate_p.add_argument("class_name", help="Class name in module")

    return parser


def _cmd_list(args: argparse.Namespace) -> int:
    plugins = registry.list(args.type)
    metadata = registry.all_metadata(args.type)

    if args.format == "text":
        if not plugins:
            print("No plugins found.")
            return 0
        for key, plugin in plugins.items():
            meta = metadata.get(key)
            display_name = registry.get_display_name(plugin)
            print(f"{args.type}:{display_name}")
            if meta:
                print(f"  Version: {meta.version}")
                print(f"  Description: {meta.description}")
                print(f"  Entry point: {meta.entry_point_name}")
                if meta.author:
                    print(f"  Author: {meta.author}")
            print()
    elif args.format == "json":
        data = {}
        for k, v in plugins.items():
            meta = metadata.get(k)
            data[k] = {
                "plugin_type": k.split(":")[0],
                "name": registry.get_display_name(v),
                "version": meta.version if meta else "",
                "description": meta.description if meta else "",
            }
        print(json.dumps(data, indent=2))
    return 0


def _cmd_show(args: argparse.Namespace) -> int:
    plugin = registry.get(args.type, args.name)
    meta = registry.metadata(args.type, args.name)

    if not plugin:
        print(f"Plugin not found: {args.type}:{args.name}")
        return 1

    display_name = registry.get_display_name(plugin)

    if args.format == "text":
        print(f"Type: {args.type}")
        print(f"Name: {display_name}")
        print(f"Description: {plugin.description}")
        if meta:
            print(f"Version: {meta.version}")
            print(f"Entry point: {meta.entry_point_name}")
            print(f"Module: {meta.module_name}")
            print(f"Class: {meta.class_name}")
            if meta.author:
                print(f"Author: {meta.author}")
            if meta.dependencies:
                print(f"Dependencies: {', '.join(meta.dependencies)}")
    elif args.format == "json":
        data = {
            "type": args.type,
            "name": display_name,
            "description": plugin.description,
            "version": meta.version if meta else "unknown",
            "entry_point": meta.entry_point_name if meta else "unknown",
            "module": meta.module_name if meta else "unknown",
            "class": meta.class_name if meta else "unknown",
        }
        print(json.dumps(data, indent=2))
    return 0


def _cmd_reload(args: argparse.Namespace) -> int:
    from computronium.plugins.core.hotreload import HotReloader

    reloader = HotReloader(args.watch)
    reloaded = reloader.check_and_reload()
    if reloaded:
        print(f"Reloaded: {', '.join(reloaded)}")
    else:
        print("No changes detected.")
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    try:
        module = importlib.import_module(args.module)
        cls = getattr(module, args.class_name)
        instance = cls()
        plugin_type = registry._detect_plugin_type(instance)
        if plugin_type:
            print(f"Valid {plugin_type} plugin: {instance.name}")
            print(f"Description: {instance.description}")
            if hasattr(instance, "requires"):
                print(f"Requires: {instance.requires()}")
        else:
            print("Class does not implement a known plugin protocol")
            return 1
    except Exception as e:
        print(f"Validation failed: {e}")
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.plugin_command == "list":
        return _cmd_list(args)
    elif args.plugin_command == "show":
        return _cmd_show(args)
    elif args.plugin_command == "reload":
        return _cmd_reload(args)
    elif args.plugin_command == "validate":
        return _cmd_validate(args)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
