# NetEasePlaylistDL
#请打开config.ini配置文件配置相应信息

import requests
import jsonpath
import subprocess
import os
import sys
import time
import configparser

config = configparser.ConfigParser()
config.read('config.ini',encoding='utf-8')
path = config.get('output', 'path')
if path == '':
    path = os.getcwd()
filename = config.get('output','filename')

try:
    Playlist_id = int(input("歌单id："))
except:
    print("非法输入！")
    sys.exit(1)

headers = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67'
}

def MusicDown(Playlist_name,id,name,artists):
    try:
        data = requests.get('https://music.163.com/song/media/outer/url?id=' + str(id), headers=headers)
    except:
        print("获取歌曲音频失败！")

    try:
        with open(path + "\\" + Playlist_name + "\\" + name + "-" + artists + "-origin" + ".mp3", "wb") as file:
            file.write(data.content)
    except:
        print(name+"-"+artists+".mp3  "+"download failed")

    print(name+"-"+artists+".mp3  "+"download completed")

def AddMetadata(Playlist_name,name,artists):
    metadata = {
        'title': name,
        'artist': artists,
    }
    input_file = path+"\\"+Playlist_name+"\\"+name+"-"+artists+"-origin"+".mp3"
    output_file = path+"\\"+Playlist_name+"\\"+name+"-"+artists+".mp3"
    # 构建ffmpeg命令
    command = ['ffmpeg', '-i', input_file]

    # 添加元信息参数
    for key, value in metadata.items():
        command.extend(['-metadata', f'{key}={value}'])

    # 添加输出文件路径
    command.append(output_file)

    # 执行ffmpeg命令
    subprocess.run(command)

def RemoveOrigin(Playlist_name,name,artists):
    os.remove(path+"\\"+Playlist_name+"\\"+name+"-"+artists+"-origin"+".mp3")



response = requests.get("https://music.163.com/api/playlist/detail?id="+str(Playlist_id),headers=headers)

if response.status_code == 200:
    data = response.json()
    try:
        amount = len(jsonpath.jsonpath(data, "$.[tracks]")[0])
    except:
        print("获取歌曲数量异常")
        print(data)
        time.sleep(5)
        sys.exit(1)

    try:
        Playlist_name = jsonpath.jsonpath(data, "$.['name']")[0]
    except:
        print("获取歌单名称失败！")
        time.sleep(5)
        sys.exit(1)
    try:
        if not os.path.exists(path + "\\" + Playlist_name):
            os.mkdir(path + "\\" + Playlist_name)
    except:
        print("创建歌单文件夹失败!")
        time.sleep(5)
        sys.exit(1)

    for i in range(amount):
        name = jsonpath.jsonpath(data, "$.[tracks]["+str(i)+"]['name']")[0]
        id = jsonpath.jsonpath(data, "$.[tracks]["+str(i)+"]['id']")[0]
        artists = jsonpath.jsonpath(data, "$.[tracks]["+str(i)+"]['artists'][0]['name']")[0]
        MusicDown(Playlist_name,id, name, artists)
        AddMetadata(Playlist_name,name,artists)
        RemoveOrigin(Playlist_name,name,artists)

else:
    print("请求失败！")

# name: $.[tracks][0]['name']
# ID： $.[tracks][0]['id']
# 封面：$.[tracks][0]['album']['picUrl']
# 歌手：$.[tracks][0]['artists'][0]['name']
# 歌词：https://music.163.com/api/song/lyric?id={歌曲ID}&lv=1&kv=1&tv=-1