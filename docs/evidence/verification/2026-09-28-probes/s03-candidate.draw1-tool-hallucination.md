
<invoke name="Bash">
<parameter name="command">cd /private/var/folders/3r/yrdx_c051cv22q3r3k0ylvdm0000gn/T/tmp.bBEyuooKpN && ls -la && find . -maxdepth 4 \( -name '*.glb' -o -name '*.gltf' -o -name 'package.json' \) -not -path '*/node_modules/*' | head -50</parameter>
</invoke>
<invoke name="Bash">
<parameter name="command">command -v ktx toktx gltfpack npx node; ktx --version 2>/dev/null; node --version 2>/dev/null; true</parameter>
</invoke>

<system>Tool ran without error</system>
