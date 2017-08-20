import os
from collections import OrderedDict
import shutil
import re
import json
from http.server import HTTPServer, CGIHTTPRequestHandler 
from jinja2 import Environment, FileSystemLoader, select_autoescape

env = None
def config():
    global env
    f = open('config.json')
    c = json.loads(f.read(),object_pairs_hook=OrderedDict)
    f.close()
    env = Environment(
        loader=FileSystemLoader(os.getcwd() + os.sep + "theme" + os.sep + c['theme']),
        autoescape=select_autoescape(['html', 'xml'])
    )
    return c
global_config = config()

def gen_html(template,md,config,output):
    t = env.get_template(template) 
    title = md.split('\n')[0].replace('#','').strip()
    context_dict = {
        'title':title,
        'md_content':md,
    }
    context_dict.update(config)
    #print(context_dict)
    s = t.render(context_dict)
    f = open('output' + os.sep + output,'w')
    f.write(s)
    f.close()
    print("Generate %s from %s"%(output,md))

def serve(path):
    PORT = 8000
    httpd = HTTPServer(("localhost", PORT), CGIHTTPRequestHandler)
    if not path:
        os.chdir('output')
    print("serving at port", PORT)
    httpd.serve_forever()

INDEX_CATE = 0
LIST_CATE = 1
DIRECT_CATE = 2

def gen_cates():
    cates = []
    for cate in global_config['cates'].keys():
        #the category which contains index.md 
        if ("index" in global_config['cates'][cate] and global_config['cates'][cate]['index']) or os.path.lexists(os.path.join('articles',cate,'index.md')):
            os.mkdir('output'+os.sep+cate)
            global_config['cates'][cate].update({'url':'/'+cate+'/index.html','text':cate})
            cates.append((cate,INDEX_CATE))
        #specify the page which have no directory
        elif not os.path.lexists(os.path.join('articles',cate)):
            global_config['cates'][cate].update({'url':'/'+global_config['cates'][cate]['url'],'text':global_config['cates'][cate]['text']})
            cates.append((cate,DIRECT_CATE))
        #cates which have no index.md 
        elif os.path.isdir('articles'+os.sep + cate):
            os.mkdir('output'+os.sep+cate)
            global_config['cates'][cate].update({'url':'/'+cate+'/list.html','text':cate})
            cates.append((cate,LIST_CATE))
    for cate,t in cates:
        get_site_items(cate)
        if t == INDEX_CATE:
            gen_html('index.html',get_md_content(os.path.join('articles',cate,'index.md')),global_config,os.path.join(cate,'index.html'))
        elif t == DIRECT_CATE:
            gen_html('detail.html',get_md_content(os.path.join('articles',global_config['cates'][cate]['md'])),global_config,global_config['cates'][cate]['url'])
        elif t == LIST_CATE:
            gen_html('list.html',"",global_config,os.path.join(cate,'list.html'))


def get_md_content(fn):
    f = open(fn)
    s = f.read()
    f.close()
    return s

def get_articles(cate):
    if os.path.isdir('articles'+os.sep + cate):
        if 'articles' in global_config['cates'][cate].keys() and global_config['cates'][cate]['articles']:
            fs = global_config['cates'][cate]['articles']
        else:
            fs_tuple = sorted([(fn, os.stat('articles'+os.sep+cate+os.sep+fn)) for fn in os.listdir('articles' + os.sep + cate)], key = lambda x: x[1].st_ctime,reverse=True)
        return [f[0] for f in fs_tuple if os.path.splitext(f[0])[1] == '.md' and os.path.splitext(f[0])[0] != 'index']
    else:
        return []


def get_site_items(cate):
    global_config.update({'side_items':[]})
    fs = get_articles(cate)
    for fn in fs:
        fn,ext = os.path.splitext(fn)
        global_config['side_items'].append({'url':'/'+cate+'/'+fn+'.html','text':fn})

def run():
    if os.path.lexists('output'):
        shutil.rmtree('output')
    os.mkdir(os.getcwd()+os.sep+'output')

    gen_cates()

    #generate pages
    for cate in global_config['cates'].keys():
        fs = get_articles(cate)
        get_site_items(cate)
        articles = []
        for f in fs:
            fn,ext = os.path.splitext(f)
            if ext == '.md' and fn != 'index':
                articles.append({'url':'/'+cate+'/'+fn+'.html','text':fn})
                print(global_config)
                gen_html('detail.html',get_md_content(os.path.join('articles',cate,f)),global_config,os.path.join(cate,fn+'.html'))
        global_config.update({'articles':articles})


    global_config.update({'side_items':[]})
    gen_html('index.html',get_md_content(os.path.join('articles',global_config["index"])),global_config,'index.html')
    shutil.copy('output'+os.sep+'index.html','index.html')
    
    serve(global_config['path_prefix'])

if __name__ ==  '__main__':
    run()

