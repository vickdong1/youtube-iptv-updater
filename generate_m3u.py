#!/usr/bin/env python3
# generate_m3u.py
# 自动刷新 YouTube cookies 并生成 IPTV 播放列表
# 适配新版 yt-dlp (>=2024.10)，优先使用 --write-cookies

import subprocess, os, sys, time, datetime, shutil

COOKIES_FILE = "cookies.txt"
CHANNELS_FILE = "channels.txt"
OUTPUT_FILE = "youtube_live.m3u"
BROWSER = "chrome"
YT_DLP = shutil.which("yt-dlp") or "yt-dlp"

def log(msg):
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

def get_ytdlp_version():
    try:
        out = subprocess.check_output([YT_DLP, "--version"], text=True).strip()
        return out
    except:
        return "unknown"

def refresh_cookies():
    """自动从浏览器提取 cookie"""
    log("🍪 正在从浏览器提取 YouTube 登录 cookie ...")
    version = get_ytdlp_version()
    log(f"yt-dlp 版本: {version}")

    # 优先使用新版参数
    cmd = [YT_DLP, "--cookies-from-browser", BROWSER, "--write-cookies", COOKIES_FILE,
           "--skip-download", "https://www.youtube.com"]

    # 如果 --write-cookies 不支持，就改用 --dump-cookies
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if "no such option" in proc.stderr.lower():
            cmd = [YT_DLP, "--cookies-from-browser", BROWSER, "--dump-cookies", COOKIES_FILE,
                   "--skip-download", "https://www.youtube.com"]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except FileNotFoundError:
        log("❌ 未找到 yt-dlp，请先运行 pip install yt-dlp")
        return False
    except Exception as e:
        log(f"❌ 提取 cookie 出错: {e}")
        return False

    if os.path.exists(COOKIES_FILE) and os.path.getsize(COOKIES_FILE) > 0:
        log(f"✅ 成功导出 cookies.txt ({os.path.getsize(COOKIES_FILE)} 字节)")
        return True
    else:
        log(f"⚠️ 提取 cookie 失败：{proc.stderr.strip() or proc.stdout.strip()}")
        return False

def read_channels():
    if not os.path.exists(CHANNELS_FILE):
        log(f"❌ 未找到 {CHANNELS_FILE}")
        sys.exit(1)
    channels = []
    for line in open(CHANNELS_FILE, "r", encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "#" in line:
            url, name = line.split("#", 1)
            channels.append((url.strip(), name.strip()))
        else:
            channels.append((line, line))
    return channels

def get_stream(url):
    """使用 cookie 获取 m3u8 链接"""
    try:
        cmd = [YT_DLP, "-g", "--cookies", COOKIES_FILE, url]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if proc.returncode == 0 and proc.stdout.strip():
            for line in proc.stdout.splitlines():
                if "m3u8" in line or "manifest.googlevideo.com" in line:
                    return line.strip()
            return proc.stdout.splitlines()[0].strip()
        else:
            err = proc.stderr.strip().splitlines()[-1] if proc.stderr else "未知错误"
            log(f"yt-dlp 抓取失败: {err}")
            return None
    except Exception as e:
        log(f"⚠️ 抓流异常: {e}")
        return None

def generate_m3u(channels):
    lines = ["#EXTM3U"]
    success = 0
    for url, name in channels:
        log(f"▶ 正在获取：{name} ({url})")
        stream = get_stream(url)
        if stream:
            lines.append(f'#EXTINF:-1 group-title="YouTube",{name}')
            lines.append(stream)
            log(f"✅ {name} 成功")
            success += 1
        else:
            log(f"❌ {name} 失败")
        time.sleep(1)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    log(f"📺 已生成 {OUTPUT_FILE} ({success}/{len(channels)} 成功)")

def main():
    log("========== 开始运行 generate_m3u ==========")
    ok = refresh_cookies()
    if not ok:
        log("⚠️ cookie 提取失败，将尝试使用现有 cookies.txt（如果有）")
    else:
        log("✅ cookie 已刷新")

    if not os.path.exists(COOKIES_FILE):
        log("❌ 没有有效 cookie，YouTube 将拒绝请求。请先登录浏览器再运行脚本。")
        sys.exit(1)

    channels = read_channels()
    generate_m3u(channels)
    log("✅ 所有频道处理完成")

if __name__ == "__main__":
    main()
