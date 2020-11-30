#docker img下载,支持断点续传,进度和速度显示
#version 2.0

import os
import sys
import gzip
from io import BytesIO
import json
import hashlib
import shutil
import requests
import tarfile
import urllib3
import time
urllib3.disable_warnings()

if sys.platform=='linux':
    import readline
path=os.path.abspath('.')
if 'tools' in path.replace('\\','/').split('/'):#这里是为了便于开发调试
    path=path.split('tools',maxsplit=1)[0]+'Library/utils'
else:
    path=path+'/Library/utils'
if not path in (p.replace('\\','/') for p in sys.path):
    sys.path.append(path)

from pbar import Pbar

#from Library.utils.pbar import Pbar

# sys.argv.append('kalilinux/kali-rolling')
# sys.argv.append('W:/downloads/docker')
if len(sys.argv) < 2 :
    print('Usage:#docker_pull [registry/][repository/]image[:tag|@digest] [base save path]\n')
    print('参考:https://github.com/NotGlop/docker-drag/')
    print('增加了断点续传支持和详细的进度速度显示,下载中可以ctrl+c,将会自动保存进度')
    exit(1)


if len(sys.argv)==3:
    base_path=sys.argv[2]
    if not base_path.endswith('/'):
        base_path=base_path+'/'
    if not os.path.exists(base_path):
        print('base path not found')
        exit(1)
else:
    base_path=os.path.abspath('.')+'/output/docker/'
if not os.path.exists(base_path):
    os.mkdir(base_path)

# Look for the Docker image to download
repo = 'library'
tag = 'latest'
imgparts = sys.argv[1].split('/')
try:
    img,tag = imgparts[-1].split('@')
except ValueError:
    try:
        img,tag = imgparts[-1].split(':')
    except ValueError:
        img = imgparts[-1]
# Docker client doesn't seem to consider the first element as a potential registry unless there is a '.' or ':'
if len(imgparts) > 1 and ('.' in imgparts[0] or ':' in imgparts[0]):
    registry = imgparts[0]
    repo = '/'.join(imgparts[1:-1])
else:
    registry = 'registry-1.docker.io'
    if len(imgparts[:-1]) != 0:
        repo = '/'.join(imgparts[:-1])
    else:
        repo = 'library'
repository = '{}/{}'.format(repo, img)

bar=Pbar(move_mode='ll',show_percent_num=True,info_len=50)
bar.start_bar()

bar.set_rate(20,'Get Docker authentication endpoint')
# Get Docker authentication endpoint when it is required
auth_url='https://auth.docker.io/token'
reg_service='registry.docker.io'
resp = requests.get('https://{}/v2/'.format(registry), verify=False)
if resp.status_code == 401:
    auth_url = resp.headers['WWW-Authenticate'].split('"')[1]
    try:
        reg_service = resp.headers['WWW-Authenticate'].split('"')[3]
    except IndexError:
        reg_service = ""


# Get Docker token (this function is useless for unauthenticated registries like Microsoft)
def get_auth_head(type):
    resp = requests.get('{}?service={}&scope=repository:{}:pull'.format(auth_url, reg_service, repository), verify=False)
    access_token = resp.json()['token']
    auth_head = {'Authorization':'Bearer '+ access_token, 'Accept': type}
    return auth_head



bar.set_rate(40,'Fetch manifest v2 and get image layer digests')
# Fetch manifest v2 and get image layer digests
auth_head = get_auth_head('application/vnd.docker.distribution.manifest.v2+json')
resp = requests.get('https://{}/v2/{}/manifests/{}'.format(registry, repository, tag), headers=auth_head, verify=False)
if (resp.status_code != 200):
    bar.print('[-] Cannot fetch manifest for {} [HTTP {}]'.format(repository, resp.status_code))
    bar.print(resp.content)
    auth_head = get_auth_head('application/vnd.docker.distribution.manifest.list.v2+json')
    resp = requests.get('https://{}/v2/{}/manifests/{}'.format(registry, repository, tag), headers=auth_head, verify=False)
    if (resp.status_code == 200):
        bar.print('[+] Manifests found for this tag (use the @digest format to pull the corresponding image):')
        manifests = resp.json()['manifests']
        for manifest in manifests:
            for key, value in manifest["platform"].items():
                bar.print('{}: {}, '.format(key, value))
            bar.print('digest: {}'.format(manifest["digest"]))
    bar.clear(True)
    exit(1)

layers = resp.json()['layers']

bar.set_rate(60,'Create image folder')
# Create tmp folder that will hold the image
imgdir = base_path+'tmp_{}_{}'.format(img, tag.replace(':', '@'))

if not os.path.exists(imgdir):
    os.mkdir(imgdir)
    bar.print('Creating image structure in: ' + imgdir)
else:
    bar.print('Detect exists image , resume download...')

bar.set_rate(80,'Get image config')
config = resp.json()['config']['digest']
confresp = requests.get('https://{}/v2/{}/blobs/{}'.format(registry, repository, config), headers=auth_head, verify=False)
file = open('{}/{}.json'.format(imgdir, config[7:]), 'wb')
file.write(confresp.content)
file.close()

content = [{
    'Config': config[7:] + '.json',
    'RepoTags': [ ],
    'Layers': [ ]
    }]
if len(imgparts[:-1]) != 0:
    content[0]['RepoTags'].append('/'.join(imgparts[:-1]) + '/' + img + ':' + tag)
else:
    content[0]['RepoTags'].append(img + ':' + tag)

empty_json = '{"created":"1970-01-01T00:00:00Z","container_config":{"Hostname":"","Domainname":"","User":"","AttachStdin":false, \
    "AttachStdout":false,"AttachStderr":false,"Tty":false,"OpenStdin":false, "StdinOnce":false,"Env":null,"Cmd":null,"Image":"", \
    "Volumes":null,"WorkingDir":"","Entrypoint":null,"OnBuild":null,"Labels":null}}'

bar.set_rate(100,'init success')
bar.print('Init success')
bar.set_rate(0,'Download layer...')

# Build layer folders
parentid=''
for layer in layers:
    ublob = layer['digest']
    # FIXME: Creating fake layer ID. Don't know how Docker generates it
    fake_layerid = hashlib.sha256((parentid+'\n'+ublob+'\n').encode('utf-8')).hexdigest()
    layerdir = imgdir + '/' + fake_layerid
    if not os.path.exists(layerdir):
        os.mkdir(layerdir)
    if os.path.exists(layerdir+'/layer.tar'):
        bar.print(ublob[7:19] + ': Exists skip...')
        continue
    stream_start_index=0
    if os.path.exists(layerdir+'/stream_index'):
        with open(layerdir+'/stream_index','r',encoding='utf-8') as f:
            stream_start_index=int(f.read().strip())
        bar.print('Resume download on:'+str(stream_start_index))

    # Creating VERSION file
    file = open(layerdir + '/VERSION', 'w')
    file.write('1.0')
    file.close()

    # Creating layer.tar file
    bar.print(ublob[7:19] + ': Downloading...')
    bar.set_rate(None,ublob[7:19] + ': Get Docker auth token...')

    auth_head = get_auth_head('application/vnd.docker.distribution.manifest.v2+json') # refreshing token to avoid its expiration
    if stream_start_index!=0:
        auth_head['Range']='bytes='+str(stream_start_index)+'-'

    bar.set_rate(None, 'Wait response...')
    stream_index=0
    
    try:
        bresp = requests.get('https://{}/v2/{}/blobs/{}'.format(registry, repository, ublob), headers=auth_head, stream=True, verify=False)
        if (bresp.status_code not in (200,206)): # When the layer is located at a custom URL
            bresp = requests.get(layer['urls'][0], headers=auth_head, stream=True, verify=False)
            if (bresp.status_code not in (200,206)):
                bar.print('ERROR: Cannot download layer {} [HTTP {}]'.format(ublob[7:19], bresp.status_code))
                bar.print(bresp.content)
                bar.clear(True)
                exit(1)
        # Stream download and follow the progress
        bresp.raise_for_status()
        total_size = int(bresp.headers['Content-Length'])

        if stream_start_index==0:
            mode='wb'
        else:
            mode='ab'
        last_index=[time.time(),stream_start_index,0]

        with open(layerdir + '/layer_gzip.tar', mode) as file:
            for chunk in bresp.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    stream_index+=len(chunk)
                    bar.set_rate((stream_start_index+stream_index)*100//total_size,'{}/{} bytes,{} k/s'.format(stream_start_index+stream_index,total_size,round(last_index[2]/1024,1)))
                now= time.time()
                if now-last_index[0]>=1:
                    dld=stream_start_index+stream_index-last_index[1]
                    speed=dld/(now-last_index[0])
                    bar.set_rate(None,'{}/{} bytes,{} k/s'.format(stream_start_index+stream_index,total_size,round(last_index[2]/1024,1)))

                    last_index[0]=now
                    last_index[1]=stream_start_index+stream_index
                    last_index[2]=speed
                    
    except KeyboardInterrupt:
        bar.print(ublob[7:19] + ': Donwload cancle , save index...')
        bar.set_rate(0,'Cancel...')
        if stream_index!=0:
            with open(layerdir+'/stream_index','w',encoding='utf-8') as f:
                f.write(str(stream_start_index+stream_index))
        
        bar.clear(True)
        exit(1)

    except Exception as identifier:
        bar.print(ublob[7:19] + ': Donwload error , save index...')
        bar.set_rate(0,'Error...')
        if stream_index!=0:
            with open(layerdir+'/stream_index','w',encoding='utf-8') as f:
                f.write(str(stream_start_index+stream_index))
        bar.clear(True)
        exit(1)
        


    bar.print("\r{}: Extracting...{}".format(ublob[7:19], " "*50)) # Ugly but works everywhere
    bar.set_rate(0,'Extracting...')
    with open(layerdir + '/layer.tar', "wb") as file: # Decompress gzip response
        unzLayer = gzip.open(layerdir + '/layer_gzip.tar','rb')
        shutil.copyfileobj(unzLayer, file)
        unzLayer.close()
    if os.path.exists(layerdir + '/stream_index'):
        os.remove(layerdir + '/stream_index')
    os.remove(layerdir + '/layer_gzip.tar')
    bar.print("{}: Pull complete [{}]".format(ublob[7:19], stream_start_index+stream_index))
    content[0]['Layers'].append(fake_layerid + '/layer.tar')
    
    # Creating json file
    file = open(layerdir + '/json', 'w')
    # last layer = config manifest - history - rootfs
    if layers[-1]['digest'] == layer['digest']:
        # FIXME: json.loads() automatically converts to unicode, thus decoding values whereas Docker doesn't
        json_obj = json.loads(confresp.content)
        del json_obj['history']
        try:
            del json_obj['rootfs']
        except: # Because Microsoft loves case insensitiveness
            del json_obj['rootfS']
    else: # other layers json are empty
        json_obj = json.loads(empty_json)
    json_obj['id'] = fake_layerid
    if parentid:
        json_obj['parent'] = parentid
    parentid = json_obj['id']
    file.write(json.dumps(json_obj))
    file.close()
    bar.set_rate(0,'')

file = open(imgdir + '/manifest.json', 'w')
file.write(json.dumps(content))
file.close()

if len(imgparts[:-1]) != 0:
    content = { '/'.join(imgparts[:-1]) + '/' + img : { tag : fake_layerid } }
else: # when pulling only an img (without repo and registry)
    content = { img : { tag : fake_layerid } }
file = open(imgdir + '/repositories', 'w')
file.write(json.dumps(content))
file.close()

# Create image tar and clean tmp folder
docker_tar = repo.replace('/', '_') + '_' + img + '.tar'
bar.print("Creating archive...")
bar.set_rate(50,"Creating archive...")
tar = tarfile.open(docker_tar, "w")
tar.add(imgdir, arcname=os.path.sep)
bar.set_rate(100)
tar.close()
shutil.rmtree(imgdir)
bar.print('Docker image pulled: ' + docker_tar)
bar.clear(True)