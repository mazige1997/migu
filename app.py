import requests, subprocess, threading, time, os, datetime, hashlib, json, re
from queue import Queue
from flask import Flask, request, jsonify, Response
from urllib.parse import urlparse

REMOTE_URL = "https://123.tv1288.xyz/migu.txt"
TXT_FILE = "2026.txt"  # 保留生成的txt文件
M3U_FILE = "migu.m3u"  # 最终输出的M3U文件
ACCESS_FILE = "code.txt"
LOG_FILE = "update.log"
RESULT_HASH = "result.hash"
IP_FILE = "ip.json"

START_TIME_STR = "2026-03-20 00:00:00"
DEFAULT_CODE = "2026"

app = Flask(__name__)

if not os.path.exists(ACCESS_FILE):
    open(ACCESS_FILE, "w").write(DEFAULT_CODE)

# 频道名称映射
CHANNEL_NAMES = {
    "608807420": "CCTV1综合",
    "631780532": "CCTV2财经",
    "624878271": "CCTV3综艺",
    "631780421": "CCTV4中文国际",
    "641886683": "CCTV5体育",
    "641886773": "CCTV5+体育赛事",
    "624878396": "CCTV6电影",
    "673168121": "CCTV7国防军事",
    "624878356": "CCTV8电视剧",
    "673168140": "CCTV9纪录",
    "624878405": "CCTV10科教",
    "667987558": "CCTV11戏曲",
    "673168185": "CCTV12社会与法",
    "608807423": "CCTV13新闻",
    "624878440": "CCTV14少儿",
    "673168223": "CCTV15音乐",
    "673168256": "CCTV17农业农村",
    "608807419": "CCTV4欧洲",
    "608807416": "CCTV4美洲",
    "609006487": "CGTN外语纪录",
    "609154345": "CGTN阿拉伯语",
    "609006450": "CGTN西班牙语",
    "609006476": "CGTN法语",
    "609006446": "CGTN俄语",
    "884121956": "老故事",
    "624878970": "发现之旅",
    "708869532": "中学生",
    "609017205": "CGTN",
    "646596895": "赛事最经典",
    "629943305": "体坛名栏汇",
    "637444975": "四海钓鱼",
    "956909356": "陕西体育休闲频道",
    "958475359": "武术世界",
    "961930263": "快乐垂钓",
    "962067526": "辽宁广播电视台体育休闲频道",
    "651632648": "东方卫视",
    "623899368": "江苏卫视",
    "608831231": "广东卫视",
    "630287636": "北京卫视",
    "630291707": "辽宁卫视",
    "962042070": "河北卫视",
    "783847495": "江西卫视",
    "790187291": "河南卫视",
    "738910838": "陕西卫视",
    "608917627": "大湾区卫视",
    "947472496": "湖北卫视",
    "947472500": "吉林卫视",
    "947472506": "青海卫视",
    "849116810": "东南卫视",
    "947472502": "海南卫视",
    "849119120": "海峡卫视",
    "956904896": "中国农林卫视",
    "956923145": "兵团卫视",
    "738910535": "宁夏卫视",
    "738910914": "重庆卫视",
    "961023778": "三沙卫视",
    "838109047": "南京新闻综合频道",
    "838153729": "南京教科频道",
    "838151753": "南京十八频道",
    "626064707": "体育休闲频道",
    "626064714": "江苏城市频道",
    "626064674": "江苏国际",
    "628008321": "江苏教育",
    "626064697": "江苏影视频道",
    "626065193": "江苏综艺频道",
    "626064693": "公共新闻频道",
    "639731825": "盐城新闻综合",
    "639731826": "淮安新闻综合",
    "639731818": "泰州新闻综合",
    "639731715": "连云港新闻综合",
    "639731832": "宿迁新闻综合",
    "639731747": "徐州新闻综合",
    "626064703": "优漫卡通频道",
    "651632657": "上海新闻综合",
    "617290047": "上视东方影视",
    "608780988": "上海第一财经",
    "955227979": "江阴新闻综合",
    "955227985": "南通新闻综合",
    "955227996": "宜兴新闻综合",
    "639737327": "溧水新闻综合",
    "956909362": "陕西银龄频道",
    "956909358": "陕西都市青春频道",
    "956909303": "陕西秦腔频道",
    "956909289": "陕西新闻资讯频道",
    "956923159": "财富天下",
    "639731783": "镇江新闻综合",
    "962045223": "辽宁广播电视台公共频道",
    "962045226": "辽宁广播电视台生活频道",
    "962067517": "辽宁广播电视台影视剧频道",
    "962067523": "宁夏广播电视台文旅频道",
    "962067520": "宁夏广播电视台经济频道",
    "625703337": "经典深圳旁边电影",
    "617432318": "抗战经典影片",
    "619495952": "新片放映厅",
    "952383261": "CHC影迷电影",
    "644368714": "CHC动作电影",
    "644368373": "CHC家庭影院",
    "713591450": "和美乡途轮播台",
    "614961829": "南方影视",
    "959986621": "中国天气",
    "923287154": "CETV1",
    "923287211": "CETV2",
    "923287339": "CETV4",
    "609154353": "山东教育",
    "629942228": "最强综艺趴",
    "614952364": "嘉佳卡通",
    "629942219": "经典动画大集合",
    "961930269": "新动漫",
    "713589837": "新动力量创一流",
    "959986618": "中华特产",
    "958475356": "环球旅游",
    "961930369": "茶"
}

def get_code():
    return open(ACCESS_FILE).read().strip()

def bj_time():
    return datetime.datetime.utcnow() + datetime.timedelta(hours=8)

def today_str():
    return bj_time().strftime("%Y-%m-%d")

def yesterday_str():
    return (bj_time() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

# ===== IP统计 =====
def load_ip():
    if not os.path.exists(IP_FILE):
        return {}
    return json.load(open(IP_FILE))

def save_ip(data):
    json.dump(data, open(IP_FILE, "w"))

def record_ip(ip):
    data = load_ip()
    now = int(time.time())

    # 清理48小时外
    for i in list(data.keys()):
        if now - data[i] > 172800:
            del data[i]

    data[ip] = now
    save_ip(data)

def get_ip_stats():
    data = load_ip()
    today = today_str()
    yesterday = yesterday_str()

    t_count = 0
    y_count = 0

    for ip, t in data.items():
        d = datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d")
        if d == today:
            t_count += 1
        elif d == yesterday:
            y_count += 1

    return t_count, y_count

# =================

def log_update():
    now = bj_time().strftime("%Y-%m-%d %H:%M:%S")
    logs = []
    if os.path.exists(LOG_FILE):
        logs = open(LOG_FILE).read().splitlines()
    logs.insert(0, now)
    logs = logs[:5]
    open(LOG_FILE, "w").write("\n".join(logs))

def get_logs():
    if not os.path.exists(LOG_FILE):
        return []
    return open(LOG_FILE).read().splitlines()

def get_runtime():
    start = datetime.datetime.strptime(START_TIME_STR, "%Y-%m-%d %H:%M:%S")
    now = bj_time()
    delta = now - start
    d = delta.days
    h = delta.seconds // 3600
    m = (delta.seconds % 3600) // 60
    return f"{d}天 {h}小时 {m}分钟"

def fetch():
    try:
        r = requests.get(REMOTE_URL, timeout=10)
        return [i.strip() for i in r.text.splitlines() if i.strip()]
    except:
        return []

def check(url):
    try:
        r = subprocess.run(["ffprobe", "-i", url],
                           stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                           text=True, timeout=15)
        for line in r.stderr.splitlines():
            if "Video:" in line and "x" in line:
                for p in line.split(","):
                    if "x" in p:
                        res = p.strip().split(" ")[0]
                        if res in ["1920x1080", "1280x720"]:
                            return url, res
    except:
        return None

def calc_hash(content):
    return hashlib.md5(content.encode()).hexdigest()

def get_channel_id_from_url(url):
    """从URL中提取频道ID"""
    # 匹配 /数字 格式的路径
    match = re.search(r'/(\d+)$', url)
    if match:
        return match.group(1)
    return None

def get_channel_name(url):
    """根据URL获取频道名称"""
    channel_id = get_channel_id_from_url(url)
    if channel_id and channel_id in CHANNEL_NAMES:
        return CHANNEL_NAMES[channel_id]
    return f"频道_{channel_id}" if channel_id else "未知频道"

def run_check():
    """执行检查，生成txt文件，然后生成m3u文件"""
    data = fetch()
    if not data:
        print(f"[{bj_time()}] 警告: 远程数据源返回空")
        return

    q = Queue()
    for i in data:
        q.put(i)

    res = []
    def worker():
        while not q.empty():
            u = q.get()
            r = check(u)
            if r:
                res.append(r)
            q.task_done()

    for _ in range(10):
        threading.Thread(target=worker).start()
    q.join()

    # 如果没有获取到任何可用的URL
    if not res:
        print(f"[{bj_time()}] 警告: 没有获取到可用的URL")
        return
    
    # 1. 生成2026.txt文件
    max_len = max([len(u) for u, _ in res]) if res else 0
    
    txt_content = ""
    for url, resolution in res:
        space = " " * (max_len - len(url) + 2)
        txt_content += f"{url}{space}[{resolution}]\n"
    
    new_hash = calc_hash(txt_content)
    
    if os.path.exists(RESULT_HASH):
        old_hash = open(RESULT_HASH).read().strip()
        if new_hash == old_hash:
            print(f"[{bj_time()}] 信息: 内容未变化，跳过更新")
            return
    
    open(RESULT_HASH, "w").write(new_hash)
    
    # 保存2026.txt文件
    with open(TXT_FILE, "w", encoding='utf-8') as f:
        f.write(txt_content)
    
    print(f"[{bj_time()}] 已生成 {TXT_FILE}，包含 {len(res)} 个频道")
    
    # 2. 基于2026.txt生成migu.m3u文件
    generate_m3u_from_txt()
    
    log_update()

def generate_m3u_from_txt():
    """从2026.txt文件生成migu.m3u文件"""
    if not os.path.exists(TXT_FILE):
        print(f"[{bj_time()}] 错误: {TXT_FILE} 不存在，无法生成M3U文件")
        return False
    
    try:
        with open(TXT_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 生成M3U格式的内容
        m3u_content = "#EXTM3U\n"
        m3u_content += f"# 咪咕直播源 - 自动生成\n"
        m3u_content += f"# 更新时间: {bj_time().strftime('%Y-%m-%d %H:%M:%S')}\n"
        m3u_content += f"# 频道数量: {len(lines)} 个\n\n"
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 解析每一行，格式: URL     [分辨率]
            # 使用正则表达式提取URL和分辨率
            match = re.search(r'^(https?://[^\s]+)\s+\[(\d+x\d+)\]$', line)
            if match:
                url = match.group(1)
                resolution = match.group(2)
                channel_name = get_channel_name(url)
                m3u_content += f"#EXTINF:-1, {channel_name} [{resolution}]\n"
                m3u_content += f"{url}\n"
        
        # 保存migu.m3u文件
        with open(M3U_FILE, "w", encoding='utf-8') as f:
            f.write(m3u_content)
        
        print(f"[{bj_time()}] 已生成 {M3U_FILE}，包含 {len(lines)} 个频道")
        return True
        
    except Exception as e:
        print(f"[{bj_time()}] 生成M3U文件时出错: {e}")
        return False

def loop():
    while True:
        run_check()
        time.sleep(1800)

# ===== 前端页面 =====
HTML = '''
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>系统面板</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{
margin:0;
font-family:Arial;
background:linear-gradient(135deg,#020617,#0f172a);
color:#e2e8f0;
}

.container{
max-width:1000px;
margin:auto;
padding:20px;
}

.card{
background:rgba(15,23,42,0.7);
border-radius:15px;
padding:20px;
margin-top:20px;
box-shadow:0 0 20px rgba(0,255,255,0.2);
}

input{
width:80%;
padding:12px;
border-radius:10px;
border:none;
margin-top:10px;
}

button{
padding:12px 20px;
border:none;
border-radius:10px;
background:#06b6d4;
color:#fff;
cursor:pointer;
}

pre{
white-space:pre-wrap;
word-break:break-all;
font-size:14px;
}

.title{
font-size:26px;
text-align:center;
margin-top:40px;
}

.floating{
position:fixed;
right:20px;
bottom:20px;
background:rgba(0,255,255,0.15);
padding:10px 15px;
border-radius:10px;
font-size:14px;
backdrop-filter:blur(10px);
box-shadow:0 0 10px rgba(0,255,255,0.5);
}
</style>
</head>

<body>
<div class="container">

<div id="login">
<div class="title">访问验证</div>
<div class="card" style="text-align:center">
<input type="password" id="c" placeholder="输入访问码">
<br><br>
<button onclick="go()">进入系统</button>
</div>
</div>

<div id="panel" style="display:none">
<div class="title">系统状态面板</div>

<div class="card">
<h3>M3U播放列表</h3>
<pre id="data"></pre>
</div>

<div class="card">
<h3>使用说明</h3>
<div id="tip"></div>
</div>

<div class="card">
<h3>运行状态</h3>
<div id="info"></div>
</div>

</div>
</div>

<div id="float" class="floating" style="display:none">
公众号：潇雨萌萌
</div>

<script>
function go(){
 let c=document.getElementById("c").value;
 fetch("/migu.m3u?code="+c).then(r=>{
   if(r.headers.get("content-type")?.includes("application/json")) {
     return r.json().then(d=>{
       if(d.error){alert("访问码错误");return;}
       alert("获取数据出错: " + d.message);
       return;
     });
   } else {
     return r.text().then(data=>{
       document.getElementById("login").style.display="none";
       document.getElementById("panel").style.display="block";
       document.getElementById("float").style.display="block";

       document.getElementById("data").textContent=data;

       // 尝试提取第一个URL用于提示
       let lines = data.split('\\n');
       for(let line of lines) {
         if(line.startsWith('http')) {
           let url = new URL(line);
           let host = url.hostname;
           let port = url.port;
           document.getElementById("tip").innerHTML=
           "播放器M3U链接：<br><code>/migu.m3u?code="+c+"</code><br><br>" +
           "示例URL：<br><code>"+line+"</code>";
           break;
         }
       }

       // 获取运行状态信息
       fetch("/info?code="+c).then(r=>r.json()).then(d=>{
         if(!d.error) {
           document.getElementById("info").innerHTML=
           "运行时长："+d.runtime+"<br><br>最近更新：<br>"+d.logs.join("<br>");
         }
       });
     });
   }
 }).catch(e=>{
   alert("请求失败: " + e);
 });
}
</script>

</body>
</html>
'''

@app.route("/")
def index():
    return HTML

@app.route("/migu.m3u")
def migu_m3u():
    code = request.args.get("code", "")
    
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    record_ip(ip)
    
    if not code:
        return HTML
    
    if code != get_code():
        return jsonify({"error": 1, "message": "无效的code"})
    
    if os.path.exists(M3U_FILE):
        m3u_content = open(M3U_FILE, 'r', encoding='utf-8').read()
        return Response(
            m3u_content,
            mimetype="audio/x-mpegurl",
            headers={
                "Content-Disposition": "attachment; filename=migu.m3u",
                "Cache-Control": "no-cache, max-age=0"
            }
        )
    else:
        return jsonify({
            "error": 2,
            "message": "M3U文件不存在，请等待首次更新完成",
            "logs": get_logs(),
            "runtime": get_runtime()
        })

@app.route("/info")
def info():
    code = request.args.get("code", "")
    
    if not code:
        return jsonify({"error": 1, "message": "需要code参数"})
    
    if code != get_code():
        return jsonify({"error": 1, "message": "无效的code"})
    
    return jsonify({
        "logs": get_logs(),
        "runtime": get_runtime()
    })

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        c = request.form.get("code", "")
        if c:
            open(ACCESS_FILE, "w").write(c)
    
    today, yesterday = get_ip_stats()
    
    return f'''
    <body style="background:#020617;color:#0ff;text-align:center;padding-top:80px">
    <h2>后台管理</h2>
    
    <h3>修改访问码</h3>
    <form method="post">
    <input name="code" value="{get_code()}" style="padding:10px"><br><br>
    <button style="padding:10px;background:#06b6d4;border:none">保存</button>
    </form>
    
    <hr style="margin:40px">
    
    <h3>访问统计（去重IP）</h3>
    <p>今日访问：{today} 个IP</p>
    <p>昨日访问：{yesterday} 个IP</p>
    
    <hr style="margin:40px">
    
    <h3>系统信息</h3>
    <p>运行时长：{get_runtime()}</p>
    <p>最近更新：<br>{"<br>".join(get_logs())}</p>
    <p>TXT文件：{os.path.exists(TXT_FILE)}</p>
    <p>M3U文件：{os.path.exists(M3U_FILE)}</p>
    
    </body>
    '''

if __name__ == "__main__":
    # 首次启动时运行一次检查
    print(f"[{bj_time()}] 系统启动，开始首次检查...")
    run_check()
    
    # 启动后台更新线程
    threading.Thread(target=loop, daemon=True).start()
    
    print(f"[{bj_time()}] 服务启动，监听 0.0.0.0:80")
    app.run(host="0.0.0.0", port=80)