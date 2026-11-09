"""Publish one winter-campaign page from a JSON spec.

Usage: python3 tools/publish.py content/invierno/<spec>.json

Spec "zona":     kind, zone, slug, title, desc, lead, body_html, barrios, faqs
Spec "articulo": kind, slug, title, headline, short, desc, eyebrow, lead, wa_text, body_html, faqs, summary
Regenerates the hub page, updates sitemap.xml, llms.txt, blog index and footers. Never deletes files.
"""
import json, sys, datetime, zoneinfo
from urllib.parse import quote
from sitegen import *

HUB = '/calefaccion-bomba-de-calor-madrid/'
HUB_NAME = 'Calefacción con bomba de calor en Madrid'
REGISTRY = 'content/invierno/publicadas.json'
TODAY = datetime.datetime.now(zoneinfo.ZoneInfo('Europe/Madrid')).date().isoformat()
FOOT_LINK = f'<br><strong>Invierno:</strong> <a href="{HUB}">{HUB_NAME}</a>'
BASE_TIPS = [('¿Merece la pena usar el aire acondicionado como calefacción?', '/blog/calefaccion-con-aire-acondicionado/')]

PRICES = '''<h2>Precios de aire acondicionado instalado en {c}</h2>
<ul><li><strong>Haier</strong>: desde 700 € instalado.</li><li><strong>Daikin</strong>: desde 900 € instalado.</li><li><strong>Mitsubishi</strong>: desde 1.040 € instalado.</li><li>Equipo adicional: +200 €. Retirada del equipo antiguo: +80 €.</li></ul>
<p>Precios para una habitación de hasta 20 m², IVA no incluido y sin coste de desplazamiento a {c}. Si quieres usarlo también como calefacción, dínoslo y te recomendamos un modelo con bomba de calor. Calcula tu caso en la <a href="/#calculadora">calculadora de presupuesto</a>.</p>
<h2>Cómo trabajamos en {c}</h2>
<ul><li><strong>Nos escribes</strong> por WhatsApp o llamada y nos cuentas qué necesitas.</li><li><strong>Presupuesto en 24h</strong>, con visita a tu casa o por fotos.</li><li><strong>Instalación en 48-72h</strong>, dejando todo limpio y funcionando.</li><li><strong>2 años de garantía</strong> e instalación certificada según el RITE.</li></ul>'''


def load_registry():
    try:
        return json.loads(rd(REGISTRY))
    except FileNotFoundError:
        return []


def zones(reg, exclude=None):
    return [(f"Calefacción en {r['name']}", r['path']) for r in reg if r['kind'] == 'zona' and r['path'] != exclude]


def tips(reg, exclude=None):
    return [(r['headline'], r['path']) for r in reg if r['kind'] == 'articulo' and r['path'] != exclude] + BASE_TIPS


def winter_links(reg, path):
    out = ''
    z = zones(reg, path)
    if z:
        out += link_grid_section('Calefacción con bomba de calor en otras zonas', [(HUB_NAME, HUB)] + z)
    return out + link_grid_section('Consejos de invierno', tips(reg, path))


def publish_zona(s, reg):
    c, path = s['zone'], f"/{s['slug']}/"
    svc, gal = city_sections()
    faqs = [tuple(x) for x in s['faqs']]
    lds = [{"@context": "https://schema.org", "@type": "Service", "name": f"Calefacción con aire acondicionado en {c}",
            "serviceType": "Instalación, reparación y mantenimiento de aire acondicionado con bomba de calor",
            "url": B + path, "description": s['desc'], "provider": PROVIDER, "areaServed": [{"@type": "Place", "name": c}]},
           crumbs_ld([("Inicio", B + '/'), (HUB_NAME, B + HUB), (f"Calefacción en {c}", B + path)]), faq_ld(faqs)]
    main = (f'<main>\n<div class="wrap crumbs"><a href="/">Inicio</a> › <a href="{HUB}">Calefacción en invierno</a> › {c}</div>\n'
            + hero(f'Calefacción en {c}', s.get('h1', f'Calefacción con aire acondicionado en {c}'), s['lead'],
                   f'Hola, quiero información de calefacción con aire acondicionado en {c}')
            + svc.replace('Getafe', c)
            + '<section style="padding-top:0"><div class="wrap prose">' + s['body_html'] + PRICES.format(c=c)
            + f'<h2>Zonas de {c} donde trabajamos</h2><p>{s["barrios"]} Si no ves tu calle, <a href="{WA}{quote(f"Hola, quiero saber si llegáis a mi zona en {c}")}" target="_blank" rel="noopener">pregúntanos por WhatsApp</a>.</p></div></section>'
            + gal + winter_links(reg, path) + FAQ_SEC.format(faq_html(faqs)) + '\n</main>')
    build(CITY_TEMPLATE, path, s['title'], s['desc'], 'website', lds, main)
    return {'kind': 'zona', 'path': path, 'name': c, 'headline': s['title'], 'summary': s['desc'], 'date': TODAY}, 'Invierno: calefacción por zonas', '0.8'


def publish_articulo(s, reg):
    path = f"/blog/{s['slug']}/"
    faqs = [tuple(x) for x in s['faqs']]
    lds = [{"@context": "https://schema.org", "@type": "Article", "headline": s['headline'], "description": s['desc'],
            "mainEntityOfPage": B + path, "image": B + "/og-image.jpg", "inLanguage": "es-ES",
            "datePublished": TODAY, "dateModified": TODAY,
            "author": {"@type": "Organization", "name": "YJV Clima y Confort", "url": B + "/"}, "publisher": PROVIDER},
           crumbs_ld([("Inicio", B + '/'), ("Consejos", B + '/blog/'), (s['short'], B + path)]), faq_ld(faqs)]
    main = (f'<main>\n<div class="wrap crumbs"><a href="/">Inicio</a> › <a href="/blog/">Consejos</a> › {s["short"]}</div>\n'
            + hero(s['eyebrow'], s['headline'], s['lead'], s['wa_text'])
            + '<section style="padding-top:0"><div class="wrap prose">' + s['body_html'] + '</div></section>'
            + winter_links(reg, path) + post_services_links() + FAQ_SEC.format(faq_html(faqs)) + '\n</main>')
    build(POST_TEMPLATE, path, s['title'], s['desc'], 'article', lds, main)
    bi = rd('blog/index.html')
    if f'href="{path}"' not in bi.split('<footer>')[0]:
        bi = bi.replace('</div></div></section>', f'<div class="faq-item"><h3><a href="{path}">{s["headline"]}</a></h3><p>{s["summary"]}</p></div></div></div></section>', 1)
        wr('blog/index.html', bi)
    return {'kind': 'articulo', 'path': path, 'name': s['short'], 'headline': s['headline'], 'summary': s['summary'], 'date': TODAY}, 'Invierno: consejos', '0.7'


def build_hub(reg):
    svc, gal = city_sections()
    faqs = [('¿El aire acondicionado sirve de calefacción?', 'Sí, si es bomba de calor. La mayoría de splits actuales lo son: si en el mando tienes el modo calor (un sol), el tuyo también calienta.'),
            ('¿Trabajáis en invierno?', 'Sí. En invierno instalamos, reparamos y revisamos equipos igual que en verano, y suele ser más fácil darte cita rápida.'),
            ('¿Cuánto cuesta instalar aire acondicionado en Madrid?', 'Desde 700 € instalado (Haier), 900 € (Daikin) o 1.040 € (Mitsubishi) para una habitación de hasta 20 m², IVA no incluido.'),
            ('¿Mi aire no calienta bien, qué hago?', 'Revisa que el mando esté en modo calor y limpia los filtros. Si sigue igual, escríbenos por WhatsApp y lo revisamos.')]
    lds = [{"@context": "https://schema.org", "@type": "Service", "name": HUB_NAME,
            "serviceType": "Instalación, reparación y mantenimiento de aire acondicionado con bomba de calor",
            "url": B + HUB, "provider": PROVIDER, "areaServed": [{"@type": "City", "name": "Madrid"}]},
           crumbs_ld([("Inicio", B + '/'), (HUB_NAME, B + HUB)]), faq_ld(faqs)]
    body = ('<h2>Calienta tu casa con el aire acondicionado</h2>'
            '<p>Un aire acondicionado con bomba de calor toma calor del aire exterior y lo mete en casa, por eso gasta mucho menos que un radiador o un calefactor eléctrico. Es una buena opción para pisos sin gas, para habitaciones que usas a ratos o como apoyo a la caldera. Te lo explicamos en <a href="/blog/calefaccion-con-aire-acondicionado/">¿merece la pena usar el aire acondicionado como calefacción?</a></p>'
            '<h2>Qué hacemos en invierno</h2><ul>'
            '<li><a href="/instalacion-aire-acondicionado-madrid/">Instalación</a> de equipos para frío y calor, en 48-72h.</li>'
            '<li><a href="/reparacion-aire-acondicionado-madrid/">Reparación</a> de equipos que no calientan, gotean o dan error.</li>'
            '<li><a href="/mantenimiento-aire-acondicionado-madrid/">Mantenimiento</a>: limpieza de filtros y batería para que caliente bien y gaste menos.</li>'
            '<li><a href="/sustitucion-aire-acondicionado-madrid/">Sustitución</a> de equipos antiguos por inverter.</li></ul>'
            + PRICES.format(c='Madrid'))
    main = (f'<main>\n<div class="wrap crumbs"><a href="/">Inicio</a> › Calefacción en invierno</div>\n'
            + hero('Campaña de invierno', 'Calefacción con aire acondicionado en Madrid',
                   'Instalamos, reparamos y revisamos aire acondicionado con bomba de calor en Madrid capital y municipios cercanos. Presupuesto gratis en 24 horas por WhatsApp.',
                   'Hola, quiero información de calefacción con aire acondicionado')
            + svc.replace('Getafe', 'Madrid')
            + '<section style="padding-top:0"><div class="wrap prose">' + body + '</div></section>'
            + (link_grid_section('Zonas de Madrid donde trabajamos este invierno', zones(reg)) if zones(reg) else '')
            + link_grid_section('Consejos de invierno', tips(reg)) + gal + FAQ_SEC.format(faq_html(faqs)) + '\n</main>')
    build(CITY_TEMPLATE, HUB, 'Calefacción con Aire Acondicionado en Madrid | Bomba de Calor | YJV Clima',
          'Calefacción con aire acondicionado y bomba de calor en Madrid y alrededores: instalación desde 700 €, reparación y mantenimiento. Presupuesto gratis en 24h.',
          'website', lds, main)


def main():
    s = json.load(open(sys.argv[1], encoding='utf-8'))
    reg = load_registry()
    entry, section, prio = (publish_zona if s['kind'] == 'zona' else publish_articulo)(s, reg)
    reg = [r for r in reg if r['path'] != entry['path']] + [entry]
    # rebuild previously published pages' link grids is not needed: hub + footers link everything
    build_hub(reg)
    for p in all_html():
        h = rd(p)
        if FOOT_LINK not in h and '<div class="site-links">' in h:
            i = h.index('</div>', h.index('<div class="site-links">'))
            wr(p, h[:i] + FOOT_LINK + h[i:])
    add_to_sitemap(HUB, TODAY, '0.8')
    touch_sitemap(HUB, TODAY)
    add_to_sitemap(entry['path'], TODAY, prio)
    if entry['kind'] == 'articulo':
        touch_sitemap('/blog/', TODAY)
    add_to_llms('Invierno: calefacción con aire acondicionado', HUB_NAME, HUB,
                'Calefacción con aire acondicionado y bomba de calor en Madrid y alrededores: instalación, reparación y mantenimiento.')
    add_to_llms(section, entry['headline'].split(' | YJV')[0], entry['path'], entry['summary'])
    wr(REGISTRY, json.dumps(reg, ensure_ascii=False, indent=1) + '\n')
    print(B + entry['path'])


if __name__ == '__main__':
    main()
