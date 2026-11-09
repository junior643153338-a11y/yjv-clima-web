"""Shared helpers to generate pages for yjvclimayconfort.es from the existing page templates."""
import json, os, re
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = 'https://yjvclimayconfort.es'
WA = 'https://wa.me/34643153338?text='
CITY_TEMPLATE = 'aire-acondicionado-getafe/index.html'
POST_TEMPLATE = 'blog/cada-cuanto-mantenimiento-aire-acondicionado/index.html'


def rd(p):
    return open(os.path.join(ROOT, p), encoding='utf-8').read()


def wr(p, s):
    p = os.path.join(ROOT, p)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(s)


def esc_attr(s):
    return s.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;')


def ld(obj):
    return '<script type="application/ld+json">\n' + json.dumps(obj, ensure_ascii=False, indent=2) + '\n</script>'


def faq_ld(faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}


def crumbs_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}


def faq_html(faqs):
    return '<div class="faq-list">' + ''.join(f'<div class="faq-item"><h3>{q}</h3><p>{a}</p></div>' for q, a in faqs) + '</div>'


PROVIDER = {"@id": B + "/#negocio", "@type": "HVACBusiness", "name": "YJV Clima y Confort", "telephone": "+34643153338"}


def build(template, path, title, desc, og_type, lds, main):
    t = rd(template)
    url = B + path
    meta = f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="index, follow">
<title>{title}</title>
<meta name="description" content="{esc_attr(desc)}">
<link rel="canonical" href="{url}">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" href="/favicon-512.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="es_ES">
<meta property="og:site_name" content="YJV Clima y Confort">
<meta property="og:title" content="{esc_attr(title)}">
<meta property="og:description" content="{esc_attr(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{B}/og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
'''
    fonts = t[t.index('<link rel="preconnect"'):t.index('<script type="application/ld+json">')]
    rest = t[t.index('<style>'):]
    rest = rest[:rest.index('<main>')] + main + rest[rest.index('</main>') + len('</main>'):]
    wr(path.strip('/') + '/index.html', meta + fonts + '\n'.join(ld(x) for x in lds) + '\n' + rest)


def hero(eyebrow, h1, lead, wa_text):
    return f'''<section class="hero" style="padding-top:28px">
  <div class="wrap" style="grid-template-columns:1fr">
    <div>
      <div class="eyebrow">{eyebrow}</div>
      <h1>{h1}</h1>
      <p class="lead">{lead}</p>
      <div class="hero-ctas">
        <a class="btn btn-accent" href="{WA}{quote(wa_text)}" target="_blank" rel="noopener">Pide tu presupuesto gratis</a>
        <a class="btn btn-ghost" href="tel:+34643153338">Llamar: 643 153 338</a>
      </div>
    </div>
  </div>
</section>'''


FAQ_SEC = '''<section style="background: var(--bg-alt); border-top: 1px solid var(--line); border-bottom: 1px solid var(--line);">
  <div class="wrap">
    <div class="section-head"><h2>Preguntas frecuentes</h2></div>
    {}
  </div>
</section>'''


def link_grid_section(heading, links):
    inner = ''.join(f'<a href="{u}">{n}</a>' for n, u in links)
    return f'''<section style="padding-top:0">
  <div class="wrap">
    <div class="section-head" style="margin-bottom:16px"><h2>{heading}</h2></div>
    <div class="link-grid">{inner}</div>
  </div>
</section>'''


def city_sections():
    g = rd(CITY_TEMPLATE)
    svc = g[g.index('<section style="padding-top:0"><div class="wrap">'):g.index('</div></section>', g.index('services-grid')) + len('</div></section>')]
    gal = g[g.index('<section>\n  <div class="wrap">\n    <div class="section-head"><h2>Trabajos realizados'):]
    gal = gal[:gal.index('</section>') + len('</section>')]
    return svc, gal


def post_services_links():
    a = rd(POST_TEMPLATE)
    s = a[a.index('<section style="padding-top:0">\n  <div class="wrap">\n    <div class="section-head" style="margin-bottom:16px"><h2>Nuestros servicios'):]
    return s[:s.index('</section>') + len('</section>')]


def add_to_sitemap(path, today, priority):
    sm = rd('sitemap.xml')
    if f'<loc>{B}{path}</loc>' not in sm:
        sm = sm.replace('</urlset>', f'  <url>\n    <loc>{B}{path}</loc>\n    <lastmod>{today}</lastmod>\n    <priority>{priority}</priority>\n  </url>\n</urlset>')
    wr('sitemap.xml', sm)


def touch_sitemap(path, today):
    sm = rd('sitemap.xml')
    sm = re.sub(r'(<loc>' + re.escape(B + path) + r'</loc>\n    <lastmod>)[^<]+', r'\g<1>' + today, sm)
    wr('sitemap.xml', sm)


def add_to_llms(section, title, path, desc):
    ll = rd('llms.txt')
    if f'({B}{path})' in ll:
        return
    line = f'- [{title}]({B}{path}): {desc}'
    head = f'## {section}\n\n'
    if head in ll:
        nxt = ll.find('\n\n', ll.index(head) + len(head))
        ll = ll[:nxt] + '\n' + line + ll[nxt:]
    else:
        ll = ll.replace('\n\n- [Inicio]', f'\n\n{head}{line}\n\n- [Inicio]', 1)
    wr('llms.txt', ll)


def all_html():
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('tools', 'content')]
        for f in files:
            if f.endswith('.html'):
                yield os.path.relpath(os.path.join(root, f), ROOT)
