import tkinter as tk
from tkinter import ttk
import math

class MaterialTheme:
    """Material Design 3 主题配置"""
    
    def __init__(self):
        self.colors = {
            'primary': '#6750A4', 'on_primary': '#FFFFFF',
            'primary_container': '#EADDFF', 'on_primary_container': '#21005D',
            'secondary': '#625B71', 'on_secondary': '#FFFFFF',
            'secondary_container': '#E8DEF8', 'on_secondary_container': '#1D192B',
            'tertiary': '#7D5260', 'on_tertiary': '#FFFFFF',
            'tertiary_container': '#FFD8E4', 'on_tertiary_container': '#31111D',
            'error': '#B3261E', 'on_error': '#FFFFFF',
            'error_container': '#F9DEDC', 'on_error_container': '#410E0B',
            'background': '#FFFBFE', 'on_background': '#1C1B1F',
            'surface': '#FFFBFE', 'on_surface': '#1C1B1F',
            'surface_variant': '#E7E0EC', 'on_surface_variant': '#49454F',
            'outline': '#79747E', 'outline_variant': '#CAC4D0',
            'scrim': '#000000'
        }
        
        self.typography = {
            'display_large': ('Inter', 57, 'normal'),   # 字体名, 大小, 样式
            'display_medium': ('Inter', 45, 'normal'),
            'display_small': ('Inter', 36, 'normal'),
            'headline_large': ('Inter', 32, 'normal'),
            'headline_medium': ('Inter', 28, 'normal'),
            'headline_small': ('Inter', 24, 'normal'),
            'title_large': ('Inter', 22, 'bold'),       # 使用 'bold' 替代 'medium'
            'title_medium': ('Inter', 16, 'bold'),      # 使用 'bold' 替代 'medium'
            'title_small': ('Inter', 14, 'bold'),       # 使用 'bold' 替代 'medium'
            'label_large': ('Inter', 14, 'bold'),       # 使用 'bold' 替代 'medium'
            'label_medium': ('Inter', 12, 'bold'),      # 使用 'bold' 替代 'medium'
            'label_small': ('Inter', 11, 'bold'),       # 使用 'bold' 替代 'medium'
            'body_large': ('Inter', 16, 'normal'),
            'body_medium': ('Inter', 14, 'normal'),
            'body_small': ('Inter', 12, 'normal')
        }
        
        self.elevation = {
            'level0': {'shadow': ''},
            'level1': {'shadow': 'rgba(0,0,0,0.2)'},  # 1dp
            'level2': {'shadow': 'rgba(0,0,0,0.3)'},  # 3dp
            'level3': {'shadow': 'rgba(0,0,0,0.4)'},  # 6dp
            'level4': {'shadow': 'rgba(0,0,0,0.5)'},  # 8dp
            'level5': {'shadow': 'rgba(0,0,0,0.6)'},  # 12dp
        }

class MaterialWidgetMixin:
    """Material Widget 混合类，提供通用功能"""
    
    def __init__(self):
        self._hover_state = False
        self._pressed_state = False
    
    def _apply_ripple_effect(self, event, widget):
        """应用涟漪效果"""
        # 简化的涟漪效果实现
        original_bg = widget.cget('bg')
        widget.config(bg=self.colors.get('primary', '#6750A4'))
        self.after(100, lambda: widget.config(bg=original_bg))

class MaterialFrame(tk.Frame):
    """Material Design 风格的框架"""
    
    def __init__(self, parent, elevation=0, corner_radius=4, **kwargs):
        # 默认样式
        kwargs.setdefault('bg', MaterialTheme().colors['surface'])
        kwargs.setdefault('relief', 'flat')
        kwargs.setdefault('highlightthickness', 0)
        
        super().__init__(parent, **kwargs)
        self.elevation = elevation
        self.corner_radius = corner_radius
        self._setup_style()
    
    def _setup_style(self):
        """设置样式"""
        if self.elevation > 0:
            # 应用阴影效果
            shadow_color = self._get_elevation_color(self.elevation)
            self.config(highlightbackground=shadow_color, highlightthickness=1)
    
    def _get_elevation_color(self, level):
        """获取对应海拔的颜色"""
        colors = {
            1: '#00000020', 2: '#00000030', 3: '#00000040',
            4: '#00000050', 5: '#00000060'
        }
        return colors.get(level, '#00000020')

class MaterialButton(tk.Button, MaterialWidgetMixin):
    """Material Design 风格的按钮"""
    
    def __init__(self, parent, variant='filled', **kwargs):
        self.variant = variant
        self.theme = MaterialTheme()
        self._setup_button_style(kwargs)
        
        super().__init__(parent, **kwargs)
        MaterialWidgetMixin.__init__(self)
        
        # 绑定事件
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)
    
    def _setup_button_style(self, kwargs):
        """设置按钮样式"""
        #使用高对比度颜色方案，确保按钮在不同背景下都具有良好的可见性和可访问性
        if self.variant == 'filled':
            kwargs.setdefault('bg', self.theme.colors['primary'])
            kwargs.setdefault('fg', self.theme.colors['on_primary'])
            kwargs.setdefault('activebackground', self.theme.colors['primary_container'])
            kwargs.setdefault('activeforeground', self.theme.colors['on_primary_container'])
        elif self.variant == 'outlined':
            kwargs.setdefault('bg', self.theme.colors['surface'])
            kwargs.setdefault('fg', self.theme.colors['primary'])
            kwargs.setdefault('activebackground', self.theme.colors['primary_container'])
            kwargs.setdefault('activeforeground', self.theme.colors['on_primary_container'])
            kwargs.setdefault('highlightthickness', 2)
            kwargs.setdefault('highlightbackground', self.theme.colors['primary'])
        elif self.variant == 'text':
            kwargs.setdefault('bg', self.theme.colors['surface'])
            kwargs.setdefault('fg', self.theme.colors['primary'])
            kwargs.setdefault('activebackground', self.theme.colors['primary_container'])
            kwargs.setdefault('activeforeground', self.theme.colors['on_primary_container'])
            kwargs.setdefault('highlightthickness', 0)
        
    
    def _on_enter(self, event):
        """鼠标进入事件"""
        if self.variant == 'filled':
            self.config(bg=self.theme.colors['primary_container'])
        elif self.variant == 'outlined':
            self.config(bg=self.theme.colors['primary_container'])
        elif self.variant == 'text':
            self.config(bg=self.theme.colors['primary_container'])
    
    def _on_leave(self, event):
        """鼠标离开事件"""
        if self.variant == 'filled':
            self.config(bg=self.theme.colors['primary'])
        elif self.variant == 'outlined':
            self.config(bg=self.theme.colors['surface'])
        elif self.variant == 'text':
            self.config(bg=self.theme.colors['surface'])
    
    def _on_press(self, event):
        """按下事件"""
        self.config(relief='sunken')
    
    def _on_release(self, event):
        """释放事件"""
        self.config(relief='raised')

class MaterialEntry(tk.Entry):
    """Material Design 风格的输入框"""
    
    def __init__(self, parent, placeholder="", **kwargs):
        self.placeholder = placeholder
        self.placeholder_color = '#9E9E9E'
        self.focused_color = MaterialTheme().colors['primary']
        self.unfocused_color = MaterialTheme().colors['outline']
        
        kwargs.setdefault('font', MaterialTheme().typography['body_medium'])
        kwargs.setdefault('bg', MaterialTheme().colors['surface'])
        kwargs.setdefault('fg', MaterialTheme().colors['on_surface'])
        kwargs.setdefault('insertbackground', MaterialTheme().colors['on_surface'])
        kwargs.setdefault('relief', 'solid')
        kwargs.setdefault('bd', 2)
        kwargs.setdefault('highlightthickness', 0)
        
        super().__init__(parent, **kwargs)
        
        # 设置占位符
        self._show_placeholder()
        
        # 绑定事件
        self.bind('<FocusIn>', self._on_focus_in)
        self.bind('<FocusOut>', self._on_focus_out)
        self.bind('<Key>', self._on_key)
    
    def _show_placeholder(self):
        """显示占位符"""
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(fg=self.placeholder_color)
    
    def _hide_placeholder(self):
        """隐藏占位符"""
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(fg=MaterialTheme().colors['on_surface'])
    
    def _on_focus_in(self, event):
        """获得焦点"""
        self._hide_placeholder()
        self.config(highlightbackground=self.focused_color, highlightthickness=2)
    
    def _on_focus_out(self, event):
        """失去焦点"""
        if not self.get():
            self._show_placeholder()
        self.config(highlightbackground=self.unfocused_color, highlightthickness=2)
    
    def _on_key(self, event):
        """按键事件"""
        if self.get() != self.placeholder:
            self.config(fg=MaterialTheme().colors['on_surface'])

class MaterialLabel(tk.Label):
    """Material Design 风格的标签"""
    
    def __init__(self, parent, **kwargs):
        # 修复：移除 'transparent' 颜色，使用继承父组件的背景色
        # 不设置 bg 参数，让标签继承父组件的背景色
        kwargs.setdefault('fg', MaterialTheme().colors['on_surface'])
        kwargs.setdefault('font', MaterialTheme().typography['body_medium'])
        
        super().__init__(parent, **kwargs)

class MaterialCard(MaterialFrame):
    """Material Design 风格的卡片"""
    
    def __init__(self, parent, title="", **kwargs):
        kwargs.setdefault('elevation', 1)
        kwargs.setdefault('corner_radius', 12)
        
        super().__init__(parent, **kwargs)
        
        if title:
            self._create_title(title)
    
    def _create_title(self, title):
        """创建标题"""
        title_label = MaterialLabel(self, text=title, font=MaterialTheme().typography['title_large'])
        title_label.pack(anchor='w', padx=20, pady=(20, 10))

class MaterialTreeView(ttk.Treeview):
    """Material Design 风格的表格视图"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # 配置样式
        style = ttk.Style()
        theme = MaterialTheme()
        
        # 配置行样式
        style.configure(
            'Material.Treeview',
            background=theme.colors['surface'],
            foreground=theme.colors['on_surface'],
            fieldbackground=theme.colors['surface'],
            font=theme.typography['body_small'],
            rowheight=40,
            borderwidth=0,
            relief='flat'
        )
        
        # 配置表头样式
        style.configure(
            'Material.Treeview.Heading',
            background=theme.colors['surface_variant'],
            foreground=theme.colors['on_surface_variant'],
            font=theme.typography['label_medium'],
            relief='flat',
            borderwidth=0
        )
        
        # 配置选中样式
        style.map(
            'Material.Treeview',
            background=[('selected', theme.colors['primary'])],
            foreground=[('selected', theme.colors['on_primary'])]
        )
        
        self.configure(style='Material.Treeview')