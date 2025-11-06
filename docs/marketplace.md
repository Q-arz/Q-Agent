## Marketplace Plan

The marketplace enables installing external modules safely.

### Package Format

- Archive containing `module.py` and `module.json` (manifest)
- `module.json` includes: id, name, version, permissions, compatibility, hashes

### Installation Flow

1) Download package and verify checksum/signature
2) Check compatibility (API version)
3) Extract to `modules/<id>/`
4) Register module and refresh dynamic router

### Updates

- Semantic versioning
- Incompatible updates are blocked without explicit approval

### Trust

- Public keys for signed modules
- Source URL allowlist


