from urllib import request
import json
import re


def get_html_from_url(url):
    print(url)
    while True:
        try:
            response = request.urlopen(url, timeout=5)
            html = response.read().decode('utf-8')
            return html
        except Exception as e:
            continue


def get_msg_urls():
    url = "https://www.cryst.ehu.es/cryst/magnext.php?from=mwyckpos&magtr=2"
    html = get_html_from_url(url)

    pattern = re.compile("<td bgcolor=\"#f0f0f0\" align=\"left\"><a href=\".*?\"")
    sg_urls = [link[44:-1] for link in pattern.findall(html)]

    res = []
    for url in sg_urls:
        url = "https://www.cryst.ehu.es/cryst/magnext.php" + url
        html = get_html_from_url(url)
        res = res + get_msg_urls_from_html(html)
    return res


def get_msg_urls_from_html(html):
    pattern = re.compile(r"<b>Listed with respect to the <a href=\"/cryst/magnext_help.html#bns_og\">OG setting</a>:</b>")
    html = pattern.split(html)[0]

    pattern = re.compile(r"/cgi-bin/cryst/programs/nph-magwplist\?gnum=[0-9]+\.[0-9]+\"")
    res = [url[:-1] for url in pattern.findall(html)]
    return res


def get_wyckoff_positions():
    with open("data/msg_urls.json", "r") as f:
        msg_urls = json.load(f)
    res = []
    for url in msg_urls:
        url = "https://www.cryst.ehu.es" + url
        html = get_html_from_url(url)
        positions = get_wyckoff_positions_from_html(html)
        msg_id = get_msg_id_from_url(url)
        translation = get_translation_from_html(html)
        data = {
            "id": msg_id,
            "translation": translation,
            "wyckoff_positions": positions
        }
        res.append(data)
    return res


def get_translation_from_html(html):
    pattern = re.compile(r"\((?:[0-9](?:/[1-9])?),(?:[0-9](?:/[1-9])?),(?:[0-9](?:/[1-9])?)\)(?:\')?")
    return pattern.findall(html)


def get_msg_id_from_url(url):
    pattern = re.compile(r"[0-9]+\.[0-9]+")
    return pattern.findall(url)[0]


def get_wyckoff_positions_from_html(html):
    pattern = re.compile(r"<tr><td align=center>[0-9]+</td><td align=center>")
    sentences = pattern.split(html)

    res = []
    for i in range(1, len(sentences)):
        if i != len(sentences) - 1:
            s = sentences[i]
        else:
            s = sentences[i]
            pattern = re.compile(r"<h3>Site Symmetries of the Wyckoff Positions</h3>")
            s = pattern.split(s)[0]
        letter = s[0]
        pattern = re.compile(r"\(.*? \| .*?\)")
        positions = [re.sub(r'<.*?>', '', p) for p in pattern.findall(s)]
        print(positions)
        data = {
                "letter": letter,
                "postions": positions
                }
        res.append(data)
    return res


def crawl():
    msg_urls = get_msg_urls()
    with open("data/msg_urls.json", "w") as f:
        json.dump(msg_urls, f, indent=4, separators=(',', ':'))
    wp = get_wyckoff_positions()
    with open("data/wyckoff_position.json", "w") as f:
        json.dump(wp, f, indent=4, separators=(',', ':'))


if __name__ == "__main__":
    crawl()