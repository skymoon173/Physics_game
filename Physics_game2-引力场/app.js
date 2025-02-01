// 基本设置
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// 添加光源
const light = new THREE.PointLight(0xffffff, 1.5, 200);
light.position.set(0, 50, 0);
scene.add(light);

// 添加环境光
const ambientLight = new THREE.AmbientLight(0x404040);
scene.add(ambientLight);

// 创建网格
const gridSize = 100;
const gridDivisions = 50;
const planeGeometry = new THREE.PlaneGeometry(gridSize, gridSize, gridDivisions, gridDivisions);
const planeMaterial = new THREE.MeshBasicMaterial({ color: 0x0077ff, wireframe: true });
const plane = new THREE.Mesh(planeGeometry, planeMaterial);
plane.rotation.x = -Math.PI / 2;
scene.add(plane);

// 创建动感太阳
const sunGeometry = new THREE.SphereGeometry(2, 32, 32);
const sunMaterial = new THREE.MeshStandardMaterial({ color: 0xffaa00, metalness: 1, roughness: 0.5, emissive: 0xffaa00, emissiveIntensity: 0.9 });
const sun = new THREE.Mesh(sunGeometry, sunMaterial);
sun.position.set(0, 0, 0);
scene.add(sun);

// 行星类
class Planet {
    constructor(radius, distance, color, velocity) {
        this.radius = radius;
        this.distance = distance;
        this.color = color;
        this.velocity = velocity;
        
        const geometry = new THREE.SphereGeometry(radius, 32, 32);
        const material = new THREE.MeshStandardMaterial({ color: color, metalness: 0.8, roughness: 0.2 });
        this.mesh = new THREE.Mesh(geometry, material);
        this.mesh.position.x = distance;
        
        scene.add(this.mesh);
    }

    update(gravitationalForce) {
        const dx = sun.position.x - this.mesh.position.x;
        const dy = sun.position.y - this.mesh.position.y;
        const dz = sun.position.z - this.mesh.position.z;
        const distance = Math.sqrt(dx * dx + dy * dy + dz * dz);
        const forceMagnitude = gravitationalForce / (distance * distance);
        const force = new THREE.Vector3(dx, dy, dz).normalize().multiplyScalar(forceMagnitude);
        
        this.velocity.add(force);
        this.mesh.position.add(this.velocity);
    }
}

// 创建行星
const planets = [
    new Planet(0.5, 10, 0x0000ff, new THREE.Vector3(0, 0, 0.05)),
    new Planet(0.8, 20, 0xff0000, new THREE.Vector3(0, 0, 0.03)),
    new Planet(1, 30, 0x00ff00, new THREE.Vector3(0, 0, 0.02))
];

// 设置相机位置
camera.position.z = 100;

// 控制器设置
const controls = new THREE.OrbitControls(camera, renderer.domElement);

// 更新网格顶点以模拟引力效应
function updateGrid() {
    const vertices = plane.geometry.attributes.position.array;
    for (let i = 0; i < vertices.length; i += 3) {
        const x = vertices[i];
        const z = vertices[i + 1];
        const distance = Math.sqrt(x * x + z * z);
        const gravityEffect = Math.exp(-distance / 10) * 5; // 模拟引力效应
        vertices[i + 2] = -gravityEffect;
    }
    plane.geometry.attributes.position.needsUpdate = true;
}

// 更新行星位置
function updatePlanets() {
    const gravitationalForce = 0.1;
    planets.forEach(planet => planet.update(gravitationalForce));
}

// 渲染循环
function animate() {
    requestAnimationFrame(animate);
    updateGrid();
    updatePlanets();
    
    // 让太阳旋转以增加动感效果
    sun.rotation.y += 0.01;

    controls.update();
    renderer.render(scene, camera);
}
animate();

// 调整窗口大小
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});
