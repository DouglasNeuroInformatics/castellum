import re
import subprocess
import sys

import polib

REMOVE = {
    '"first_name"',
    '"last_name"',
    '"is_blocked"',
    '"year_of_birth"',
    'Admin',
    'Administrator*in',
    'Administrator*innen',
    'App',
    'Audit',
    'Aufräumfunktion',
    'Batch-Modus',
    'BDSG',
    'Breadcrumbs',
    'Castellum',
    'CSV',
    'Dashboard',
    'DSGVO',
    'Durchführer*innen',
    'Einladungs-Links',
    'Einwilligungs-Revisionen',
    'Encoding',
    'Erinnerungs-E-Mails',
    'Export key',
    'Feeds',
    'FIDO2',
    'Geofilter',
    'GeoJSON',
    'Hash',
    'ID',
    'ISO 8601-Format',
    'jjjj-mm-tt',
    'JSON',
    'Kalender-Feeds',
    'lit.',
    'Lösch-URL',
    'QR-Code',
    'Rekrutierer*in',
    'Rekrutierer*innen',
    'Rekrutierungs-Wiedervorlagen',
    'settings.PRODUCTION',
    'SSH Key',
    'SS:MM',
    'Tab',
    'Tags',
    'Teilnahmestatus',
    'Terminplan-ID',
    'TOTP',
    'UTF-8',
    'UUID',
    'Volljährigkeits-Ablauf-Erinnerung',
}

IGNORE = {
    'kontaktierbar',
    'Merkmalskategorie',
    'Merkmalskategorien',
    'min',
    'Pseudonymlisten',
    'rekrutierbar',
    'Studienteilnahmen',
    'Subtabs',
    'Vertraulichkeitsstufe',
    'Volljährigkeit',
    'Vorgangsbezogene',
    'wiederaufzunehmen',
    'Wiedervorlagetermin',
    'Wiedervorlagezeit',
    'Zuverlässigkeitseintrag',
}


def clean(text):
    for word in sorted(REMOVE, key=lambda s: -len(s)):
        text = text.replace(word, '')
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'%\([^)]+\)s', '', text)
    text = re.sub(r'{[^}]+}', '', text)
    text = text.replace('-', ' ')
    return text


with open('castellum/locale/de/LC_MESSAGES/django.po') as fh:
    lines = [clean(entry.msgstr) for entry in polib.pofile(fh.read())]

proc = subprocess.Popen(
    ['hunspell', '-d', 'de_DE', '-l'],
    stdout=subprocess.PIPE,
    stdin=subprocess.PIPE,
    encoding='utf-8',
)
stdout, _ = proc.communicate(input='\n'.join(lines))
errors = set(stdout.split()) - IGNORE
for error in sorted(errors):
    print(error)
if errors:
    sys.exit(1)
