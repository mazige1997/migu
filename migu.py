import requests
import json
import re
import os
from urllib.parse import urlparse

def get_ip_port_from_api(url):
    """
    从API接口获取IP和端口信息
    接口返回JSON格式：{"data": "http://ip:port/path [resolution]\n...", ...}
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            ip_port_list = []
            
            # 从data字段提取所有链接
            links_text = data.get('data', '')
            links = links_text.strip().split('\n')
            
            for link in links:
                link = link.strip()
                if not link:
                    continue
                
                # 提取URL部分（去除分辨率信息）
                # 格式示例: http://115.191.9.43:1234/608807420 [1280x720]
                url_match = re.search(r'(https?://[^\s]+)', link)
                if url_match:
                    full_url = url_match.group(1)
                    
                    # 解析URL获取协议、IP和端口
                    parsed = urlparse(full_url)
                    if parsed.hostname and parsed.port:
                        ip_port_list.append({
                            'ip': parsed.hostname,
                            'port': parsed.port,
                            'scheme': parsed.scheme,
                            'full_url': full_url
                        })
                    elif parsed.hostname:
                        # 如果没有端口，使用默认端口
                        ip_port_list.append({
                            'ip': parsed.hostname,
                            'port': 80 if parsed.scheme == 'http' else 443,
                            'scheme': parsed.scheme,
                            'full_url': full_url
                        })
            
            if ip_port_list:
                print(f"成功获取到 {len(ip_port_list)} 个IP:端口组合")
                return ip_port_list
            else:
                print("从API响应中未找到有效的IP:端口信息")
                return None
        else:
            print(f"API请求失败，HTTP状态码: {response.status_code}")
            return None
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return None
    except Exception as e:
        print(f"获取API数据时发生错误: {e}")
        return None

def get_channel_path(channel_url):
    """
    从频道URL中提取路径部分
    示例: http://:1234/608807420 -> /608807420
    """
    # 匹配路径部分
    match = re.search(r'/(\d+)$', channel_url)
    if match:
        return f"/{match.group(1)}"
    return None

def generate_m3u_with_dynamic_ips(channel_text, api_url):
    """
    为每个频道生成M3U条目，每个条目使用API返回的不同IP:端口
    """
    print(f"正在从API获取IP:端口信息: {api_url}")
    ip_port_list = get_ip_port_from_api(api_url)
    
    if not ip_port_list:
        print("无法获取IP:端口信息，脚本终止")
        return ""
    
    # 解析频道文本
    lines = channel_text.strip().split('\n')
    
    m3u_content = "#EXTM3U\n"
    m3u_content += "# 咪咕直播源 - 动态IP生成\n"
    m3u_content += "# 更新时间: 2026-04-12\n"
    m3u_content += f"# 源数量: {len(ip_port_list)} 个\n"
    
    # 显示所有获取到的IP:端口
    m3u_content += "# 可用源:\n"
    for i, item in enumerate(ip_port_list, 1):
        m3u_content += f"#   {i}. {item['ip']}:{item['port']}\n"
    m3u_content += "\n"
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 处理分组行
        if line.startswith('#genre#'):
            m3u_content += f"{line}\n"
            continue
        
        # 处理频道行
        parts = line.split(',', 1)
        if len(parts) == 2:
            channel_name = parts[0]
            channel_url = parts[1]
            
            # 提取频道路径
            channel_path = get_channel_path(channel_url)
            if not channel_path:
                print(f"警告: 无法从 {channel_url} 提取路径")
                continue
            
            # 为每个IP:端口组合生成一个条目
            for item in ip_port_list:
                ip = item['ip']
                port = item['port']
                scheme = item['scheme']
                
                # 构建完整的URL
                full_url = f"{scheme}://{ip}:{port}{channel_path}"
                
                # 在频道名后添加IP:端口标识
                display_name = f"{channel_name} [{ip}:{port}]"
                m3u_content += f"#EXTINF:-1,{display_name}\n"
                m3u_content += f"{full_url}\n"
    
    return m3u_content

def main():
    # API接口URL
    api_url = "https://sygatrvnoylq.ap-northeast-1.clawcloudrun.com/2026.txt?code=0330"
    
    # 频道列表文本
    channel_text = """#genre#
CCTV1综合,http://:1234/608807420
CCTV2财经,http://:1234/631780532
CCTV3综艺,http://:1234/624878271
CCTV4中文国际,http://:1234/631780421
CCTV5体育,http://:1234/641886683
CCTV5+体育赛事,http://:1234/641886773
CCTV6电影,http://:1234/624878396
CCTV7国防军事,http://:1234/673168121
CCTV8电视剧,http://:1234/624878356
CCTV9纪录,http://:1234/673168140
CCTV10科教,http://:1234/624878405
CCTV11戏曲,http://:1234/667987558
CCTV12社会与法,http://:1234/673168185
CCTV13新闻,http://:1234/608807423
CCTV14少儿,http://:1234/624878440
CCTV15音乐,http://:1234/673168223
CCTV17农业农村,http://:1234/673168256
CCTV4欧洲,http://:1234/608807419
CCTV4美洲,http://:1234/608807416
CGTN外语纪录,http://:1234/609006487
CGTN阿拉伯语,http://:1234/609154345
CGTN西班牙语,http://:1234/609006450
CGTN法语,http://:1234/609006476
CGTN俄语,http://:1234/609006446
老故事,http://:1234/884121956
发现之旅,http://:1234/624878970
中学生,http://:1234/708869532
CGTN,http://:1234/609017205
咪咕体育,#genre#
赛事最经典,http://:1234/646596895
体坛名栏汇,http://:1234/629943305
四海钓鱼,http://:1234/637444975
陕西体育休闲频道,http://:1234/956909356
武术世界,http://:1234/958475359
快乐垂钓,http://:1234/961930263
辽宁广播电视台体育休闲频道,http://:1234/962067526
咪咕卫视,#genre#
东方卫视,http://:1234/651632648
江苏卫视,http://:1234/623899368
广东卫视,http://:1234/608831231
北京卫视,http://:1234/630287636
辽宁卫视,http://:1234/630291707
河北卫视,http://:1234/962042070
江西卫视,http://:1234/783847495
河南卫视,http://:1234/790187291
陕西卫视,http://:1234/738910838
大湾区卫视,http://:1234/608917627
湖北卫视,http://:124.71.194.147:1234/947472496
吉林卫视,http://:1234/947472500
青海卫视,http://:1234/947472506
东南卫视,http://:1234/849116810
海南卫视,http://:1234/947472502
海峡卫视,http://:1234/849119120
中国农林卫视,http://:1234/956904896
兵团卫视,http://:1234/956923145
宁夏卫视,http://:1234/738910535
重庆卫视,http://:1234/738910914
三沙卫视,http://:1234/961023778
咪咕地方,#genre#
南京新闻综合频道,http://:1234/838109047
南京教科频道,http://:1234/838153729
南京十八频道,http://:1234/838151753
体育休闲频道,http://:1234/626064707
江苏城市频道,http://:1234/626064714
江苏国际,http://:1234/626064674
江苏教育,http://:124.71.194.147:1234/628008321
江苏影视频道,http://:1234/626064697
江苏综艺频道,http://:1234/626065193
公共新闻频道,http://:1234/626064693
盐城新闻综合,http://:1234/639731825
淮安新闻综合,http://:1234/639731826
泰州新闻综合,http://:1234/639731818
连云港新闻综合,http://:1234/639731715
宿迁新闻综合,http://:1234/639731832
徐州新闻综合,http://:1234/639731747
优漫卡通频道,http://:1234/626064703
上海新闻综合,http://:1234/651632657
上视东方影视,http://:1234/617290047
上海第一财经,http://:1234/608780988
江阴新闻综合,http://:1234/955227979
南通新闻综合,http://:1234/955227985
宜兴新闻综合,http://:1234/955227996
溧水新闻综合,http://:1234/639737327
陕西银龄频道,http://:1234/956909362
陕西都市青春频道,http://:1234/956909358
陕西秦腔频道,http://:1234/956909303
陕西新闻资讯频道,http://:1234/956909289
财富天下,http://:1234/956923159
镇江新闻综合,http://:1234/639731783
辽宁广播电视台公共频道,http://:1234/962045223
辽宁广播电视台生活频道,http://:1234/962045226
辽宁广播电视台影视剧频道,http://:1234/962067517
宁夏广播电视台文旅频道,http://:1234/962067523
宁夏广播电视台经济频道,http://:1234/962067520
咪咕影视,#genre#
经典深圳旁边电影,http://:1234/625703337
抗战经典影片,http://:1234/617432318
新片放映厅,http://:1234/619495952
CHC影迷电影,http://:1234/952383261
CHC动作电影,http://:1234/644368714
CHC家庭影院,http://:1234/644368373
和美乡途轮播台,http://:1234/713591450
南方影视,http://:1234/614961829
咪咕天气,#genre#
中国天气,http://:1234/959986621
咪咕教育,#genre#
CETV1,http://:1234/923287154
CETV2,http://:1234/923287211
CETV4,http://:1234/923287339
山东教育,http://:1234/609154353
咪咕综艺,#genre#
最强综艺趴,http://:1234/629942228
咪咕少儿,#genre#
嘉佳卡通,http://:1234/614952364
经典动画大集合,http://:1234/629942219
新动漫,http://:1234/961930269
咪咕纪实,#genre#
新动力量创一流,http://:1234/713589837
中华特产,http://:1234/959986618
环球旅游,http://:124.71.194.147:1234/958475356
茶,http://:1234/961930369"""
    
    print("="*60)
    print("咪咕直播源生成脚本 - 动态IP:端口版本")
    print("="*60)
    
    # 统计原始频道数量
    original_channels = len([line for line in channel_text.split('\n') 
                           if line and not line.startswith('#genre#')])
    
    print(f"原始频道数: {original_channels} 个")
    print(f"API接口: {api_url}")
    print()
    
    # 生成M3U内容
    print("正在生成M3U格式的播放列表...")
    m3u_content = generate_m3u_with_dynamic_ips(channel_text, api_url)
    
    if not m3u_content:
        print("✗ 生成M3U内容失败，脚本终止。")
        return
    
    # 计算生成的条目数
    ip_count = m3u_content.count("# 可用源:")
    if ip_count:
        # 提取IP数量
        ip_match = re.search(r"# 源数量: (\d+) 个", m3u_content)
        if ip_match:
            ip_num = int(ip_match.group(1))
            total_entries = original_channels * ip_num
            print(f"✓ 获取到IP:端口组合: {ip_num} 个")
            print(f"✓ 最终条目数: {total_entries} 个")
    
    print()
    
    # 保存到migu.m3u文件
    print("正在保存到 migu.m3u 文件...")
    print("-"*40)
    
    try:
        with open("migu.m3u", 'w', encoding='utf-8') as f:
            f.write(m3u_content)
        
        # 获取文件信息
        file_size = os.path.getsize("migu.m3u")
        line_count = 0
        with open("migu.m3u", 'r', encoding='utf-8') as f:
            line_count = len(f.readlines())
        
        print("✓" + "="*60)
        print(f"✓ 文件已成功保存: migu.m3u")
        print(f"✓ 文件大小: {file_size:,} 字节")
        print(f"✓ 行数: {line_count} 行")
        print(f"✓ 保存路径: {os.path.abspath('migu.m3u')}")
        print("✓" + "="*60)
        print()
        
        # 显示文件内容预览
        print("文件内容预览:")
        print("-"*40)
        
        with open("migu.m3u", 'r', encoding='utf-8') as f:
            # 显示前30行
            for i in range(30):
                line = f.readline()
                if not line:
                    break
                
                # 高亮显示不同的行类型
                if line.startswith('#EXTM3U'):
                    print(f"\033[92m{line.rstrip()}\033[0m")  # 绿色
                elif line.startswith('#'):
                    if line.startswith('#genre#'):
                        print(f"\033[93m{line.rstrip()}\033[0m")  # 黄色
                    elif '可用源:' in line:
                        print(f"\033[96m{line.rstrip()}\033[0m")  # 青色
                    else:
                        print(f"\033[90m{line.rstrip()}\033[0m")  # 灰色
                else:
                    print(line.rstrip())
        
        print(f"... (共 {line_count} 行，显示前30行)")
        print("-"*40)
        print("✓ 脚本执行完成！您可以在当前目录找到 migu.m3u 文件")
        print()
        print("文件格式说明:")
        print("  - 每个频道会根据API返回的IP:端口数量重复出现")
        print("  - 频道名后会显示IP:端口，如: CCTV1综合 [115.191.9.43:1234]")
        print("  - 端口不固定，根据API返回的实际端口生成")
        print("  - 标准M3U格式，支持大多数播放器")
        
    except Exception as e:
        print(f"✗ 文件保存失败: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ 用户中断脚本执行。")
    except Exception as e:
        print(f"\n✗ 脚本执行过程中发生错误: {e}")