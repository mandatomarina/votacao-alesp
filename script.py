from fixedwidth.fixedwidth import FixedWidth
import subprocess
from lxml.html import fromstring
import urllib.request
import os
#pdftotext -layout -x 34 -y 140 -W 260 -H 565 20190507-200713-ID_SESSAO\=13698-PDF.pdf teste.csv

class Votacao:

    def __init__(self, vote):
        self.infile = 'data/' + vote['filename']
        self.ementa = vote['proposicao']
        self.nome = vote['nome']
        self.raw = {'right' : [], 'left' : []}
        self.data = []
        self.table = []

    def _extract(self, linha, side):
        x = {}
        if side == 'left':
            x['nome'] = linha[0:47].strip().replace("L ","").replace("P ", "").strip()
            x['partido'] = linha[48:65].strip()
            x['voto'] = linha[66:].strip()
        else:
            x['nome'] = linha[0:60].strip().replace("L ","").strip()
            x['partido'] = linha[61:78].strip()
            x['voto'] = linha[78:].strip()
        return x

    def _totxt(self):
        #esquerda
        args = ["pdftotext", "-layout", "-fixed", "3", "-x", "34", "-y", "140", "-W", "260", "-H", "565", self.infile, self.infile + "_l.txt"]
        subprocess.call(args)
        self.raw['left'] = open(self.infile + "_l.txt", "r").readlines()

        args = ["pdftotext", "-layout", "-fixed", "3", "-x", "280", "-y", "140", "-W", "370", "-H", "565", self.infile, self.infile + "_r.txt"]
        subprocess.call(args)
        self.raw['right'] += open(self.infile + "_r.txt", "r").readlines()

    def _process(self):
        if not self.raw['right']:
            self._totxt()
        for l in self.raw['left']:
            if len(l) > 1:
                self.data.append(self._extract(l, 'left'))
        for l in self.raw['right']:
            if len(l) > 1:
                self.data.append(self._extract(l, 'right'))
        return self.data

def rockandroll():
    url = "https://www.al.sp.gov.br/alesp/votacoes-no-plenario/?anoSessao=2019"

    soup = fromstring(urllib.request.urlopen(url).read())

    x = "//table[@class='tabela']//a[contains(@href,'.pdf')]"

    votes = []
    for vote in soup.xpath(x):
        v = {}
        v['nome'] = vote.text
        v['vote_url'] = vote.get('href')
        v['filename'] = v['vote_url'].split("/")[-1]
        try:
            v['proposicao'] = vote.getparent().getparent().getnext().xpath(".//a")[0].text
            v['proposicao_url'] = vote.getparent().getparent().getnext().xpath(".//a")[0].get('href')
        except:
            v['proposicao'] = ""
            v['proposicao_url'] = ""

        if not os.path.isfile("data/"+v['filename']):
            print("Getting "+v['vote_url'])
            tmp = urllib.request.urlopen(v['vote_url'])
            with open('data/'+v['filename'], 'wb') as arquivo:
                arquivo.write(tmp.read())
        votes.append(v)
    return votes

votes = rockandroll()
tabelao = []
for v in votes:
    if v['proposicao']:
        w = Votacao(v)
        w._process()
        for item in w.data:
            linha = [w.nome, item['nome'], item['partido'], item['voto']]
            tabelao.append(linha)

import csv
with open("resultado.csv", "w") as arquivo:
    x = csv.writer(arquivo)
    x.writerows(tabelao)
    arquivo.close()
