import subprocess
import locale

default_coding = locale.getpreferredencoding()
utf = 'utf-8'
console_coding = 'cp866'
print(f"Кодировка системы по умолчанию: {default_coding}")
dns_names = ['yandex.ru', 'youtube.com']
for name in dns_names:
    args = ['ping', name]
    subproc_ping = subprocess.Popen(args, stdout=subprocess.PIPE)
    for line in subproc_ping.stdout:
        line = line.decode(console_coding).encode(utf)
        print(line.decode(utf), end='')
