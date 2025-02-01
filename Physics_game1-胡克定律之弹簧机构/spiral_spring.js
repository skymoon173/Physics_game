class SpiralSpringSimulation {
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
        this.restLength = 100;      // 增加自然长度
        this.gloveRadius = 20; // 手套半径
        this.wallWidth = 50;  // 墙的宽度
        this.maxStretch = 250; // 最大拉伸距离
        this.groundY = 280; // 地面高度

        // 弹簧绘制参数
        this.springCoils = 15;     // 弹簧圈数
        this.springRadius = 15;    // 弹簧半径
        this.springWidth = 50;     // 弹簧自然状态下的宽度

        // 运动控制
        this.velocity = 0;
        this.isDragging = false;
        this.isRunning = true;
        this.idealMode = true;

        // 能量历史记录
        this.energyHistory = [];
        this.maxEnergyPoints = 200;

        // 添加弹簧的最小压缩长度
        this.minSpringLength = 40;  // 增加最小压缩长度

        this.setupEventListeners();
        this.setupControls();
        this.setupButtons();
        this.animate();
    }

    drawSpring(startX, endX, centerY) {
        // 计算弹簧实际连接点（球的左边缘）
        const gloveEdgeX = endX + this.gloveRadius;
        
        this.simCtx.beginPath();
        this.simCtx.moveTo(startX, centerY);
        
        // 计算当前弹簧的总长度，确保不小于最小压缩长度
        const currentWidth = Math.max(gloveEdgeX - startX, this.minSpringLength);
        
        // 弹簧的视觉参数随弹性系数变化
        const stiffnessFactor = this.springConstant / 50; // 50是默认弹性系数
        const effectiveRadius = this.springRadius * (1 / Math.sqrt(stiffnessFactor));
        
        // 绘制弹簧的螺旋
        for (let i = 0; i <= this.springCoils * 16; i++) {
            const x = startX + (i * currentWidth) / (this.springCoils * 16);
            const ratio = i / (this.springCoils * 16);
            
            // 使用正弦函数创建螺旋效果，弹簧半径随压缩程度和弹性系数变化
            const compressionRatio = currentWidth / this.restLength;
            const amplitude = effectiveRadius * Math.min(1, 1/Math.sqrt(compressionRatio));
            const y = centerY + amplitude * Math.sin(i * Math.PI * 2 / 16);
            
            if (i === 0) {
                this.simCtx.moveTo(x, y);
            } else {
                this.simCtx.lineTo(x, y);
            }
        }

        // 连接到球的边缘
        this.simCtx.lineTo(gloveEdgeX, centerY);

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
        this.drawSpring(springStartX, this.gloveX - this.gloveRadius * 2, this.gloveY);

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
                
                // 限制手套移动，考虑最小弹簧长度和球的半径
                const minX = this.wallX + this.wallWidth/2 + this.minSpringLength + this.gloveRadius;
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
        const springEndX = this.wallX + this.wallWidth/2;
        const displacement = (this.gloveX - springEndX) - this.restLength;
        
        const kineticEnergy = 0.5 * this.mass * this.velocity * this.velocity;
        const potentialEnergy = 0.5 * this.springConstant * displacement * displacement;
        const totalEnergy = kineticEnergy + potentialEnergy;

        document.getElementById('kineticValue').textContent = kineticEnergy.toFixed(2);
        document.getElementById('potentialValue').textContent = potentialEnergy.toFixed(2);
        document.getElementById('totalValue').textContent = totalEnergy.toFixed(2);

        const maxEnergy = Math.max(totalEnergy, 100);
        
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

        return { kinetic: kineticEnergy, potential: potentialEnergy, total: totalEnergy };
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

        let maxEnergy = 1;
        this.energyHistory.forEach(energy => {
            maxEnergy = Math.max(maxEnergy, energy.total);
        });

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
            const springEndX = this.wallX + this.wallWidth/2;
            // 计算到球边缘的位移
            const displacement = (this.gloveX - this.gloveRadius - springEndX) - this.restLength;
            
            // 计算弹力，考虑最小压缩长度
            let springForce;
            if (this.gloveX - this.gloveRadius - springEndX <= this.minSpringLength) {
                // 达到最小压缩长度时，使用非常大的弹力阻止进一步压缩
                springForce = 2000 * (this.minSpringLength - (this.gloveX - this.gloveRadius - springEndX));
            } else {
                springForce = -this.springConstant * displacement;
            }
            
            let netForce = springForce;
            
            if (!this.idealMode) {
                const frictionForce = -this.friction * Math.sign(this.velocity) * Math.abs(springForce);
                netForce += frictionForce;
            }
            
            const acceleration = netForce / this.mass;
            this.velocity += acceleration * 0.016;
            this.gloveX += this.velocity * 0.016;

            // 确保手套不会压缩弹簧超过最小长度
            const minX = springEndX + this.minSpringLength + this.gloveRadius;
            if (this.gloveX < minX) {
                this.gloveX = minX;
                this.velocity = -this.velocity * 0.8;
            }
            this.gloveX = Math.min(this.gloveX, 750);
        }

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
    new SpiralSpringSimulation();
}; 