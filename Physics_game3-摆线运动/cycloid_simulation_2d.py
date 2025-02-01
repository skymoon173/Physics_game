import tkinter as tk
from tkinter import ttk
import math
import time

class CycloidSimulation:
    def __init__(self, root):
        self.root = root
        self.root.title("摆线等时性演示 - 时间竞赛")
        
        # 设置参数
        self.WIDTH = 1000
        self.HEIGHT = 800
        self.R = 150  # 减小摆线半径
        self.POINTS = 200
        self.g = 980  # 重力加速度
        
        # 定义显示区域的边距
        self.MARGIN = 100  # 边距，避免曲线贴近边缘
        
        # 定义共同的起点和终点
        self.start_y = self.HEIGHT * 0.3  # 调整起点高度
        self.end_y = self.HEIGHT * 0.7    # 调整终点高度
        self.height = self.end_y - self.start_y
        
        # 二次曲线系数
        self.quadratic_coef = 0.5
        
        # 创建主框架
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建控制面板
        self.create_control_panel()
        
        # 创建画布
        self.canvas = tk.Canvas(self.main_frame, width=self.WIDTH, height=self.HEIGHT, bg='white')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 初始化轨道和小球
        self.tracks = []
        self.balls = []
        self.time_texts = []
        self.create_tracks()
        
        # 动画状态
        self.is_running = False
        
    def create_control_panel(self):
        """创建控制面板"""
        panel = ttk.Frame(self.main_frame, padding="10")
        panel.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 起始位置选择
        ttk.Label(panel, text="起始位置 (0-100%):").pack(pady=5)
        self.start_pos = tk.StringVar(value="0")
        ttk.Entry(panel, textvariable=self.start_pos, width=10).pack()
        
        # 二次曲线系数调整
        ttk.Label(panel, text="二次曲线系数:").pack(pady=(15,5))
        self.coef_var = tk.StringVar(value="0.5")
        coef_entry = ttk.Entry(panel, textvariable=self.coef_var, width=10)
        coef_entry.pack()
        
        # 更新曲线按钮
        ttk.Button(panel, text="更新曲线", 
                  command=self.update_tracks).pack(pady=10)
        
        # 控制按钮
        ttk.Button(panel, text="开始", 
                  command=self.start_simulation).pack(pady=5)
        ttk.Button(panel, text="重置", 
                  command=self.reset_simulation).pack(pady=5)
        
        # 运行时间显示框
        ttk.Label(panel, text="\n运行时间", font=('Arial', 10, 'bold')).pack(pady=(20,5))
        self.time_labels = []
        colors = ["blue", "red", "green"]
        names = ["摆线", "直线", "二次曲线"]
        for color, name in zip(colors, names):
            frame = ttk.Frame(panel)
            frame.pack(fill=tk.X, pady=2)
            ttk.Label(frame, text=f"{name}:", 
                     foreground=color).pack(side=tk.LEFT)
            label = ttk.Label(frame, text="0.00s")
            label.pack(side=tk.RIGHT)
            self.time_labels.append(label)
        
        # 添加理论说明
        theory_frame = ttk.LabelFrame(panel, text="理论说明", padding="5")
        theory_frame.pack(fill=tk.X, pady=(20,5))
        
        explanation_text = """
摆线(Cycloid)是圆在直线上滚动时，圆周上一点的轨迹。

参数方程：
x = R(θ - sinθ)
y = R(1 - cosθ)
其中：
R: 滚动圆的半径
θ: 参数角度 [0, π]

特性：
1. 起点处切线垂直(90°)
2. 终点处切线水平(0°)
3. 等时性：从摆线上任意点
   滑到最低点所需时间相同

比较：
- 蓝色摆线：最快下降曲线
- 红色直线：最短距离
- 绿色二次曲线：y=ax²+bx+c
"""
        ttk.Label(theory_frame, text=explanation_text, 
                 justify=tk.LEFT, wraplength=200).pack(pady=5)

    def create_tracks(self):
        """创建三条轨道"""
        # 定义摆线的起点，考虑边距
        start_x = self.MARGIN
        start_y = self.start_y
        
        # 1. 生成摆线轨道
        cycloid_points = []
        theta_max = math.pi  # 使用半个圆的参数范围
        
        for i in range(self.POINTS):
            t = i / (self.POINTS - 1)
            theta = t * theta_max
            x = start_x + self.R * (theta - math.sin(theta))
            y = start_y + self.R * (1 - math.cos(theta))
            cycloid_points.append((x, y))
        
        # 获取摆线的终点
        end_x, end_y = cycloid_points[-1]
        
        # 确保终点不超出显示范围
        if end_x > self.WIDTH - self.MARGIN:
            scale = (self.WIDTH - 2 * self.MARGIN) / (end_x - start_x)
            # 重新计算摆线点
            cycloid_points = []
            for i in range(self.POINTS):
                t = i / (self.POINTS - 1)
                theta = t * theta_max
                x = start_x + self.R * scale * (theta - math.sin(theta))
                y = start_y + self.R * scale * (1 - math.cos(theta))
                cycloid_points.append((x, y))
            end_x, end_y = cycloid_points[-1]
        
        # 2. 直线轨道 - 直接连接摆线的起点和终点
        straight_points = []
        for i in range(self.POINTS):
            t = i / (self.POINTS - 1)
            x = start_x + t * (end_x - start_x)
            y = start_y + t * (end_y - start_y)
            straight_points.append((x, y))
        
        # 3. 二次曲线 - 通过起点和终点，并满足起点垂直条件
        quadratic_points = []
        total_width = end_x - start_x
        total_height = end_y - start_y
        
        # 二次曲线参数：y = ax² + bx + c
        # 条件：1) 过起点 (0,0)
        #      2) 过终点 (w,h)
        #      3) 起点斜率为无穷大
        for i in range(self.POINTS):
            t = i / (self.POINTS - 1)
            x = start_x + t * total_width
            # 相对坐标
            rel_x = t * total_width
            # 二次曲线方程
            a = (total_height - total_width * self.quadratic_coef) / (total_width * total_width)
            b = self.quadratic_coef
            rel_y = a * rel_x * rel_x + b * rel_x
            y = start_y + rel_y
            quadratic_points.append((x, y))
        
        # 清除旧的轨道和小球
        self.canvas.delete("all")
        self.tracks = [cycloid_points, straight_points, quadratic_points]
        self.balls = []
        self.time_texts = []
        
        # 绘制网格
        for x in range(0, self.WIDTH, 50):
            self.canvas.create_line(x, 0, x, self.HEIGHT, fill="gray90")
        for y in range(0, self.HEIGHT, 50):
            self.canvas.create_line(0, y, self.WIDTH, y, fill="gray90")
        
        # 修改时间文本的偏移位置，避免起点和终点的重叠
        text_offsets = [
            (0, -40),      # 摆线时间显示在最上方
            (-60, -20),    # 直线时间显示在左侧
            (60, 20)       # 二次曲线时间显示在右下方
        ]
        
        # 创建轨道、小球和时间显示
        colors = ["blue", "red", "green"]
        names = ["摆线", "直线", "二次曲线"]
        
        for points, color, name, offset in zip(self.tracks, colors, names, text_offsets):
            # 绘制轨道
            self.canvas.create_line(points, fill=color, width=3)
            
            # 创建小球
            ball = self.canvas.create_oval(-10, -10, 10, 10, fill=color)
            self.balls.append({
                "shape": ball,
                "points": points,
                "index": 0,
                "velocity": 0,
                "running": False,
                "start_time": 0,
                "name": name,
                "text_offset": offset
            })
            
            # 创建时间文本，使用不同的偏移位置
            time_text = self.canvas.create_text(
                points[0][0] + offset[0], points[0][1] + offset[1],
                text=f"{name}: 0.00s",
                fill=color,
                font=('Arial', 12, 'bold'),
                anchor="w"  # 文本左对齐
            )
            self.time_texts.append(time_text)

    def update_tracks(self):
        """更新轨道"""
        try:
            self.quadratic_coef = float(self.coef_var.get())
            self.create_tracks()
            self.reset_simulation()
        except ValueError:
            pass

    def start_simulation(self):
        """开始模拟"""
        if self.is_running:
            return
            
        try:
            start_percent = float(self.start_pos.get())
            if not 0 <= start_percent <= 100:
                return
                
            self.is_running = True
            start_time = time.time()
            
            # 根据百分比设置起始位置
            start_index = int((start_percent / 100) * (self.POINTS - 1))
            
            for ball in self.balls:
                ball["index"] = start_index
                ball["velocity"] = 0
                ball["running"] = True
                ball["start_time"] = start_time
                
                # 设置小球初始位置
                point = ball["points"][start_index]
                self.canvas.coords(ball["shape"], 
                                 point[0]-5, point[1]-5,
                                 point[0]+5, point[1]+5)
                
                # 设置时间文本位置
                self.canvas.coords(
                    self.time_texts[self.balls.index(ball)],
                    point[0], point[1]-20
                )
            
            self.update_simulation()
            
        except ValueError:
            pass

    def reset_simulation(self):
        """重置模拟"""
        self.is_running = False
        
        for i, ball in enumerate(self.balls):
            ball["index"] = 0
            ball["velocity"] = 0
            ball["running"] = False
            point = ball["points"][0]
            self.canvas.coords(ball["shape"], 
                             point[0]-5, point[1]-5,
                             point[0]+5, point[1]+5)
            self.canvas.itemconfig(self.time_texts[i], 
                                 text=f"{ball['name']}: 0.00s")
            self.canvas.coords(self.time_texts[i], 
                             point[0], point[1]-20)

    def update_simulation(self):
        """更新模拟"""
        if not self.is_running:
            return
            
        dt = 1/60
        all_stopped = True
        
        for i, ball in enumerate(self.balls):
            if not ball["running"]:
                continue
                
            all_stopped = False
            points = ball["points"]
            current_index = int(ball["index"])
            
            if current_index >= len(points) - 1:
                ball["running"] = False
                continue
            
            # 计算切线角度
            p1 = points[current_index]
            p2 = points[current_index + 1]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            theta = math.atan2(dy, dx)
            
            # 更新速度和位置
            ball["velocity"] += self.g * math.sin(theta) * dt
            step_length = math.hypot(dx, dy)
            ball["index"] += (ball["velocity"] * dt) / step_length
            
            # 限制索引范围
            ball["index"] = min(ball["index"], len(points) - 1)
            
            # 更新小球位置
            point = points[int(ball["index"])]
            self.canvas.coords(ball["shape"], 
                             point[0]-5, point[1]-5,
                             point[0]+5, point[1]+5)
            
            # 更新时间显示
            elapsed_time = time.time() - ball["start_time"]
            # 更新画布上的时间显示
            self.canvas.itemconfig(
                self.time_texts[i], 
                text=f"{ball['name']}: {elapsed_time:.2f}s"
            )
            offset = ball["text_offset"]
            self.canvas.coords(
                self.time_texts[i],
                point[0] + offset[0], point[1] + offset[1]
            )
            # 更新右侧面板的时间显示
            self.time_labels[i].config(text=f"{elapsed_time:.2f}s")
        
        if not all_stopped:
            self.root.after(16, self.update_simulation)
        else:
            self.is_running = False

def main():
    root = tk.Tk()
    app = CycloidSimulation(root)
    root.mainloop()

if __name__ == "__main__":
    main()