# Branding: Vom Laster gefallen

A cardboard box tumbling off the back of a truck. Orange like a hi-vis vest,
teal links as the complementary colour.

Everything here is baked into the BookStack image and applied on every
container start, locally and on Railway. Nothing has to be uploaded by hand.

| File | Purpose |
|---|---|
| `apply-branding.php` | Writes colours, name, logo and icons into BookStack's settings. **Edit colours here** |
| `50-apply-branding.sh` | linuxserver `/custom-cont-init.d` hook that runs the PHP file as `abc` |
| `logo-header-500.png` | Header logo (white, transparent), served at `/branding/` |
| `icon-*.png` | Favicon / app icons (32 to 256 px) |
| `*.svg` | Sources. Re-render to PNG with headless Chrome; the wordmark uses Archivo Black |

Because the settings are rewritten on every start, edits to these keys under
Settings > Customization only last until the next restart. Change
`apply-branding.php` and redeploy instead.

## Colours

| Setting | Light | Dark |
|---|---|---|
| Primary (`app-color`) | `#c2410c` | `#ea580c` |
| Links (`link-color`) | `#0e7490` | `#22b8cf` |
| Shelf | `#8a5a2b` | `#c8955f` |
| Book | `#c2410c` | `#f0803c` |
| Chapter | `#a16207` | `#e0a82e` |
| Page | `#0e7490` | `#3cc6db` |
| Draft | `#7c3aed` | `#a78bfa` |
