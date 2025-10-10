# FFmpeg 完整安装指南

## 概述

为了使用完整的字幕烧录功能（将字幕直接烧录到视频画面上），需要安装包含 `libass` 支持的 FFmpeg 版本。

## 当前状态检测

检查您的 FFmpeg 是否支持字幕烧录：

```bash
ffmpeg -filters | grep subtitles
```

如果有输出，说明您的 FFmpeg 支持字幕滤镜；如果没有输出，需要重新安装 FFmpeg。

## 安装方法

### macOS

#### 方法1: 直接下载预编译二进制文件（最快，推荐）

```bash
# 1. 下载预编译的 ffmpeg
curl -O https://evermeet.cx/ffmpeg/ffmpeg-6.1.zip

# 2. 解压
unzip ffmpeg-6.1.zip

# 3. 移动到系统路径
sudo mv ffmpeg /usr/local/bin/
sudo chmod +x /usr/local/bin/ffmpeg

# 4. 验证安装
ffmpeg -version
ffmpeg -filters | grep subtitles
```

**优点**: 安装最快，不依赖包管理器  
**缺点**: 需要手动下载更新

预期输出:
```
 ... subtitles          V->V       Render text subtitles onto input video using the libass library.
```

#### 方法2: 使用 Homebrew

```bash
# 卸载现有的 ffmpeg
brew uninstall ffmpeg

# 安装完整版 ffmpeg（包含 libass）
brew install ffmpeg

# 验证安装
ffmpeg -filters | grep subtitles
```

**如果 brew 很慢，可以使用国内镜像加速**:
```bash
# 使用中科大镜像
export HOMEBREW_BOTTLE_DOMAIN=https://mirrors.ustc.edu.cn/homebrew-bottles
export HOMEBREW_API_DOMAIN=https://mirrors.ustc.edu.cn/homebrew-bottles/api

# 或者使用清华镜像
export HOMEBREW_BOTTLE_DOMAIN=https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles

# 然后再安装
brew install ffmpeg
```

#### 方法3: 使用 MacPorts

```bash
# 1. 先安装 MacPorts（如果没有）
# 从 https://www.macports.org/install.php 下载安装

# 2. 安装 ffmpeg（包含 libass 支持）
sudo port install ffmpeg +libass +freetype

# 3. 验证
ffmpeg -filters | grep subtitles
```

#### 方法4: 使用 conda/miniconda

```bash
# 如果已安装 conda
conda install -c conda-forge ffmpeg

# 验证
ffmpeg -filters | grep subtitles
```

⚠️ **注意**: conda 版本可能不包含完整的 libass 支持，建议使用方法1或方法2

### Linux (Ubuntu/Debian)

```bash
# 安装 FFmpeg 及相关库
sudo apt update
sudo apt install ffmpeg libass-dev

# 验证安装
ffmpeg -filters | grep subtitles
```

### Linux (CentOS/RHEL)

```bash
# 启用 EPEL 仓库
sudo yum install epel-release

# 安装 FFmpeg
sudo yum install ffmpeg libass

# 验证安装
ffmpeg -filters | grep subtitles
```

### Windows

1. 下载完整版 FFmpeg:
   - 访问 https://www.gyan.dev/ffmpeg/builds/
   - 下载 "ffmpeg-git-full.7z"

2. 解压并配置环境变量:
   ```
   将 ffmpeg.exe 所在目录添加到系统 PATH
   ```

3. 验证安装:
   ```cmd
   ffmpeg -filters | findstr subtitles
   ```

## 功能对比

### 完整版 FFmpeg（推荐）
- ✅ 字幕直接烧录到视频画面上
- ✅ 支持字幕样式自定义（字体、颜色、大小等）
- ✅ 更好的字幕渲染质量
- ✅ 支持多种字幕格式（VTT, SRT, ASS等）

### 简化版 FFmpeg（备用方案）
- ⚠️ 字幕作为 subtitle track 嵌入
- ⚠️ 需要播放器支持才能显示字幕
- ⚠️ 无法自定义字幕样式
- ⚠️ 某些平台可能不支持

## 当前系统检测

运行以下Python脚本检测您的FFmpeg配置：

```python
import subprocess

def check_ffmpeg_features():
    """检查FFmpeg功能支持"""
    try:
        # 检查FFmpeg版本
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True)
        print("FFmpeg 版本:")
        print(result.stdout.split('\n')[0])
        print()
        
        # 检查字幕滤镜支持
        result = subprocess.run(['ffmpeg', '-filters'], 
                              capture_output=True, text=True)
        if 'subtitles' in result.stdout:
            print("✅ 支持字幕滤镜 (libass)")
            # 提取详细信息
            for line in result.stdout.split('\n'):
                if 'subtitles' in line:
                    print(f"   {line.strip()}")
        else:
            print("❌ 不支持字幕滤镜")
            print("   建议重新安装包含 libass 的 FFmpeg")
        print()
        
        # 检查编解码器支持
        result = subprocess.run(['ffmpeg', '-codecs'], 
                              capture_output=True, text=True)
        print("主要编解码器支持:")
        for codec in ['h264', 'hevc', 'vp9', 'aac', 'mp3']:
            if codec in result.stdout.lower():
                print(f"   ✅ {codec.upper()}")
            else:
                print(f"   ❌ {codec.upper()}")
                
    except FileNotFoundError:
        print("❌ 未找到 FFmpeg")
        print("   请先安装 FFmpeg")
    except Exception as e:
        print(f"❌ 检测出错: {e}")

if __name__ == '__main__':
    check_ffmpeg_features()
```

保存为 `check_ffmpeg.py` 并运行：
```bash
python check_ffmpeg.py
```

## 使用建议

1. **开发/测试环境**: 建议安装完整版 FFmpeg
2. **生产环境**: 必须安装完整版 FFmpeg 以确保最佳用户体验
3. **临时使用**: 如果只是临时使用，备用方案也可以工作

## 常见问题

### Q: 为什么我的 FFmpeg 没有 libass？
A: 某些包管理器（如 conda）提供的 FFmpeg 是精简版，不包含所有编解码器和滤镜。建议使用官方源安装。

### Q: 备用方案的字幕能正常显示吗？
A: 备用方案将字幕作为 subtitle track 嵌入到视频容器中。在支持字幕的播放器（如 VLC、mpv）中可以正常显示，但在某些平台（如移动设备、网页播放器）可能无法显示。

### Q: 如何验证字幕是否正确嵌入？
A: 使用以下命令检查视频流信息：
```bash
ffmpeg -i your_video_with_subs.mp4
```
如果有字幕，会看到类似这样的输出：
```
Stream #0:2(eng): Subtitle: mov_text (tx3g / 0x67337874)
```

### Q: 能否同时生成两种版本？
A: 可以修改代码生成两种版本，但这会增加处理时间和存储空间。

## 相关资源

- [FFmpeg 官方网站](https://ffmpeg.org/)
- [FFmpeg 编译指南](https://trac.ffmpeg.org/wiki/CompilationGuide)
- [libass 项目页面](https://github.com/libass/libass)
- [字幕格式规范](https://www.w3.org/TR/webvtt1/)

## 支持

如果遇到安装问题，请：
1. 检查系统版本和架构
2. 查看 FFmpeg 官方文档
3. 在项目 Issue 中报告问题

