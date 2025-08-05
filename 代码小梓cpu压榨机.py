import tkinter as tk
import customtkinter as ctk
import multiprocessing
import time
import psutil
import webbrowser
import sys
import os
from PIL import Image, ImageTk

# 确保资源路径正确
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# CPU 压力测试工作函数
def cpu_stress_worker(duration, speed_factor, max_usage, stop_event):
    end_time = time.time() + duration
    sleep_time = 0.01 * (100 / speed_factor)
    
    while time.time() < end_time and not stop_event.is_set():
        start = time.time()
        
        # 计算一定量的数学运算
        cycles = int(10000 * (max_usage / 100))
        for _ in range(cycles):
            result = sum(i * i for i in range(100))
        
        # 根据速度调整计算间隔
        elapsed = time.time() - start
        if elapsed < sleep_time:
            time.sleep(sleep_time - elapsed)

class CPUTesterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 应用设置
        self.title("代码小梓-CPU压榨机 ")
        self.geometry("1145x693")
        self.minsize(900, 650)
        
        # 设置应用图标
        try:
            self.iconbitmap(resource_path("icon.ico"))
        except:
            pass
        
        # 默认配置
        self.config = {
            "cpu_threads": multiprocessing.cpu_count(),
            "stress_speed": 100,
            "max_cpu_usage": 100
        }
        
        # 主题设置
        self.current_theme = "dark"
        ctk.set_appearance_mode(self.current_theme)
        
        # 压力测试进程列表
        self.test_processes = []
        self.stop_event = multiprocessing.Event()
        
        # 监控标志
        self.monitoring = False
        self.emergency_stop = False
        
        # 创建GUI组件
        self.create_widgets()
        
        # 开始监控
        self.start_monitoring()
    
    def create_widgets(self):
        # 主容器布局
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # 左侧边栏
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        # 侧边栏标题
        self.sidebar_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="CPU 压力测试",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.sidebar_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # 侧边栏按钮
        self.home_button = ctk.CTkButton(
            self.sidebar_frame, 
            text="主 仪 表 盘",
            command=self.show_dashboard,
            font=ctk.CTkFont(size=14),
            height=40,
            corner_radius=10,
            anchor="w",
            fg_color="transparent"
        )
        self.home_button.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        
        self.logs_button = ctk.CTkButton(
            self.sidebar_frame, 
            text="测 试 日 志",
            command=self.show_logs,
            font=ctk.CTkFont(size=14),
            height=40,
            corner_radius=10,
            anchor="w",
            fg_color="transparent"
        )
        self.logs_button.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        
        self.settings_button = ctk.CTkButton(
            self.sidebar_frame, 
            text="系 统 设 置 查 看",
            command=self.show_settings,
            font=ctk.CTkFont(size=14),
            height=40,
            corner_radius=10,
            anchor="w",
            fg_color="transparent"
        )
        self.settings_button.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        
        # 主题切换
        self.theme_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="主题设置:",
            font=ctk.CTkFont(size=12)
        )
        self.theme_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        
        self.theme_var = ctk.StringVar(value=self.current_theme)
        self.theme_menu = ctk.CTkOptionMenu(
            self.sidebar_frame, 
            values=["dark", "light", "system"],
            command=self.change_theme,
            variable=self.theme_var,
            width=180,
            height=30,
            anchor="center"
        )
        self.theme_menu.grid(row=6, column=0, padx=20, pady=(0, 10))
        
        # 关于按钮
        self.about_button = ctk.CTkButton(
            self.sidebar_frame, 
            text="关 于 作 者",
            command=self.show_about,
            font=ctk.CTkFont(size=12),
            height=30,
            corner_radius=10,
            fg_color="transparent"
        )
        self.about_button.grid(row=7, column=0, padx=20, pady=(0, 20))
        
        # 主内容区域
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # 创建不同的内容页面
        self.create_dashboard()
        self.create_logs_page()
        self.create_settings_page()
        
        # 默认显示仪表盘
        self.show_dashboard()
    
    def create_dashboard(self):
        """创建仪表盘页面"""
        self.dashboard_frame = ctk.CTkFrame(self.main_frame, corner_radius=10, fg_color="transparent")
        self.dashboard_frame.grid_columnconfigure(0, weight=1)
        self.dashboard_frame.grid_rowconfigure(1, weight=1)
        
        # 标题
        title_frame = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        ctk.CTkLabel(
            title_frame, 
            text="CPU 性能监控",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")
        
        # CPU 信息卡片
        info_frame = ctk.CTkFrame(self.dashboard_frame, corner_radius=15)
        info_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_rowconfigure(2, weight=1)
        
        # 第一行信息
        row1 = ctk.CTkFrame(info_frame, fg_color="transparent")
        row1.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        ctk.CTkLabel(
            row1, 
            text=f"CPU 核心数: {multiprocessing.cpu_count()}",
            font=ctk.CTkFont(size=16)
        ).pack(side="left", padx=10)
        
        # 第二行信息
        row2 = ctk.CTkFrame(info_frame, fg_color="transparent")
        row2.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(
            row2, 
            text="当前 CPU 使用率:",
            font=ctk.CTkFont(size=16)
        ).pack(side="left", padx=10)
        
        self.cpu_usage_var = ctk.StringVar(value="0.0%")
        ctk.CTkLabel(
            row2, 
            textvariable=self.cpu_usage_var,
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        # 进度条
        progress_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        progress_frame.grid(row=2, column=0, padx=10, pady=(1, 20), sticky="ew")
        
        self.cpu_progress = ctk.CTkProgressBar(
            progress_frame, 
            orientation="horizontal",
            height=5,
            corner_radius=10
        )
        self.cpu_progress.pack(fill="x", padx=10, pady=10)
        self.cpu_progress.set(0)
        
        # 控制面板
        control_frame = ctk.CTkFrame(self.dashboard_frame, corner_radius=15)
        control_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        ctk.CTkLabel(
            control_frame, 
            text="压力测试控制",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10))
        
        # 测试持续时间
        duration_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        duration_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(
            duration_frame, 
            text="测试持续时间 (秒):",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=(0, 10))
        
        self.duration_entry = ctk.CTkEntry(
            duration_frame, 
            width=80,
            placeholder_text="30",
            font=ctk.CTkFont(size=14)
        )
        self.duration_entry.pack(side="left")
        self.duration_entry.insert(0, "30")
        
        # 按钮区域
        btn_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)
        
        self.start_btn = ctk.CTkButton(
            btn_frame, 
            text="开始压力测试",
            command=self.confirm_start_test,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            corner_radius=10,
            fg_color="#2e8b57",
            hover_color="#3cb371"
        )
        self.start_btn.pack(side="left", padx=10, fill="x", expand=True)
        
        self.stop_btn = ctk.CTkButton(
            btn_frame, 
            text="停止测试",
            command=self.stop_stress_test,
            font=ctk.CTkFont(size=14),
            height=40,
            corner_radius=10,
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=10, fill="x", expand=True)
        
        self.emergency_btn = ctk.CTkButton(
            btn_frame, 
            text="紧急停止",
            command=self.emergency_stop_test,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            corner_radius=10,
            fg_color="#b22222",
            hover_color="#dc143c",
            state="disabled"
        )
        self.emergency_btn.pack(side="left", padx=10, fill="x", expand=True)
        
        # 状态信息
        status_frame = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        status_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        self.status_var = ctk.StringVar(value="就绪")
        status_label = ctk.CTkLabel(
            status_frame, 
            textvariable=self.status_var,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#3498db"
        )
        status_label.pack(side="left", padx=10)
    
    def create_logs_page(self):
        """创建日志页面"""
        self.logs_frame = ctk.CTkFrame(self.main_frame, corner_radius=10, fg_color="transparent")
        
        # 日志标题
        title_frame = ctk.CTkFrame(self.logs_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            title_frame, 
            text="测试日志记录",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")
        
        # 日志区域
        log_frame = ctk.CTkFrame(self.logs_frame, corner_radius=15)
        log_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(0, weight=1)
        
        self.log_text = ctk.CTkTextbox(
            log_frame,
            font=ctk.CTkFont(size=12, family="Consolas"),
            wrap="word",
            activate_scrollbars=True
        )
        self.log_text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.log_text.insert("0.0", "系统就绪，等待压力测试...\n")
        
        # 清除日志按钮
        btn_frame = ctk.CTkFrame(self.logs_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        clear_btn = ctk.CTkButton(
            btn_frame, 
            text="清除日志",
            command=self.clear_logs,
            font=ctk.CTkFont(size=14),
            height=40,
            corner_radius=10,
            fg_color="#2c3e50",
            hover_color="#34495e"
        )
        clear_btn.pack(side="right", padx=10)
    
    def create_settings_page(self):
        """创建设置页面"""
        self.settings_frame = ctk.CTkFrame(self.main_frame, corner_radius=10, fg_color="transparent")
        
        # 设置标题
        title_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            title_frame, 
            text="系统设置",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")
        
        # 设置卡片
        settings_card = ctk.CTkFrame(self.settings_frame, corner_radius=15)
        settings_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # 设置项
        setting_items = [
            {"label": "测试线程数", "value": str(multiprocessing.cpu_count()), "description": "设置用于压力测试的CPU线程数"},
            {"label": "最大CPU占用", "value": "100%", "description": "设置压力测试期间的最大CPU占用率"},
            {"label": "测试速度", "value": "100%", "description": "设置压力测试的计算速度"},
            {"label": "日志级别", "value": "标准", "description": "设置日志记录的详细程度"},
        ]
        
        for i, item in enumerate(setting_items):
            frame = ctk.CTkFrame(settings_card, fg_color="transparent")
            frame.pack(fill="x", padx=20, pady=15)
            
            label_frame = ctk.CTkFrame(frame, fg_color="transparent")
            label_frame.pack(fill="x", pady=(0, 5))
            
            ctk.CTkLabel(
                label_frame, 
                text=item["label"],
                font=ctk.CTkFont(size=16, weight="bold")
            ).pack(side="left")
            
            ctk.CTkLabel(
                label_frame, 
                text=item["value"],
                font=ctk.CTkFont(size=16)
            ).pack(side="right")
            
            ctk.CTkLabel(
                frame, 
                text=item["description"],
                font=ctk.CTkFont(size=14),
                text_color="#7f8c8d"
            ).pack(anchor="w")
        
        # 保存按钮
        btn_frame = ctk.CTkFrame(settings_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)
        
        save_btn = ctk.CTkButton(
            btn_frame, 
            text="代码小梓-bilibili",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            corner_radius=10,
            fg_color="#2980b9",
            hover_color="#3498db"
        )
        save_btn.pack(side="right", padx=10)
    
    def show_page(self, page):
        """显示指定页面"""
        self.dashboard_frame.grid_forget()
        self.logs_frame.grid_forget()
        self.settings_frame.grid_forget()
        
        if page == "dashboard":
            self.dashboard_frame.grid(row=0, column=0, sticky="nsew")
            self.home_button.configure(fg_color=("gray75", "gray25"))
        elif page == "logs":
            self.logs_frame.grid(row=0, column=0, sticky="nsew")
            self.logs_button.configure(fg_color=("gray75", "gray25"))
        elif page == "settings":
            self.settings_frame.grid(row=0, column=0, sticky="nsew")
            self.settings_button.configure(fg_color=("gray75", "gray25"))
    
    def show_dashboard(self):
        """显示仪表盘页面"""
        self.show_page("dashboard")
        self.home_button.configure(fg_color=("gray75", "gray25"))
        self.logs_button.configure(fg_color="transparent")
        self.settings_button.configure(fg_color="transparent")
    
    def show_logs(self):
        """显示日志页面"""
        self.show_page("logs")
        self.home_button.configure(fg_color="transparent")
        self.logs_button.configure(fg_color=("gray75", "gray25"))
        self.settings_button.configure(fg_color="transparent")
    
    def show_settings(self):
        """显示设置页面"""
        self.show_page("settings")
        self.home_button.configure(fg_color="transparent")
        self.logs_button.configure(fg_color="transparent")
        self.settings_button.configure(fg_color=("gray75", "gray25"))
    
    def change_theme(self, choice):
        """切换主题"""
        ctk.set_appearance_mode(choice)
        self.current_theme = choice
    
    def show_about(self):
        """显示关于窗口"""
        about_win = ctk.CTkToplevel(self)
        about_win.title("关于 cpu压榨器 作者")
        about_win.geometry("500x400")
        about_win.transient(self)
        about_win.grab_set()
        
        # 内容框架
        content_frame = ctk.CTkFrame(about_win, corner_radius=15)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 标题
        ctk.CTkLabel(
            content_frame, 
            text="CPU 压榨器-代码小梓",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(20, 10))
        
        # 版本信息
        ctk.CTkLabel(
            content_frame, 
            text="版本: v2.13.4",
            font=ctk.CTkFont(size=16)
        ).pack(pady=5)
        
        # 作者信息
        ctk.CTkLabel(
            content_frame, 
            text="作者: 代码小梓",
            font=ctk.CTkFont(size=16)
        ).pack(pady=10)
        
        # 链接按钮
        links_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        links_frame.pack(pady=20)
        
        blog_btn = ctk.CTkButton(
            links_frame, 
            text="访问我的博客",
            command=lambda: webbrowser.open("https://li958633.github.io/dmxzweb/"),
            font=ctk.CTkFont(size=14),
            width=120,
            height=35,
            corner_radius=8,
            fg_color="#2c3e50",
            hover_color="#34495e"
         )
        blog_btn.pack(side="left", padx=10)
        
        bili_btn = ctk.CTkButton(
            links_frame, 
            text="B站主页",
            command=lambda: webbrowser.open("https://space.bilibili.com/1114574804"),
            font=ctk.CTkFont(size=14),
            width=120,
            height=35,
            corner_radius=8,
            fg_color="#8e44ad",
            hover_color="#9b59b6"
        )
        bili_btn.pack(side="left", padx=10)
        
        # 关闭按钮
        ctk.CTkButton(
            content_frame, 
            text="关闭",
            command=about_win.destroy,
            font=ctk.CTkFont(size=14),
            width=100,
            height=35,
            corner_radius=8
        ).pack(pady=20)
    
    def log_message(self, message):
        """在日志区域添加消息"""
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
    
    def clear_logs(self):
        """清除日志"""
        self.log_text.delete("1.0", "end")
        self.log_message("日志已清除")
    
    def validate_int_entry(self, value):
        """验证整数输入"""
        if value == "":
            return True
        try:
            int(value)
            return True
        except ValueError:
            return False
    
    def confirm_start_test(self):
        """显示安全确认弹窗"""
        # 验证持续时间输入
        try:
            duration = int(self.duration_entry.get())
            if duration <= 0:
                self.show_error("错误", "持续时间必须大于0")
                return
        except ValueError:
            self.show_error("错误", "请输入有效的数字")
            return
            
        # 创建确认对话框
        dialog = ctk.CTkToplevel(self)
        dialog.title("确认压力测试")
        dialog.geometry("600x450")
        dialog.transient(self)
        dialog.grab_set()
        
        # 内容框架
        content_frame = ctk.CTkFrame(dialog, corner_radius=15)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 警告图标
        warning_icon = ctk.CTkLabel(
            content_frame, 
            text="⚠️",
            font=ctk.CTkFont(size=48)
        )
        warning_icon.pack(pady=(20, 10))
        
        # 警告标题
        ctk.CTkLabel(
            content_frame, 
            text="CPU 压榨测试警告",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=5)
        
        # 警告内容
        warning_text = ctk.CTkTextbox(
            content_frame,
            width=400,
            height=120,
            font=ctk.CTkFont(size=14),
            wrap="word",
            activate_scrollbars=False,
            fg_color="transparent"
        )
        warning_text.pack(pady=10)
        warning_text.insert("0.0", "CPU压力测试将占用系统资源，可能导致:\n\n• 系统响应变慢\n• 风扇噪音增大\n• CPU温度升高\n\n高负载运行可能导致硬件温度升高，请确保散热系统正常工作且不要长时间运行。")
        warning_text.configure(state="disabled")
        
        # 按钮区域
        btn_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        btn_frame.pack(pady=(10, 20))
        
        ctk.CTkButton(
            btn_frame, 
            text="开始测试",
            command=lambda: [self.start_stress_test(duration), dialog.destroy()],
            font=ctk.CTkFont(size=14, weight="bold"),
            width=120,
            height=40,
            corner_radius=10,
            fg_color="#27ae60",
            hover_color="#2ecc71"
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame, 
            text="取消",
            command=dialog.destroy,
            font=ctk.CTkFont(size=14),
            width=120,
            height=40,
            corner_radius=10
        ).pack(side="left", padx=10)
    
    def show_error(self, title, message):
        """显示错误对话框"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()
        
        # 内容框架
        content_frame = ctk.CTkFrame(dialog, corner_radius=15)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 错误图标
        error_icon = ctk.CTkLabel(
            content_frame, 
            text="❌",
            font=ctk.CTkFont(size=48)
        )
        error_icon.pack(pady=(10, 5))
        
        # 错误消息
        ctk.CTkLabel(
            content_frame, 
            text=message,
            font=ctk.CTkFont(size=16)
        ).pack(pady=5)
        
        # 关闭按钮
        ctk.CTkButton(
            content_frame, 
            text="确定",
            command=dialog.destroy,
            font=ctk.CTkFont(size=14),
            width=100,
            height=35,
            corner_radius=8
        ).pack(pady=15)
    
    def start_stress_test(self, duration):
        """开始压力测试"""
        try:
            self.emergency_stop = False
            self.stop_event.clear()
            
            self.log_message(f"🚀 开始压力测试，配置:")
            self.log_message(f"• 线程数: {self.config['cpu_threads']}")
            self.log_message(f"• 最大占用: {self.config['max_cpu_usage']}%")
            self.log_message(f"• 速度: {self.config['stress_speed']}%")
            self.log_message(f"• 持续时间: {duration}秒")
            self.status_var.set("压力测试运行中...")
            
            # 禁用开始按钮，启用停止按钮
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.emergency_btn.configure(state="normal")
            self.duration_entry.configure(state="disabled")
            
            # 创建并启动进程
            self.test_processes = []
            for _ in range(self.config["cpu_threads"]):
                p = multiprocessing.Process(
                    target=cpu_stress_worker,
                    args=(
                        duration,
                        self.config["stress_speed"],
                        self.config["max_cpu_usage"],
                        self.stop_event
                    )
                )
                p.start()
                self.test_processes.append(p)
                
            # 设置定时器检查进程是否完成
            self.after(1000, self.check_stress_test_completion)
            
        except Exception as e:
            self.show_error("错误", f"启动压力测试失败: {str(e)}")
            self.reset_ui_state()
    
    def emergency_stop_test(self):
        """紧急停止测试"""
        self.emergency_stop = True
        self.stop_stress_test()
        self.log_message("🛑 !!! 紧急停止已触发 !!!")
        self.status_var.set("已紧急停止")
    
    def check_stress_test_completion(self):
        """检查压力测试是否完成"""
        if self.emergency_stop:
            return
            
        for p in self.test_processes:
            if p.is_alive():
                # 如果还有进程在运行，1秒后再次检查
                self.after(1000, self.check_stress_test_completion)
                return
                
        # 所有进程都已完成
        self.test_processes = []
        self.log_message("✅ 压力测试完成")
        self.status_var.set("压力测试完成")
        self.reset_ui_state()
    
    def stop_stress_test(self):
        """停止压力测试"""
        self.stop_event.set()
            
        if not self.test_processes:
            self.show_info("信息", "没有正在运行的压力测试")
            return
            
        for p in self.test_processes:
            if p.is_alive():
                p.terminate()
                
        self.test_processes = []
        self.log_message("⏹ 压力测试已停止")
        self.status_var.set("压力测试已停止")
        self.reset_ui_state()
    
    def show_info(self, title, message):
        """显示信息对话框"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()
        
        # 内容框架
        content_frame = ctk.CTkFrame(dialog, corner_radius=15)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 信息图标
        info_icon = ctk.CTkLabel(
            content_frame, 
            text="ℹ️",
            font=ctk.CTkFont(size=48)
        )
        info_icon.pack(pady=(10, 5))
        
        # 信息消息
        ctk.CTkLabel(
            content_frame, 
            text=message,
            font=ctk.CTkFont(size=16)
        ).pack(pady=5)
        
        # 关闭按钮
        ctk.CTkButton(
            content_frame, 
            text="确定",
            command=dialog.destroy,
            font=ctk.CTkFont(size=14),
            width=100,
            height=35,
            corner_radius=8
        ).pack(pady=15)
    
    def reset_ui_state(self):
        """重置UI状态"""
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.emergency_btn.configure(state="disabled")
        self.duration_entry.configure(state="normal")
    
    def start_monitoring(self):
        """开始监控CPU使用率"""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.update_monitoring()
    
    def update_monitoring(self):
        """更新监控数据"""
        if not self.monitoring:
            return
            
        # 获取CPU使用率
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # 更新UI
        self.cpu_usage_var.set(f"{cpu_usage:.1f}%")
        self.cpu_progress.set(cpu_usage / 100)
        
        # 根据使用率改变进度条颜色
        if cpu_usage > 80:
            self.cpu_progress.configure(progress_color="#e74c3c")
        elif cpu_usage > 50:
            self.cpu_progress.configure(progress_color="#f39c12")
        else:
            self.cpu_progress.configure(progress_color="#2ecc71")
        
        # 继续监控
        self.after(1000, self.update_monitoring)
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
    
    def on_closing(self):
        """窗口关闭时清理资源"""
        self.stop_monitoring()
        self.stop_stress_test()
        self.destroy()

if __name__ == "__main__":
    # 修复Windows下的multiprocessing问题
    multiprocessing.freeze_support()
    
    # 创建应用实例
    app = CPUTesterApp()
    
    # 设置应用图标
    try:
        app.iconbitmap(resource_path("icon.ico"))
    except:
        pass
    
    # 运行应用
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()