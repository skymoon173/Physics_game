class SpringSimulation {
    constructor() {
        // 初始化模拟画布
        this.simCanvas = document.getElementById('simulationCanvas');
        this.simCtx = this.simCanvas.getContext('2d');
        this.simCanvas.width = 800;
        this.simCanvas.height = 300;

        // 初始化能量图表画布
        this.graphCanvas = document.getElementById('energyGraph');
        this.graphCtx = this.graphCanvas.getContext('2d');
        this.graphCanvas.width = 800;
        this.graphCanvas.height = 200;

        // 物理参数
        this.springConstant = 50; // N/m
        this.mass = 2; // kg
        this.friction = 0.2;
        this.gravity = 9.81; // m/s^2

        // 修改物理参数和初始位置
        this.wallX = 200;  // 墙的位置
        this.wallY = 200;  // 墙的垂直位置
        this.gloveY = 250; // 手套在地面上方一点
        this.gloveX = 300; // 手套的初始水平位置
        this.restLength = 50; // 弹簧自然长度
        this.gloveRadius = 20; // 添加手套半径属性
        this.wallWidth = 50;  // 添加墙的宽度属性
        this.maxStretch = 250; // 最大拉伸距离
        this.isRunning = true; // 添加运动控制标志
        this.groundY = 280; // 地面高度

        // 手套状态
        this.velocity = 0;
        this.isDragging = false;

        // 能量历史记录
        this.energyHistory = [];
        this.maxEnergyPoints = 200;

        // 添加理想模式标志
        this.idealMode = true; // 理想模式（无摩擦力）

        // 添加弹簧绘制参数
        this.springCoils = 12;     // 弹簧圈数
        this.springRadius = 15;    // 弹簧半径
        this.springWidth = 50;     // 弹簧自然状态下的宽度

        this.setupEventListeners();
        this.setupControls();
        this.setupButtons();
        this.animate();
    }

    setupEventListeners() {
        this.simCanvas.addEventListener('mousedown', (e) => {
            const rect = this.simCanvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            if (Math.abs(x - this.gloveX) < this.gloveRadius && 
                Math.abs(y - this.gloveY) < this.gloveRadius) {
                this.isDragging = true;
            }
        });

        this.simCanvas.addEventListener('mousemove', (e) => {
            if (this.isDragging) {
                const rect = this.simCanvas.getBoundingClientRect();
                const newX = e.clientX - rect.left;
                
                // 限制手套只能在墙的右侧移动
                const minX = this.wallX + this.wallWidth/2 + this.gloveRadius;
                this.gloveX = Math.max(minX, Math.min(newX, 750));
                this.velocity = 0;
            }
        });

        this.simCanvas.addEventListener('mouseup', () => {
            this.isDragging = false;
        });
    }

    setupControls() {
        const springConstantInput = document.getElementById('springConstant');
        const massInput = document.getElementById('mass');
        const frictionInput = document.getElementById('friction');

        springConstantInput.addEventListener('input', (e) => {
            this.springConstant = Number(e.target.value);
            document.getElementById('springConstantValue').textContent = this.springConstant;
        });

        massInput.addEventListener('input', (e) => {
            this.mass = Number(e.target.value);
            document.getElementById('massValue').textContent = this.mass;
        });

        frictionInput.addEventListener('input', (e) => {
            this.friction = Number(e.target.value) / 100;
            document.getElementById('frictionValue').textContent = this.friction;
            // 当摩擦系数为0时切换到理想模式
            this.idealMode = this.friction === 0;
        });
    }

    setupButtons() {
        const stopButton = document.getElementById('stopButton');
        const resetButton = document.getElementById('resetButton');

        stopButton.addEventListener('click', () => {
            this.isRunning = !this.isRunning;
            if (!this.isRunning) {
                this.velocity = 0;
                stopButton.textContent = '继续运动';
                stopButton.classList.add('stopped');
            } else {
                stopButton.textContent = '停止运动';
                stopButton.classList.remove('stopped');
            }
        });

        resetButton.addEventListener('click', () => {
            this.gloveX = 300;
            this.velocity = 0;
            this.energyHistory = [];
        });
    }

    calculateEnergies() {
        // 计算位移（从弹簧右端到手套中心）
        const springEndX = this.wallX + this.wallWidth/2;
        const displacement = (this.gloveX - springEndX) - this.restLength;
        
        // 计算动能
        const kineticEnergy = 0.5 * this.mass * this.velocity * this.velocity;
        
        // 计算弹性势能
        const potentialEnergy = 0.5 * this.springConstant * displacement * displacement;

        const totalEnergy = kineticEnergy + potentialEnergy;

        // 更新数值显示
        document.getElementById('kineticValue').textContent = kineticEnergy.toFixed(2);
        document.getElementById('potentialValue').textContent = potentialEnergy.toFixed(2);
        document.getElementById('totalValue').textContent = totalEnergy.toFixed(2);

        // 更新能量条
        const maxEnergy = Math.max(totalEnergy, 100); // 设置最小刻度为100J
        
        // 更新柱状图
        const updateBar = (id, value) => {
            const bar = document.getElementById(id);
            const barValue = document.getElementById(id + 'Value');
            const percentage = (value / maxEnergy) * 100;
            bar.style.width = `${percentage}%`;
            barValue.textContent = `${value.toFixed(2)} J`;
        };

        updateBar('kineticBar', kineticEnergy);
        updateBar('potentialBar', potentialEnergy);
        updateBar('totalBar', totalEnergy);

        return {
            kinetic: kineticEnergy,
            potential: potentialEnergy,
            total: totalEnergy
        };
    }

    drawSpring(startX, endX, centerY) {
        this.simCtx.beginPath();
        this.simCtx.moveTo(startX, centerY);
        
        // 计算当前弹簧的总长度
        const currentWidth = endX - startX;
        
        // 计算每个螺旋的宽度
        const coilWidth = currentWidth / (this.springCoils + 1);
        
        // 绘制弹簧的螺旋
        for (let i = 0; i <= this.springCoils * 16; i++) {
            const x = startX + (i * currentWidth) / (this.springCoils * 16);
            const ratio = i / (this.springCoils * 16);
            
            // 使用正弦函数创建螺旋效果
            const amplitude = this.springRadius * (1 - 0.3 * Math.abs(2 * ratio - 1));
            const y = centerY + amplitude * Math.sin(i * Math.PI * 2 / 16);
            
            if (i === 0) {
                this.simCtx.moveTo(x, y);
            } else {
                this.simCtx.lineTo(x, y);
            }
        }

        // 连接到终点
        this.simCtx.lineTo(endX, centerY);
        
        this.simCtx.strokeStyle = '#000';
        this.simCtx.lineWidth = 2;
        this.simCtx.stroke();
    }

    drawSimulation() {
        this.simCtx.clearRect(0, 0, this.simCanvas.width, this.simCanvas.height);

        // 绘制地面
        this.simCtx.fillStyle = '#888';
        this.simCtx.fillRect(0, this.groundY, this.simCanvas.width, 20);

        // 绘制墙
        this.simCtx.fillStyle = '#666';
        this.simCtx.fillRect(this.wallX - this.wallWidth/2, 0, this.wallWidth, this.groundY);

        // 绘制弹簧
        const springStartX = this.wallX + this.wallWidth/2;
        this.drawSpring(springStartX, this.gloveX - this.gloveRadius, this.gloveY);

        // 绘制拳击手套
        this.simCtx.fillStyle = 'red';
        this.simCtx.beginPath();
        this.simCtx.arc(this.gloveX, this.gloveY, this.gloveRadius, 0, Math.PI * 2);
        this.simCtx.fill();

        // 添加拳击手套的装饰
        this.simCtx.beginPath();
        this.simCtx.arc(this.gloveX, this.gloveY, this.gloveRadius * 0.7, 0, Math.PI * 2);
        this.simCtx.strokeStyle = '#800000';
        this.simCtx.lineWidth = 2;
        this.simCtx.stroke();

        // 添加物理量显示
        this.simCtx.font = '14px Arial';
        this.simCtx.fillStyle = 'black';
        const springEndX = this.wallX + this.wallWidth/2;
        const displacement = (this.gloveX - springEndX) - this.restLength;
        this.simCtx.fillText(`形变量: ${displacement.toFixed(2)} m`, 10, 30);
        this.simCtx.fillText(`弹力: ${(-this.springConstant * displacement).toFixed(2)} N`, 10, 50);
        this.simCtx.fillText(`速度: ${this.velocity.toFixed(2)} m/s`, 10, 70);
    }

    drawEnergyGraph() {
        this.graphCtx.clearRect(0, 0, this.graphCanvas.width, this.graphCanvas.height);
        
        // 绘制背景网格
        this.graphCtx.strokeStyle = '#eee';
        this.graphCtx.beginPath();
        for (let i = 0; i < this.graphCanvas.width; i += 50) {
            this.graphCtx.moveTo(i, 0);
            this.graphCtx.lineTo(i, this.graphCanvas.height);
        }
        for (let i = 0; i < this.graphCanvas.height; i += 50) {
            this.graphCtx.moveTo(0, i);
            this.graphCtx.lineTo(this.graphCanvas.width, i);
        }
        this.graphCtx.stroke();

        // 找到最大能量值用于缩放
        let maxEnergy = 1;
        this.energyHistory.forEach(energy => {
            maxEnergy = Math.max(maxEnergy, energy.total);
        });

        // 绘制能量曲线
        const drawLine = (data, color) => {
            this.graphCtx.beginPath();
            this.graphCtx.strokeStyle = color;
            this.graphCtx.lineWidth = 2;
            data.forEach((energy, i) => {
                const x = (i / (this.maxEnergyPoints - 1)) * this.graphCanvas.width;
                const y = this.graphCanvas.height - (energy / maxEnergy) * (this.graphCanvas.height - 20);
                if (i === 0) this.graphCtx.moveTo(x, y);
                else this.graphCtx.lineTo(x, y);
            });
            this.graphCtx.stroke();
        };

        drawLine(this.energyHistory.map(e => e.total), 'black');
        drawLine(this.energyHistory.map(e => e.kinetic), 'blue');
        drawLine(this.energyHistory.map(e => e.potential), 'red');

        // 绘制图例
        this.graphCtx.font = '12px Arial';
        this.graphCtx.fillStyle = 'black';
        this.graphCtx.fillText('总能量', 10, 20);
        this.graphCtx.fillStyle = 'blue';
        this.graphCtx.fillText('动能', 70, 20);
        this.graphCtx.fillStyle = 'red';
        this.graphCtx.fillText('势能', 120, 20);
    }

    update() {
        if (!this.isDragging && this.isRunning) {
            // 计算弹力
            const springEndX = this.wallX + this.wallWidth/2;
            const displacement = (this.gloveX - springEndX) - this.restLength;
            const springForce = -this.springConstant * displacement;
            
            let netForce = springForce;
            
            // 在非理想模式下添加摩擦力
            if (!this.idealMode) {
                const frictionForce = -this.friction * Math.sign(this.velocity) * Math.abs(springForce);
                netForce += frictionForce;
            }
            
            // 更新速度和位置
            const acceleration = netForce / this.mass;
            this.velocity += acceleration * 0.016;
            this.gloveX += this.velocity * 0.016;

            // 处理与墙的完全弹性碰撞
            const minX = this.wallX + this.wallWidth/2 + this.gloveRadius;
            if (this.gloveX < minX) {
                this.gloveX = minX;
                this.velocity = -this.velocity; // 完全弹性碰撞
            }
            this.gloveX = Math.min(this.gloveX, 750);
        }

        // 更新能量历史
        const energies = this.calculateEnergies();
        this.energyHistory.push(energies);
        if (this.energyHistory.length > this.maxEnergyPoints) {
            this.energyHistory.shift();
        }
    }

    animate() {
        this.update();
        this.drawSimulation();
        this.drawEnergyGraph();
        requestAnimationFrame(() => this.animate());
    }
}

// 启动模拟
window.onload = () => {
    new SpringSimulation();
}; 