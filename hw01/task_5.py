import subprocess
import locale
import platform
from chardet import detect
default_coding = locale.getpreferredencoding()
utf = 'utf-8'
print(f"Кодировка системы по умолчанию: {default_coding}")
dns_names = ['yandex.ru', 'youtube.com']
code = '-n' if platform.system().lower() == 'windows' else '-c'
for name in dns_names:
    args = ['ping', code, '2', name]
    subproc_ping = subprocess.Popen(args, stdout=subprocess.PIPE)
    for line in subproc_ping.stdout:
        var = detect(line)
        line = line.decode(var['encoding']).encode(utf)
        print(line.decode(utf), end='')
