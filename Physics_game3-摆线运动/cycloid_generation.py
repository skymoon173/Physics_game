import tkinter as tk
from tkinter import ttk
import math

class CycloidGeneration:
    def __init__(self, root):
        self.root = root
        self.root.title("摆线生成演示")
        
        # 设置参数
        self.WIDTH = 800
        self.HEIGHT = 400
        self.R = 50  # 圆的半径
        self.MARGIN = 50  # 边距
        
        # 动画参数
        self.angle = 0  # 圆的转角
        self.is_running = False
        self.trace_points = []  # 存储轨迹点
        
        # 添加滚动范围
        self.scroll_x = 0  # 添加滚动位置变量
        
        # 创建主框架
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建画布
        self.canvas = tk.Canvas(self.main_frame, width=self.WIDTH, height=self.HEIGHT, bg='white')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 绑定鼠标事件
        self.canvas.bind("<ButtonPress-1>", self.scroll_start)
        self.canvas.bind("<B1-Motion>", self.scroll_move)
        self.last_x = 0  # 记录上次鼠标位置
        
        # 创建控制面板
        self.create_control_panel()
        
        # 绘制基准线
        self.base_y = self.HEIGHT - self.MARGIN - self.R
        self.draw_baseline()
        
        # 创建圆和跟踪点
        self.circle = self.canvas.create_oval(0, 0, 0, 0, outline='blue', width=2)
        self.track_point = self.canvas.create_oval(0, 0, 0, 0, fill='red', width=0)
        self.trace_line = None
        
        # 创建连接线
        self.radius_line = self.canvas.create_line(0, 0, 0, 0, fill='gray', dash=(4, 4))
        
    def create_control_panel(self):
        """创建控制面板"""
        panel = ttk.Frame(self.main_frame, padding="10")
        panel.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 控制按钮
        ttk.Button(panel, text="开始/暂停", command=self.toggle_animation).pack(pady=5)
        ttk.Button(panel, text="重置", command=self.reset_animation).pack(pady=5)
        
        # 圆半径控制
        ttk.Label(panel, text="圆的半径:").pack(pady=(15,5))
        self.radius_var = tk.IntVar(value=self.R)
        radius_scale = ttk.Scale(panel, from_=20, to=100, 
                              variable=self.radius_var, 
                              orient=tk.HORIZONTAL,
                              command=self.update_radius)
        radius_scale.pack()
        
        # 速度控制
        ttk.Label(panel, text="速度:").pack(pady=(15,5))
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = ttk.Scale(panel, from_=0.1, to=3.0, 
                              variable=self.speed_var, 
                              orient=tk.HORIZONTAL)
        speed_scale.pack()
        
        # 更新说明文本
        explanation = """
说明：

红点轨迹形成摆线曲线

参数方程：
x = R(θ - sinθ)
y = R(1 - cosθ)

其中：
R: 圆的半径（可调节）
θ: 转动角度

特点：
1. 圆在直线上滚动
2. 圆周上的点形成摆线
3. 调整圆的半径可以改变
   摆线的大小
4. 拖动画布可以查看更多轨迹
"""
        ttk.Label(panel, text=explanation, justify=tk.LEFT).pack(pady=20)

    def scroll_start(self, event):
        """开始拖动"""
        self.last_x = event.x
        
    def scroll_move(self, event):
        """拖动画布"""
        dx = event.x - self.last_x
        self.scroll_x += dx
        self.last_x = event.x
        self.update_circle()
        
    def update_radius(self, *args):
        """更新圆的半径"""
        # 更新半径
        self.R = self.radius_var.get()
        
        # 更新基准线位置
        self.base_y = self.HEIGHT - self.MARGIN - self.R
        self.canvas.delete("baseline")
        self.canvas.delete("trace")  # 删除旧的轨迹
        self.trace_points = []  # 清空轨迹点
        
        # 重新绘制基准线
        self.draw_baseline()
        
        # 重置动画但保持当前滚动位置
        self.reset_animation(keep_scroll=True)
        
    def draw_baseline(self):
        """绘制基准线"""
        self.canvas.create_line(
            0, self.base_y,
            self.WIDTH, self.base_y,
            width=2, tags="baseline"
        )
        
    def toggle_animation(self):
        """开始/暂停动画"""
        self.is_running = not self.is_running
        if self.is_running:
            self.update_animation()
            
    def reset_animation(self, keep_scroll=False):
        """重置动画"""
        self.is_running = False
        self.angle = 0
        if not keep_scroll:
            self.scroll_x = 0
        self.trace_points = []
        self.canvas.delete("trace")
        self.canvas.delete("baseline")
        
        # 重新绘制基准线
        self.draw_baseline()
        self.update_circle()
        
    def update_circle(self):
        """更新圆和跟踪点的位置"""
        # 计算圆心位置，考虑滚动位置
        center_x = self.MARGIN + self.R * self.angle + self.scroll_x
        center_y = self.base_y - self.R
        
        # 更新圆的位置
        self.canvas.coords(self.circle,
                         center_x - self.R, center_y - self.R,
                         center_x + self.R, center_y + self.R)
        
        # 计算跟踪点位置
        point_x = center_x + self.R * math.sin(self.angle)
        point_y = center_y - self.R * math.cos(self.angle)
        
        # 更新跟踪点位置
        point_size = 4
        self.canvas.coords(self.track_point,
                         point_x - point_size, point_y - point_size,
                         point_x + point_size, point_y + point_size)
        
        # 更新连接线
        self.canvas.coords(self.radius_line,
                         center_x, center_y,
                         point_x, point_y)
        
        # 添加轨迹点
        self.trace_points.append((point_x, point_y))
        if len(self.trace_points) > 1:
            # 删除旧的轨迹线
            if self.trace_line:
                self.canvas.delete(self.trace_line)
            # 绘制新的轨迹线
            self.trace_line = self.canvas.create_line(
                self.trace_points, fill='red', width=2, tags="trace"
            )
        
    def update_animation(self):
        """更新动画"""
        if self.is_running:
            self.angle += 0.05 * self.speed_var.get()
            self.update_circle()
            self.root.after(20, self.update_animation)

def main():
    root = tk.Tk()
    app = CycloidGeneration(root)
    root.mainloop()

if __name__ == "__main__":
    main()