from afip import Afip

# Certificado (Puede estar guardado en archivos, DB, etc)
cert = open("Ssl/Nacion1846_1b31e8cd3180840d.crt").read()

# Key (Puede estar guardado en archivos, DB, etc)
key = open("Ssl/MiClavePrivada.key").read()

# CUIT del certificado
tax_id = 20172420932

afip = Afip({
    "CUIT": tax_id,
    "cert": cert,
    "key": key,
    "access_token": "TU_ACCESS_TOKEN" # Obtenido de https://app.afipsdk.com
})

print(type(afip))