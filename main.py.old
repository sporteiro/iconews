#!/usr/bin/py
# -*- coding: utf-8 -*-
import os
import re
import random
import hashlib
import hmac
import logging
import json
import urllib
import feedparser
from string import letters
import webapp2
import jinja2
import listaIconos
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'vistas')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

secret = 'icoNoticias'

paises={'Argentina':'https://news.google.com.ar/news/feeds?pz=1&cf=all&ned=es_ar&hl=es&output=rss',
'Colombia':'http://news.google.com.ar/news?cf=all&ned=es_co&hl=es&output=rss',
'Cuba':'http://news.google.com.ar/news?cf=all&ned=es_cu&hl=es&output=rss',
'Uruguay':'http://www.elobservador.com.uy/rss/nacional/',
#http://servicios.elpais.com.uy/formatos/rss/index.asp?seccion=umomento,
'Mexico':'http://news.google.com.mx/news?pz=1&cf=all&ned=es_mx&hl=es&output=rss',
'Venezuela':'http://news.google.com.ar/news?cf=all&ned=es_ve&hl=es&output=rss'
#'Espa'u'ña':'http://news.google.com.ar/news?cf=all&ned=es&hl=es&output=rss'
}

iconos=listaIconos.iconos


def mostrarImagen(contenido):
    imagen=re.compile(r'<img.*?/>')
#    if re.findall(imagen,contenido)!='':
    try:
	y=re.findall(imagen,contenido)[0]
        return y.replace('align="right"','')
    except IndexError, e:
	return ''

def devolveIcono(palabraClave):
    ci = [a for a, b in iconos.items() if palabraClave in b]
    return ci

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def render_json(self, d):
        json_txt = json.dumps(d)
        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        self.write(json_txt)

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

        if self.request.url.endswith('.json'):
            self.format = 'json'
        else:
            self.format = 'html'
#############################################################################################
class MainPage(BlogHandler):

  def get(self):
#CRONICA NO TIENE MAS RSS      generalCronica = feedparser.parse('http://www.cronica.com.ar/rss/informacion-general.xml')
      generalClarin =  feedparser.parse('http://clarin.feedsportal.com/c/33088/f/577681/index.rss')
      generalOle =  feedparser.parse('http://ole.feedsportal.com/c/33068/f/577712/index.rss')
      deporteLanacion = feedparser.parse('http://lanacion.com.ar.feedsportal.com/deportes')
      generalGnews =feedparser.parse(paises['Argentina'])
 #     cronica = generalCronica.entries
      clarin = generalClarin.entries
      ole = generalOle.entries
      dlanacion=deporteLanacion.entries
      gn=generalGnews.entries
      todos=[]
 #     todos.append(cronica[0])
 #     todos.append(cronica[1])
#      self.render('index.html',titularesCronica = cronica,mostrarImagen=mostrarImagen,titularesClarin = clarin,todos=todos,devolveIcono=devolveIcono, gn = gn ,iconos=iconos,paises=sorted(paises))
      self.render('index.html',mostrarImagen=mostrarImagen,titularesClarin = clarin,todos=todos,devolveIcono=devolveIcono, gn = gn ,iconos=iconos,paises=sorted(paises))

  def post(self):
      pais = self.request.get('pais')
      if pais == 'Argentina':
#         generalCronica = feedparser.parse('http://www.cronica.com.ar/rss/informacion-general.xml')
#	  todos=generalCronica.entries[0:2]
	  todos=[]
          generalGnews =feedparser.parse(paises[pais])
          gn=generalGnews.entries
          self.render('index.html',todos=todos,gn = gn ,mostrarImagen=mostrarImagen,iconos=iconos,pais=pais,devolveIcono=devolveIcono,paises=sorted(paises))
      else:
          generalGnews = feedparser.parse(paises[pais])
          gn = generalGnews.entries
          self.render('index.html',gn = gn ,mostrarImagen=mostrarImagen,iconos=iconos,pais=pais,devolveIcono=devolveIcono,paises=sorted(paises))
#############################################################################################

app = webapp2.WSGIApplication([('/', MainPage),
			      ],
                              debug=True)
