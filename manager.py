import os

print "Instalando PIP..."
os.system("python get-pip.py")
print "Instalando los requisitos del Club Manager FUT 19"
os.system("python requeriments.txt install")
print "Instalando Club Manager FUT 19"
os.system("python setup.py")


