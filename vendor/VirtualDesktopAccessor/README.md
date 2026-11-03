# VirtualDesktopAccessor

Upstream: https://github.com/Ciantic/VirtualDesktopAccessor

Pinned release: `2024-12-16-windows11` (Windows x64).

Binary SHA-256: `8740C572A1C000E3B87FFEB1E4C397EAE9AF3BD4A2ABDC3BCFFACAB4493F8FF5`.

Run `scripts/setup-razer-app.ps1` to fetch and verify the binary. The DLL is
ignored by Git; its upstream MIT license is included here and copied into builds.
No DLL is loaded into other processes. Only the desktop enumeration/current/switch
exports are used. The internal shell API can change after Windows updates; verify
the adapter against the target Windows build when updating this dependency.
