import tkinter as tk
from tkinter import ttk
import math
import numpy as np
import time

class KeplerSimulation:
    def __init__(self, root):
        self.root = root
        self.root.title("开普勒第二定律模拟")
        
        # 设置窗口大小
        self.root.geometry("1200x800")
        
        # 设置默认离心率
        self.default_eccentricity = 0.7
        
        # 创建主框架
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建画布和控制面板
        self.setup_canvas()
        self.setup_control_panel()
        
        # 初始化模拟参数
        self.planets = []
        self.speed_multiplier = 1.0
        self.area_time_interval = 2.0  # 扫过面积的时间间隔(秒)
        self.last_update = time.perf_counter()
        self.running = True
        
        # 设置物理常数
        self.GM = 2000  # 引力常数与中心天体质量的乘积
        
        # 添加一个初始行星
        self.add_planet()
        
        # 开始动画
        self.update()
        
    def setup_canvas(self):
        # 创建画布
        self.canvas = tk.Canvas(
            self.main_frame, 
            width=900, 
            height=800, 
            bg='black'
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 计算中心点
        self.center_x = 450
        self.center_y = 400
        
    def setup_control_panel(self):
        # 创建带滚动条的控制面板框架
        control_outer_frame = ttk.Frame(self.main_frame)
        control_outer_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建Canvas和Scrollbar，设置固定宽度和高度
        canvas = tk.Canvas(control_outer_frame, width=300, height=800)  # 设置固定高度
        scrollbar = ttk.Scrollbar(control_outer_frame, orient="vertical", command=canvas.yview)
        
        # 创建内部框架
        control_frame = ttk.Frame(canvas)
        
        # 配置Canvas滚动区域
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        control_frame.bind("<Configure>", configure_scroll_region)
        
        # 在Canvas中创建窗口，使用full height
        canvas.create_window((0, 0), window=control_frame, anchor="nw", width=280)  # 设置固定宽度
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 布局滚动组件
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 绑定进入离开事件，只在鼠标在控制面板上时响应滚轮
        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind("<Enter>", _bind_mousewheel)
        canvas.bind("<Leave>", _unbind_mousewheel)
        
        # 设置控制面板的样式
        style = ttk.Style()
        style.configure('TLabelframe', background='#f0f0f0')
        style.configure('TLabelframe.Label', font=('Arial', 10, 'bold'))
        
        # 标题
        ttk.Label(
            control_frame, 
            text="开普勒第二定律模拟",
            font=('Arial', 16, 'bold')
        ).pack(pady=10)
        
        # 添加/删除行星按钮
        ttk.Button(
            control_frame, 
            text="添加行星", 
            command=self.add_planet
        ).pack(fill=tk.X, pady=5)
        
        ttk.Button(
            control_frame, 
            text="删除行星", 
            command=self.remove_planet
        ).pack(fill=tk.X, pady=5)
        
        # 速度控制
        ttk.Label(control_frame, text="模拟速度").pack(pady=5)
        self.speed_scale = ttk.Scale(
            control_frame,
            from_=0.1,
            to=5.0,
            orient=tk.HORIZONTAL,
            value=1.0,
            command=self.update_speed
        )
        self.speed_scale.pack(fill=tk.X, pady=5)
        
        # 修改面积时间间隔控制
        ttk.Label(control_frame, text="扫过面积的时间间隔(秒)").pack(pady=5)
        self.area_time_scale = ttk.Scale(
            control_frame,
            from_=0.1,
            to=100.0,  # 增加最大值
            orient=tk.HORIZONTAL,
            value=2.0,
            command=self.update_area_time
        )
        self.area_time_scale.pack(fill=tk.X, pady=5)
        
        # 添加面积比较显示
        self.area_compare_label = ttk.Label(
            control_frame,
            text="",
            font=('Arial', 10),
            justify=tk.LEFT
        )
        self.area_compare_label.pack(pady=10)
        
        # 显示信息
        self.info_label = ttk.Label(
            control_frame, 
            text="",
            font=('Arial', 10),
            justify=tk.LEFT
        )
        self.info_label.pack(pady=10)
        
        # 操作说明
        ttk.Label(
            control_frame,
            text="开普勒第二定律说明:\n\n" +
                 "在相同时间间隔内，行星与太阳的\n" +
                 "连线扫过的面积相等。\n\n" +
                 "观察说明:\n" +
                 "- 彩色区域表示扫过的面积\n" +
                 "- 可调整时间间隔观察面积\n" +
                 "- 近日点速度快，远日点速度慢\n" +
                 "- 扫过的面积始终相等",
            justify=tk.LEFT,
            font=('Arial', 10)
        ).pack(pady=20)
        
        # 开普勒第二定律详细说明
        law_frame = ttk.LabelFrame(control_frame, text="开普勒第二定律详细说明", padding="5")
        law_frame.pack(fill=tk.X, pady=10)
        
        law_text = """
开普勒第二定律（面积速率定律）：

行星绕太阳运动时，行星与太阳的连线在相等时间内扫过的面积相等。

数学表达：
dA/dt = L/(2m) = 常量

其中：
• A 是扫过的面积
• t 是时间
• L 是角动量
• m 是行星质量

物理含义：
1. 角动量守恒导致面积速率恒定
2. 近日点速度快，远日点速度慢
3. 轨道速度与半径的关系：
   v ∝ 1/r

观察要点：
1. 注意彩色区域（扫过的面积）
2. 比较近日点和远日点的速度
3. 观察相同时间间隔内的面积
4. 验证面积相等性

历史意义：
这一定律是开普勒在1609年发表的，
是开普勒三大定律中的第二定律，
为后来牛顿万有引力定律的发现
奠定了重要基础。
"""
        
        ttk.Label(
            law_frame,
            text=law_text,
            justify=tk.LEFT,
            font=('Arial', 10)
        ).pack(pady=5)
        
        # 修改轨道控制框架
        orbit_frame = ttk.LabelFrame(control_frame, text="轨道和行星管理", padding="5")
        orbit_frame.pack(fill=tk.X, pady=10)
        
        # 添加行星管理按钮组
        ttk.Button(
            orbit_frame,
            text="新轨道添加行星",
            command=self.add_planet_new_orbit
        ).pack(fill=tk.X, pady=2)
        
        ttk.Button(
            orbit_frame,
            text="同轨道添加行星",
            command=self.add_planet_same_orbit
        ).pack(fill=tk.X, pady=2)
        
        # 添加轨道列表框架
        orbits_list_frame = ttk.LabelFrame(control_frame, text="轨道列表", padding="5")
        orbits_list_frame.pack(fill=tk.X, pady=10)
        
        # 创建轨道列表
        self.orbits_listbox = tk.Listbox(
            orbits_list_frame,
            height=5,
            selectmode=tk.SINGLE
        )
        self.orbits_listbox.pack(fill=tk.X, pady=2)
        
        # 添加轨道管理按钮
        ttk.Button(
            orbits_list_frame,
            text="删除选中轨道",
            command=self.remove_selected_orbit
        ).pack(fill=tk.X, pady=2)
        
        ttk.Button(
            orbits_list_frame,
            text="删除选中轨道上的行星",
            command=self.remove_planet_from_orbit
        ).pack(fill=tk.X, pady=2)
        
    def update_area_time(self, value):
        self.area_time_interval = float(value)
        # 重置所有行星的位置历史
        for planet in self.planets:
            planet['positions'] = []
            planet['areas'] = []
            planet['last_area_time'] = time.perf_counter()
    
    def calculate_area(self, points):
        """计算多边形面积"""
        if len(points) < 3:
            return 0
        area = 0
        for i in range(len(points)):
            j = (i + 1) % len(points)
            area += points[i][0] * points[j][1]
            area -= points[j][0] * points[i][1]
        return abs(area) / 2
        
    def add_planet(self):
        """默认添加新轨道行星"""
        self.add_planet_new_orbit()
        
    def remove_planet(self):
        """删除最后添加的行星"""
        if self.planets:
            self.planets.pop()
            self.update_orbits_list()  # 更新轨道列表
            
    def update_speed(self, value):
        self.speed_multiplier = float(value)
        
    def get_planet_position(self, planet):
        # 计算行星在椭圆轨道上的位置
        r = (planet['a'] * (1 - planet['e']**2)) / (1 + planet['e'] * math.cos(planet['angle']))
        x = r * math.cos(planet['angle'])
        y = r * math.sin(planet['angle'])
        return x, y
        
    def calculate_velocity(self, planet):
        """根据开普勒第二定律计算速度"""
        # 计算轨道参数
        a = planet['a']
        e = planet['e']
        r = (a * (1 - e**2)) / (1 + e * math.cos(planet['angle']))
        
        # 计算速度（根据开普勒第二定律）
        # v = sqrt(GM * (2/r - 1/a))
        velocity = math.sqrt(self.GM * (2/r - 1/a))
        return velocity
        
    def update(self):
        if self.running:
            current_time = time.perf_counter()
            
            # 清空画布
            self.canvas.delete('all')
            
            # 绘制太阳
            self.canvas.create_oval(
                self.center_x-10, self.center_y-10,
                self.center_x+10, self.center_y+10,
                fill='yellow'
            )
            
            for planet in self.planets:
                # 更新行星位置
                dt = (current_time - planet['last_update']) * self.speed_multiplier
                r = math.sqrt(sum(p**2 for p in self.get_planet_position(planet)))
                angular_velocity = 50 / (r**2)
                planet['angle'] += angular_velocity * dt
                planet['last_update'] = current_time
                
                # 获取当前位置
                x, y = self.get_planet_position(planet)
                screen_x = x + self.center_x
                screen_y = y + self.center_y
                
                # 更新位置历史和面积计算
                if current_time - planet['last_area_time'] >= self.area_time_interval:
                    # 保存上一次的面积用于比较
                    if len(planet['positions']) > 2:
                        area_points = [(self.center_x, self.center_y)]
                        area_points.extend(planet['positions'])
                        area = self.calculate_area(area_points)
                        planet['areas'].append(area)
                        if len(planet['areas']) > 5:  # 保留最近5个面积记录
                            planet['areas'].pop(0)
                    
                    planet['positions'] = []
                    planet['last_area_time'] = current_time
                
                planet['positions'].append((screen_x, screen_y))
                
                # 绘制轨道
                points = []
                for angle in np.linspace(0, 2*math.pi, 100):
                    r = (planet['a'] * (1 - planet['e']**2)) / (1 + planet['e'] * math.cos(angle))
                    x = r * math.cos(angle) + self.center_x
                    y = r * math.sin(angle) + self.center_y
                    points.append(x)
                    points.append(y)
                self.canvas.create_line(points, fill='white', dash=(2, 2))
                
                # 绘制扫过的面积
                if len(planet['positions']) > 2:
                    area_points = [(self.center_x, self.center_y)]
                    area_points.extend(planet['positions'])
                    current_area = self.calculate_area(area_points)
                    
                    # 绘制面积
                    self.canvas.create_polygon(
                        *[coord for point in area_points for coord in point],
                        fill=planet['color'],
                        stipple='gray50'
                    )
                    
                    # 显示当前面积和历史比较
                    avg_area = np.mean(planet['areas']) if planet['areas'] else 0
                    diff_percent = ((current_area - avg_area) / avg_area * 100) if avg_area else 0
                    
                    area_text = f"面积: {current_area/1000:.1f}"
                    if len(planet['areas']) > 1:
                        area_text += f"\n差异: {diff_percent:+.1f}%"
                    
                    self.canvas.create_text(
                        screen_x + 15, screen_y + 15,
                        text=area_text,
                        fill=planet['color'],
                        anchor='w'
                    )
                
                # 绘制行星
                self.canvas.create_oval(
                    screen_x-5, screen_y-5,
                    screen_x+5, screen_y+5,
                    fill=planet['color']
                )
                
                # 更新速度显示
                velocity = self.calculate_velocity(planet)
                # 显示速度，添加单位和相对速度
                min_velocity = math.sqrt(self.GM * (2/(planet['a']*(1+planet['e'])) - 1/planet['a']))
                max_velocity = math.sqrt(self.GM * (2/(planet['a']*(1-planet['e'])) - 1/planet['a']))
                relative_speed = (velocity - min_velocity) / (max_velocity - min_velocity)
                
                velocity_text = (
                    f"速度: {velocity:.1f}\n"
                    f"相对速度: {relative_speed:.2%}"
                )
                
                self.canvas.create_text(
                    screen_x + 15, screen_y - 15,
                    text=velocity_text,
                    fill=planet['color'],
                    anchor='w'
                )
                
                # 在近日点和远日点标注最大最小速度
                if abs(planet['angle'] % (2*math.pi)) < 0.1:  # 近日点
                    self.canvas.create_text(
                        screen_x, screen_y - 30,
                        text=f"近日点\n最大速度: {max_velocity:.1f}",
                        fill=planet['color']
                    )
                elif abs(planet['angle'] % (2*math.pi) - math.pi) < 0.1:  # 远日点
                    self.canvas.create_text(
                        screen_x, screen_y - 30,
                        text=f"远日点\n最小速度: {min_velocity:.1f}",
                        fill=planet['color']
                    )
            
            # 更新面积比较信息
            if self.planets:
                areas_info = "面积比较:\n"
                for i, planet in enumerate(self.planets):
                    if planet['areas']:
                        areas_info += f"行星{i+1}: {np.mean(planet['areas'])/1000:.1f}\n"
                self.area_compare_label.config(text=areas_info)
            
            # 更新信息标签
            self.info_label.config(
                text=f"行星数量: {len(self.planets)}\n" +
                     f"模拟速度: {self.speed_multiplier:.1f}x\n" +
                     f"面积计算间隔: {self.area_time_interval:.1f}秒"
            )
            
            # 在轨道上显示轨道参数
            for i, planet in enumerate(self.planets):
                self.canvas.create_text(
                    self.center_x - planet['a'], self.center_y - 10,
                    text=f"轨道 {i+1}\ne={planet['e']:.2f}",
                    fill=planet['color'],
                    anchor='e'
                )
            
            # 继续更新
            self.root.after(16, self.update)  # 约60 FPS

    def add_planet_new_orbit(self):
        """在新轨道上添加行星"""
        a = np.random.randint(100, 200)  # 轨道半长轴
        e = self.default_eccentricity  # 使用默认离心率
        self.add_planet_with_params(a, e)

    def add_planet_same_orbit(self):
        """在最后一个行星的轨道上添加新行星"""
        if not self.planets:
            self.add_planet_new_orbit()
            return
        
        last_planet = self.planets[-1]
        # 在相同轨道上，但位置随机
        angle = np.random.uniform(0, 2*math.pi)
        self.add_planet_with_params(
            last_planet['a'],
            last_planet['e'],
            angle
        )

    def add_planet_with_params(self, a, e, angle=0):
        """使用指定参数添加行星"""
        color = '#{:02x}{:02x}{:02x}'.format(
            np.random.randint(100, 255),
            np.random.randint(100, 255),
            np.random.randint(100, 255)
        )
        
        planet = {
            'a': a,                  # 半长轴
            'e': e,                  # 离心率
            'angle': angle,          # 初始角度
            'color': color,          # 颜色
            'positions': [],         # 位置历史
            'areas': [],            # 面积历史
            'last_area_time': time.perf_counter(),
            'last_update': time.perf_counter()
        }
        
        self.planets.append(planet)
        self.update_orbits_list()  # 更新轨道列表

    def update_eccentricity(self, value=None):
        """更新离心率设置"""
        pass  # 这个方法用于实时显示当前离心率，可以根据需要实现

    def update_orbits_list(self):
        """更新轨道列表显示"""
        self.orbits_listbox.delete(0, tk.END)
        orbits = {}
        for i, planet in enumerate(self.planets):
            orbit_key = f"{planet['a']:.1f}_{planet['e']:.3f}"
            if orbit_key not in orbits:
                orbits[orbit_key] = []
            orbits[orbit_key].append(i)
        
        for orbit_key, planet_indices in orbits.items():
            a, e = map(float, orbit_key.split('_'))
            self.orbits_listbox.insert(tk.END, 
                f"轨道 {len(orbits)}: {len(planet_indices)}颗行星 "
                f"(a={a:.1f}, e={e:.3f})")

    def remove_selected_orbit(self):
        """删除选中的轨道及其上的所有行星"""
        selection = self.orbits_listbox.curselection()
        if not selection:
            return
        
        # 获取选中轨道的参数
        orbit_info = self.orbits_listbox.get(selection[0])
        orbit_num = int(orbit_info.split(':')[0].split()[-1]) - 1
        
        # 找到该轨道上的所有行星
        orbits = {}
        for i, planet in enumerate(self.planets):
            orbit_key = f"{planet['a']:.1f}_{planet['e']:.3f}"
            if orbit_key not in orbits:
                orbits[orbit_key] = []
            orbits[orbit_key].append(i)
        
        # 获取要删除的行星索引
        orbit_keys = list(orbits.keys())
        if orbit_num < len(orbit_keys):
            indices_to_remove = sorted(orbits[orbit_keys[orbit_num]], reverse=True)
            for idx in indices_to_remove:
                self.planets.pop(idx)
        
        self.update_orbits_list()

    def remove_planet_from_orbit(self):
        """从选中轨道上删除一颗行星"""
        selection = self.orbits_listbox.curselection()
        if not selection:
            return
        
        # 获取选中轨道的参数
        orbit_info = self.orbits_listbox.get(selection[0])
        orbit_num = int(orbit_info.split(':')[0].split()[-1]) - 1
        
        # 找到该轨道上的行星
        orbits = {}
        for i, planet in enumerate(self.planets):
            orbit_key = f"{planet['a']:.1f}_{planet['e']:.3f}"
            if orbit_key not in orbits:
                orbits[orbit_key] = []
            orbits[orbit_key].append(i)
        
        # 删除该轨道上的最后一颗行星
        orbit_keys = list(orbits.keys())
        if orbit_num < len(orbit_keys) and orbits[orbit_keys[orbit_num]]:
            idx = orbits[orbit_keys[orbit_num]][-1]
            self.planets.pop(idx)
        
        self.update_orbits_list()

def main():
    root = tk.Tk()
    app = KeplerSimulation(root)
    root.mainloop()

if __name__ == "__main__":
    main() 