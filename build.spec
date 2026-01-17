# -*- mode: python ; coding: utf-8 -*-

# 导入必要的模块
import os
import mediapipe

# 获取mediapipe的数据路径，以便将其包含在打包中
mediapipe_data_path = os.path.dirname(mediapipe.__file__)

# 加密设置，这里设为None表示不加密
block_cipher = None

# 分析阶段：分析脚本及其依赖关系
a = Analysis(
    # 主程序入口文件
    ['camera_app.py'],
    
    # 模块搜索路径，为空表示使用默认路径
    pathex=[],
    
    # 额外的二进制文件，一般为空
    binaries=[],
    
    # 数据文件：将外部文件包含到打包的exe中
    datas=[
        # 包含mediapipe的数据文件，这是解决"FileNotFoundError"的关键
        # 将mediapipe的整个数据目录复制到打包后的程序中
        (mediapipe_data_path, 'mediapipe'),
    ],
    
    # 隐藏导入：PyInstaller可能无法自动检测到的模块
    # 这些模块需要手动列出，确保它们被包含在最终的exe中
    hiddenimports=[
        'mediapipe',  # MediaPipe库
        'mediapipe.python.solutions.hands',  # MediaPipe手部检测模块
        'mediapipe.python.solutions.drawing_utils',  # MediaPipe绘图工具
        'mediapipe.python.solutions.drawing_styles',  # MediaPipe绘图样式
        'cv2',  # OpenCV库
        'numpy',  # 数值计算库
        'pyautogui',  # 自动化控制库
        'PySide6.QtCore',  # PySide6核心模块
        'PySide6.QtGui',  # PySide6图形界面模块
        'PySide6.QtWidgets',  # PySide6窗口组件模块
    ],
    
    # 钩子脚本路径，一般为空
    hookspath=[],
    
    # 钩子配置
    hooksconfig={},
    
    # 运行时钩子
    runtime_hooks=[],
    
    # 排除的模块，一般为空
    excludes=[],
    
    # Windows特定设置
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    
    # 加密设置
    cipher=block_cipher,
    
    # 归档设置
    noarchive=False,
)

# 创建PYZ归档，包含Python字节码
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 创建最终的EXE文件
exe = EXE(
    # 输入源
    pyz,  # PYZ归档
    a.scripts,  # 脚本文件
    a.binaries,  # 二进制文件
    a.zipfiles,  # ZIP文件
    a.datas,  # 数据文件
    
    # 依赖项
    [],
    
    # EXE配置参数
    name='CameraMouseControl',  # 生成的exe文件名
    
    debug=False,  # 是否显示调试信息
    
    bootloader_ignore_signals=False,  # 引导程序是否忽略信号
    
    strip=False,  # 是否移除符号表
    
    upx=True,  # 是否使用UPX压缩
    
    upx_exclude=[],  # UPX排除列表
    
    runtime_tmpdir=None,  # 运行时临时目录
    
    console=False,  # 是否显示控制台窗口 (False = 隐藏控制台窗口)
    
    disable_windowed_traceback=False,  # 是否禁用窗口模式下的回溯
    
    argv_emulation=False,  # 是否模拟argv参数传递
    
    target_arch=None,  # 目标架构
    
    codesign_identity=None,  # 代码签名身份
    
    entitlements_file=None,  # 权限文件
    
    icon=None,  # 图标文件路径 (如果有图标文件，可以在此指定)
)