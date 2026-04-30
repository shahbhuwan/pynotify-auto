import os
import pynotify_auto

site_packages = r'C:\Software\Anaconda\envs\downsclae_env\Lib\site-packages'
pth_file = os.path.join(site_packages, 'pynotify-auto.pth')

with open(pth_file, 'w') as f:
    f.write('import sys; exec("try:\\n    import pynotify_auto; pynotify_auto.install_hook()\\nexcept Exception: pass")\n')

print(f"Success: Wrote hook to {pth_file}")
