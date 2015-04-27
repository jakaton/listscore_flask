#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Flask web service for scoring text given a predifined list
# ----------------------------------------------------------------------
# Ivan Vladimir Meza-Ruiz/ ivanvladimir at turing.iimas.unam.mx
# 2015/IIMAS/UNAM
# ----------------------------------------------------------------------
from __future__ import print_function

from flask import Flask, request
import codecs
import json
import argparse
from collections import Counter


app = Flask('scorelistservice')

resources={
    "sentimiento":"data/sentimiento.txt",
    "affin":"data/afinn.txt",
    "whissell":"data/whissell.txt",
    "sentiwn":"data/sentiwn.txt",
}

def load_resource(name,namefile):
    resource={}
    if name in ["sentimiento","affin"]:
        for line in open(namefile):
            line=line.strip()
            if len(line)==0 or line.startswith("#"):
                continue
            line=line.rsplit(None,1)
            resource[line[0]]=float(line[1])
    if name in ["whissell","sentiwn"]:
        for line in open(namefile):
            line=line.strip()
            if len(line)==0 or line.startswith("#"):
                continue
            line=line.split(';')
            resource[line[0]]=tuple([float(x) for x in line[1:]])
    return resource

def load_resources(resources):
    resources_={}
    for k,v in resources.iteritems():
        resources_[k]=(v,load_resource(k,v))
    return resources_

resources=load_resources(resources)    

@app.route('/',methods=['GET'])
def index():
    return "Service up" 

@app.route('/api/v1.0/lists',methods=['GET'])
def get_lists():
    return json.dumps({"lists":resources.keys()}) 

@app.route('/api/v1.0/list/<string:name>',methods=['GET'])
def get_list(name):
    if resources.has_key(name):
        return json.dumps(resources[name][1]) 
    else:
        return json.dumps([])

def score1(text,score):
    res=[]
    sentimiento_res=resources[score][1]
    for line in text.split('\n'):
        line=line.strip()
        words=Counter(line.split())
        counts=[ k*sentimiento_res.get(w,0) for w,k in words.iteritems()]
        res.append((line,sum(counts)))
    return res
 
@app.route('/api/v1.0/score/sentimiento/<string:sntc>',methods=['GET'] )
def score_sentimiento_get(sntc):
    res=score1(sntc,"sentimiento")
    return json.dumps({"scores":res},ensure_ascii=False) 


@app.route('/api/v1.0/score/sentimiento',methods=['POST'] )
def score_sentimiento_pos():
    text=request.data
    res=score1(text,"sentimiento")
    return json.dumps({"scores":res},ensure_ascii=False) 

@app.route('/api/v1.0/score/affin/<string:sntc>',methods=['GET'] )
def score_affin_get(sntc):
    res=score1(sntc,"affin")
    return json.dumps({"scores":res},ensure_ascii=False) 

@app.route('/api/v1.0/score/affin',methods=['POST'] )
def score_affin_pos():
    text=request.data
    res=score1(text,"affin")
    return json.dumps({"scores":res},ensure_ascii=False) 

def score_whissell(text):
    res=[]
    sentimiento_res=resources["whissell"][1]
    for line in text.split('\n'):
        line=line.strip()
        words=Counter(line.split())
        counts=[ (k,sentimiento_res.get(w,(0,0,0))) for w,k in words.iteritems()]
        counts=[(k*s[0],k*s[1],k*s[2]) for k,s in counts]
        counts_=[0,0,0]
        for c in counts:
            counts_[0]+=c[0]
            counts_[1]+=c[1]
            counts_[2]+=c[2]
        res.append((line,(counts_[0],counts_[1],counts_[2])))
    return res
 

@app.route('/api/v1.0/score/whissell/<string:sntc>',methods=['GET'] )
def score_whissell_get(sntc):
    res=score_whissell(sntc)
    return json.dumps({ "order":["pleasantness","activation","imagery"],
                        "scores":res,},ensure_ascii=False) 

@app.route('/api/v1.0/score/whissell',methods=['POST'] )
def score_whissell_pos():
    text=request.data
    res=score_whissell(text)
    return json.dumps({ "order":["pleasantness","activation","imagery"],
                        "scores":res,},ensure_ascii=False) 

def score_sentiwn(text):
    res=[]
    sentimiento_res=resources["sentiwn"][1]
    for line in text.split('\n'):
        line=line.strip()
        words=Counter(line.split())
        counts=[ (k,sentimiento_res.get(w,(0,0))) for w,k in words.iteritems()]
        counts=[(k*s[0],k*s[1]) for k,s in counts]
        counts_=[0,0]
        for c in counts:
            counts_[0]+=c[0]
            counts_[1]+=c[1]
        res.append((line,(counts_[0],counts_[1])))
    return res
 

@app.route('/api/v1.0/score/sentiwn/<string:sntc>',methods=['GET'] )
def score_sentiwn_get(sntc):
    res=score_sentiwn(sntc)
    return json.dumps({ "order":["pos","neg"],
                        "scores":res,},ensure_ascii=False) 

@app.route('/api/v1.0/score/sentiwn',methods=['POST'] )
def score_sentiwn_pos():
    text=request.data
    res=score_sentiwn(text)
    return json.dumps({ "order":["pos","neg"],
                        "scores":res,},ensure_ascii=False) 


if __name__ == '__main__':
    p = argparse.ArgumentParser("Score list service")
    p.add_argument("--host",default="127.0.0.1",
            action="store", dest="host",
            help="Root url [127.0.0.1]")
    p.add_argument("--port",default=5000,type=int,
            action="store", dest="port",
            help="Port url [500]")
    p.add_argument("--debug",default=False,
            action="store_true", dest="debug",
            help="Use debug deployment [Flase]")
    p.add_argument("-v", "--verbose",
            action="store_true", dest="verbose",
            help="Verbose mode [Off]")
    opts = p.parse_args()

    app.run(debug=opts.debug,
            host=opts.host,
            port=opts.port)

