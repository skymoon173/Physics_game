# Copyright (c) [year] [your name]
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class ControlPanel:
    def __init__(self, simulation):
        self.simulation = simulation
        self.root = tk.Tk()
        self.root.title("参数控制面板")
        
        # 设置全局字体
        self.root.option_add('*Font', '微软雅黑 10')  # 设置默认字体
        
        # 防止窗口被关闭
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # 设置窗口大小和位置
        self.root.geometry("400x800+50+50")  # 宽x高+x位置+y位置
        
        # 创建参数控制
        self.create_widgets()
        
        # 创建能量显示标签
        self.create_energy_display()
        
        # 创建能量柱状图
        self.create_energy_plot()
        
        self.root.update()
    
    def create_widgets(self):
        # 设置网格布局权重
        for i in range(7):  # 为所有行设置权重
            self.root.grid_rowconfigure(i, weight=1)
        
        # 弹性系数控制
        tk.Label(self.root, text="弹性系数 (k):").grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        k_scale = ttk.Scale(self.root, from_=0.1, to=5.0, orient=tk.HORIZONTAL,
                           command=lambda x: self.update_param('k', float(x)))
        k_scale.set(self.simulation.k)
        k_scale.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # 阻尼系数控制
        tk.Label(self.root, text="阻尼系数:").grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        damp_scale = ttk.Scale(self.root, from_=0.0, to=1.0, orient=tk.HORIZONTAL,
                              command=lambda x: self.update_param('damping', float(x)))
        damp_scale.set(self.simulation.damping)
        damp_scale.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # 作用距离控制
        tk.Label(self.root, text="作用距离:").grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        dist_scale = ttk.Scale(self.root, from_=1.0, to=10.0, orient=tk.HORIZONTAL,
                              command=lambda x: self.update_param('interaction_distance', float(x)))
        dist_scale.set(self.simulation.interaction_distance)
        dist_scale.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        # 粒子数量控制
        tk.Label(self.root, text="粒子数量:").grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        num_scale = ttk.Scale(self.root, from_=10, to=100, orient=tk.HORIZONTAL,
                             command=self.update_num_particles)
        num_scale.set(self.simulation.num_particles)
        num_scale.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        
        # 重置按钮
        reset_btn = ttk.Button(self.root, text="重置模拟",
                              command=self.simulation.reset_simulation)
        reset_btn.grid(row=4, column=0, padx=5, pady=5, sticky="ew")
        
        # 重置相机按钮
        reset_camera_btn = ttk.Button(self.root, text="重置视角",
                                     command=self.simulation.reset_camera)
        reset_camera_btn.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
    
    def create_energy_display(self):
        # 创建能量显示框架
        energy_frame = ttk.LabelFrame(self.root, text="能量信息")
        energy_frame.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # 创建标签显示各种能量
        self.kinetic_label = tk.Label(energy_frame, text="动能: 0.000")
        self.kinetic_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        
        self.potential_label = tk.Label(energy_frame, text="势能: 0.000")
        self.potential_label.grid(row=1, column=0, padx=5, pady=2, sticky="w")
        
        self.lagrangian_label = tk.Label(energy_frame, text="拉格朗日量: 0.000")
        self.lagrangian_label.grid(row=2, column=0, padx=5, pady=2, sticky="w")
    
    def create_energy_plot(self):
        plot_frame = ttk.LabelFrame(self.root, text="能量分布")
        plot_frame.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        # 设置matplotlib中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', '微软雅黑', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        self.fig = Figure(figsize=(6, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # 初始化柱状图数据
        self.bars = self.ax.bar(['动能', '势能'], [0, 0], color=['skyblue', 'lightcoral'])
        self.ax.set_ylim(0, 10)
        
        # 配置字体
        font_props = {'family': 'SimHei'}
        self.ax.set_title('能量分布图', fontdict=font_props)
        self.ax.set_xlabel('能量类型', fontdict=font_props)
        self.ax.set_ylabel('能量值', fontdict=font_props)
        
        for label in self.ax.get_xticklabels() + self.ax.get_yticklabels():
            label.set_fontproperties('SimHei')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        # 设置网格布局权重
        self.root.grid_rowconfigure(6, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        self.fig.tight_layout()
    
    def update_num_particles(self, value):
        """专门处理粒子数量更新的函数"""
        new_num = int(float(value))
        if new_num != self.simulation.num_particles:
            self.simulation.num_particles = new_num
            self.simulation.reset_simulation()  # 重新初始化模拟
    
    def update_param(self, param_name, value):
        """更新其他参数"""
        if param_name != 'num_particles':  # 粒子数量由专门的函数处理
            setattr(self.simulation, param_name, value)
    
    def update_energy_plot(self, T, V):
        # 更新柱状图数据
        self.bars[0].set_height(T)
        self.bars[1].set_height(V)
        
        # 动态调整y轴范围
        max_energy = max(T, V)
        current_ymax = self.ax.get_ylim()[1]
        if max_energy > current_ymax:
            self.ax.set_ylim(0, max_energy * 1.2)
        elif max_energy < current_ymax * 0.5:
            self.ax.set_ylim(0, current_ymax * 0.8)
        
        # 重绘图表
        self.canvas.draw()
    
    def update(self):
        try:
            if not self.root.winfo_exists():
                return
                
            T, V = self.simulation.calculate_energies()
            L = T - V
            
            # 更新文本标签
            try:
                self.kinetic_label.config(text=f"动能: {T:.3f}")
                self.potential_label.config(text=f"势能: {V:.3f}")
                self.lagrangian_label.config(text=f"拉格朗日量: {L:.3f}")
                
                # 更新能量柱状图
                self.update_energy_plot(T, V)
            except tk.TclError:
                return
                
            self.root.update()
        except:
            pass  # 忽略所有其他错误

class ProteinSimulation:
    def __init__(self):
        # 初始化参数
        self.num_particles = 100
        self.interaction_distance = 5.0  # 新增参数：作用距离
        self.reset_simulation()
        self.reset_camera()
    
    def reset_simulation(self):
        # 重置粒子状态
        self.positions = np.random.rand(self.num_particles, 3) * 10
        self.velocities = np.zeros((self.num_particles, 3))
        self.masses = np.ones(self.num_particles)
        self.k = 1.0
        self.damping = 0.1
        self.colors = np.random.rand(self.num_particles, 3)
    
    def reset_camera(self):
        # 重置相机参数到初始状态
        self.rotate_x = 0
        self.rotate_y = 0
        self.translate_x = 0
        self.translate_y = 0
        self.zoom = -30.0
        
        # 重置鼠标参数
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_button = None

    def calculate_energies(self):
        """计算系统的动能和势能"""
        # 计算动能 T
        T = 0.5 * np.sum(self.masses[:, np.newaxis] * self.velocities**2)
        
        # 计算势能 V
        V = 0
        for i in range(self.num_particles):
            for j in range(i + 1, self.num_particles):
                r = self.positions[i] - self.positions[j]
                distance = np.linalg.norm(r)
                if distance < self.interaction_distance:
                    V += 0.5 * self.k * distance**2
        
        return T, V

    def calculate_lagrangian(self):
        T, V = self.calculate_energies()
        return T - V

    def calculate_forces(self):
        forces = np.zeros_like(self.positions)
        
        for i in range(self.num_particles):
            dV_dq = np.zeros(3)
            for j in range(self.num_particles):
                if i != j:
                    r = self.positions[i] - self.positions[j]
                    distance = np.linalg.norm(r)
                    if distance < self.interaction_distance:
                        dV_dq += self.k * r / distance
            
            forces[i] = -dV_dq
        
        # 添加阻尼力
        forces -= self.damping * self.velocities
        return forces

    def update(self, dt=0.01):
        # 更新位置和速度
        forces = self.calculate_forces()
        self.velocities += forces * dt / self.masses[:, np.newaxis]
        self.positions += self.velocities * dt

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # 设置相机位置
        glTranslatef(self.translate_x, self.translate_y, self.zoom)
        glRotatef(self.rotate_x, 1.0, 0.0, 0.0)
        glRotatef(self.rotate_y, 0.0, 1.0, 0.0)
        
        # 绘制粒子
        for i, (pos, color) in enumerate(zip(self.positions, self.colors)):
            glPushMatrix()
            glTranslatef(pos[0], pos[1], pos[2])
            glColor3f(color[0], color[1], color[2])
            glutSolidSphere(0.3, 10, 10)
            glPopMatrix()
            
            # 绘制粒子之间的连接线
            for j in range(i + 1, self.num_particles):
                if np.linalg.norm(self.positions[i] - self.positions[j]) < 5.0:
                    glBegin(GL_LINES)
                    glColor3f(0.5, 0.5, 0.5)
                    glVertex3f(pos[0], pos[1], pos[2])
                    glVertex3f(self.positions[j][0], self.positions[j][1], self.positions[j][2])
                    glEnd()
        
        glutSwapBuffers()

def init_gl(width, height):
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45.0, float(width)/float(height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def display():
    global simulation
    simulation.update()
    simulation.draw()

def keyboard(key, x, y):
    global simulation
    if key == b'q':
        sys.exit()
    elif key == b'r':  # 重置模拟
        simulation = ProteinSimulation()
    glutPostRedisplay()

def special(key, x, y):
    global simulation
    if key == GLUT_KEY_LEFT:
        simulation.rotate_y -= 5
    elif key == GLUT_KEY_RIGHT:
        simulation.rotate_y += 5
    elif key == GLUT_KEY_UP:
        simulation.rotate_x -= 5
    elif key == GLUT_KEY_DOWN:
        simulation.rotate_x += 5
    glutPostRedisplay()

def mouse(button, state, x, y):
    global simulation
    simulation.mouse_x = x
    simulation.mouse_y = y
    
    if state == GLUT_DOWN:
        simulation.mouse_button = button
    else:
        simulation.mouse_button = None
    
    glutPostRedisplay()

def motion(x, y):
    global simulation
    dx = x - simulation.mouse_x
    dy = y - simulation.mouse_y
    
    if simulation.mouse_button == GLUT_LEFT_BUTTON:
        # 旋转
        simulation.rotate_y += dx * 0.5
        simulation.rotate_x += dy * 0.5
    elif simulation.mouse_button == GLUT_RIGHT_BUTTON:
        # 平移
        simulation.translate_x += dx * 0.05
        simulation.translate_y -= dy * 0.05
    elif simulation.mouse_button == GLUT_MIDDLE_BUTTON:
        # 缩放
        simulation.zoom += dy * 0.1
    
    simulation.mouse_x = x
    simulation.mouse_y = y
    glutPostRedisplay()

def mouseWheel(button, dir, x, y):
    global simulation
    if dir > 0:
        simulation.zoom += 1.0
    else:
        simulation.zoom -= 1.0
    glutPostRedisplay()

def main():
    global simulation, control_panel
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Protein Simulation")
    
    init_gl(800, 600)
    simulation = ProteinSimulation()
    control_panel = ControlPanel(simulation)
    
    glutDisplayFunc(display)
    glutIdleFunc(idle)  # 使用新的idle函数
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special)
    glutMouseFunc(mouse)
    glutMotionFunc(motion)
    glutMouseWheelFunc(mouseWheel)
    
    # 添加光照效果
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    light_position = [10.0, 10.0, 10.0, 1.0]
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    
    glutMainLoop()

def idle():
    global control_panel
    simulation.update()
    control_panel.update()
    glutPostRedisplay()

if __name__ == "__main__":
    main() 