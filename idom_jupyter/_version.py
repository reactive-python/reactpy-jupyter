# Module version
version_info = 0, 7, 7, "final", 0

major, minor, patch, stage_name, stage_num = version_info
stage_name = {"alpha": "a", "beta": "b", "candidate": "rc", "final": ""}[stage_name]
stage = f'{stage_name}{stage_num}' if stage_name else ''

# Module version accessible using idom_jupyter.__version__
__version__ = f"{major}.{minor}.{patch}{stage}"
