# 实验检索目录 · Experiment Index

[项目首页](../README.md) · [Agent阅读指南](agent-guide.md) · [机器目录](experiments.json) · [目录接口](agent-catalog.md)

45项实验按课程组织；可检索中文名称、英文名称、常用别名、物理主题和分析方法。每项链接进入实际文稿或数据文件。

## 普通物理实验 1 · 8项

### 单摆测重力加速度 · Determination of Gravitational Acceleration with a Simple Pendulum

标识：`course-01/pendulum`。用摆长和重复计时求周期，以周期平方对有效摆长的含截距拟合估计重力加速度，并比较小角度与非线性单摆模型。

别名：单摆实验；单摆测重力；重力加速度测量；simple pendulum；pendulum gravity experiment；gravitational acceleration；ODE；least squares。

主题：重力加速度；简谐振动；非线性单摆；小角度近似。方法：有效摆长修正；重复计时与均值统计；周期平方线性拟合与残差 / ordinary least squares；非线性运动数值求解 / nonlinear ODE integration；初始摆角参数扫描。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-01/pendulum/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-01/pendulum/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-01/pendulum/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/PendulumLab/Notebooks/Pendulum.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-01/%E5%8D%95%E6%91%86%E6%B5%8B%E9%87%8D%E5%8A%9B%E5%8A%A0%E9%80%9F%E5%BA%A6/%E7%89%9B%E9%A1%BF%E7%AC%AC%E4%BA%8C%E8%BF%90%E5%8A%A8%E5%AE%9A%E5%BE%8B%E6%B5%8B%E9%87%8D%E5%8A%9B%E5%8A%A0%E9%80%9F%E5%BA%A6%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A.pdf)

[虚拟实验](https://hnnuyuxuan.github.io/general-physics-lab/simulations/pendulum/index.html) · [模型依据](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/docs/pendulum-model-evidence.md) · [浏览器模型](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/simulations/pendulum/model.mjs) · [观测对照](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/simulations/pendulum/observations.json) · [文献题录](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/docs/pendulum-references.json) · [数值验证](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/docs/simulation/pendulum-reference.json)


### 多普勒效应的验证 · Verification of the Acoustic Doppler Effect

标识：`course-01/doppler-verification`。对静止超声声源与运动接收器的五组速度频率记录作线性回归，由斜率反演声速并与温度模型比较。

别名：多普勒效应验证；超声多普勒实验；运动接收器频移；acoustic Doppler effect；ultrasonic Doppler experiment；moving receiver；linear regression。

主题：声波多普勒效应；频移；空气声速。方法：速度与接收频率线性回归；回归斜率反演声速；温度模型声速比较；接收器速度模型扫描。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-01/doppler-verification/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-01/doppler-verification/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-01/doppler-verification/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/DopplerVerificationLab/Notebooks/DopplerVerificationLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-01/%E5%A4%9A%E6%99%AE%E5%8B%92%E6%95%88%E5%BA%94%E7%9A%84%E9%AA%8C%E8%AF%81/%E5%A4%9A%E6%99%AE%E5%8B%92%E6%95%88%E5%BA%94%E9%AA%8C%E8%AF%81%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A.pdf)


### 多普勒效应的应用 · Doppler Measurement of Spring Oscillations and Spring Stiffness

标识：`course-01/doppler-application`。结合静态加载伸长和多普勒系统保存的振动周期，比较弹簧静动态劲度系数，并分析加载基线与有效质量的影响。

别名：多普勒效应应用；弹簧振子劲度测量；弹簧动静态法；弹簧有效质量；Doppler spring oscillator；spring stiffness；dynamic and static spring methods；spring constant。

主题：弹簧简谐振动；胡克定律；非接触周期测量；弹簧有效质量。方法：静态加载比值计算；带截距力伸长回归；周期均值动态劲度计算；静态选点敏感性比较；均匀弹簧有效质量模型扫描。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-01/doppler-application/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-01/doppler-application/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-01/doppler-application/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/DopplerApplicationLab/Notebooks/DopplerApplicationLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-01/%E5%A4%9A%E6%99%AE%E5%8B%92%E6%95%88%E5%BA%94%E7%9A%84%E5%BA%94%E7%94%A8/%E5%A4%9A%E6%99%AE%E5%8B%92%E6%95%88%E5%BA%94%E7%9A%84%E5%BA%94%E7%94%A8-%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A.pdf)


### 牛顿第二定律的验证 · Verification of Newton's Second Law on an Air Track

标识：`course-01/newton-second-law`。在保持系统总质量的五组悬挂质量记录中复算加速度，对质量与加速度回归并解释系统质量和等效反向力。

别名：牛顿第二定律实验；气垫导轨加速度；恒质量变力实验；Newton's second law；air track acceleration；force and acceleration。

主题：牛顿第二定律；恒加速度运动；系统质量；等效阻力。方法：双光电门速度换算加速度；组内重复读数平均；悬挂质量对加速度含截距回归；斜率与截距物理反演；逐组暂排除拟合敏感性。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-01/newton-second-law/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-01/newton-second-law/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-01/newton-second-law/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/NewtonSecondLawLab/Notebooks/NewtonSecondLawLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-01/%E7%89%9B%E9%A1%BF%E7%AC%AC%E4%BA%8C%E5%AE%9A%E5%BE%8B%E7%9A%84%E9%AA%8C%E8%AF%81/%E7%89%9B%E9%A1%BF%E7%AC%AC%E4%BA%8C%E8%BF%90%E5%8A%A8%E5%AE%9A%E5%BE%8B%E9%AA%8C%E8%AF%81%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A.pdf)


### 碰撞规律的研究 · Momentum and Energy in One-Dimensional Collisions

标识：`course-01/collisions`。分别处理粘合碰撞的碰前后速度和弹性附件的碰后速度记录，比较动量、动能与速度比，并用恢复系数模型解释两种极限。

别名：碰撞规律实验；气垫导轨碰撞；完全非弹性碰撞；弹性碰撞速度比；one-dimensional collisions；momentum conservation；coefficient of restitution；inelastic collision。

主题：动量守恒；动能耗散；粘合碰撞；恢复系数。方法：碰前后动量与动能计算；动量亏损和动能损失率比较；碰后速度比与质量模型比较；恢复系数碰撞模型扫描。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-01/collisions/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-01/collisions/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-01/collisions/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/CollisionsLab/Notebooks/CollisionsLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-01/%E7%A2%B0%E6%92%9E%E8%A7%84%E5%BE%8B%E7%9A%84%E7%A0%94%E7%A9%B6/%E7%A2%B0%E6%92%9E%E8%A7%84%E5%BE%8B%E7%A0%94%E7%A9%B6%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A.pdf)


### 热功当量的测量 · Electrical Heating and the Mechanical Equivalent of Heat

标识：`course-01/mechanical-equivalent-heat`。对三十个时间温度记录独立求升温速率并比较拟合区间，结合电功和总热容关系讨论热功当量的计算条件。

别名：热功当量实验；电热法热功当量；水温升温曲线；mechanical equivalent of heat；electrical calorimetry；Joule heating。

主题：电功与热量；焦耳热；热容；升温速率。方法：温度时间线性回归；首尾温升速率计算；前后及中段拟合区间比较；仪器记录值与独立升温回归分列。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-01/mechanical-equivalent-heat/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-01/mechanical-equivalent-heat/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-01/mechanical-equivalent-heat/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/MechanicalEquivalentHeatLab/Notebooks/MechanicalEquivalentHeatLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-01/%E7%83%AD%E5%8A%9F%E5%BD%93%E9%87%8F%E7%9A%84%E6%B5%8B%E9%87%8F/%E7%83%AD%E5%8A%9F%E5%BD%93%E9%87%8F%E7%9A%84%E6%B5%8B%E9%87%8F%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A.pdf)


### 物质密度的测量 · Density Measurement by Buoyancy and Pycnometry

标识：`course-01/density`。由合金空气与浸水称量求固体密度，由同一比重瓶中水和盐水净质量求液体密度，并传播重复性与指定质量分量。

别名：物质密度实验；阿基米德法测密度；比重瓶测液体密度；合金与盐水密度；density measurement；Archimedes method；pycnometer；conditional uncertainty propagation。

主题：阿基米德浮力；固体密度；液体密度；共同称量输入。方法：空气与浸水视质量差换算；比重瓶净质量比计算；重复称量均值统计；指定质量误差限条件传播 / conditional uncertainty propagation。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-01/density/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-01/density/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-01/density/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/DensityLab/Notebooks/DensityLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-01/%E7%89%A9%E8%B4%A8%E5%AF%86%E5%BA%A6%E7%9A%84%E6%B5%8B%E9%87%8F/%E7%89%A9%E8%B4%A8%E5%AF%86%E5%BA%A6%E6%B5%8B%E9%87%8F%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A.pdf)


### 液体比汽化热的测量 · Specific Latent Heat of Vaporization of Water by Condensation Calorimetry

标识：`course-01/vaporization-heat`。用初末质量与温度记录建立蒸汽凝结的热平衡，扣除凝结水显热求比汽化热，并比较称量构成和末温的影响。

别名：水的汽化热；蒸汽凝结量热；水蒸气潜热；latent heat of vaporization；steam condensation calorimetry；specific latent heat of water。

主题：相变潜热；热量守恒；凝结显热；量热器热容。方法：初末称量差求凝结质量；温度电压换算；量热平衡与显热扣除；称量构成条件比较；末温灵敏度扫描。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-01/vaporization-heat/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-01/vaporization-heat/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-01/vaporization-heat/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/VaporizationHeatLab/Notebooks/VaporizationHeatLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-01/%E6%B6%B2%E4%BD%93%E6%AF%94%E6%B1%BD%E5%8C%96%E7%83%AD%E7%9A%84%E6%B5%8B%E9%87%8F/%E6%B6%B2%E4%BD%93%E6%AF%94%E6%B1%BD%E5%8C%96%E7%83%AD%E6%B5%8B%E9%87%8F%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A.pdf)


## 普通物理实验 2 · 10项

### 表面张力系数的测定(拉脱法) · Surface Tension Measurement by the Ring Detachment Method

标识：`course-02/surface-tension`。通过载荷电压标定、吊环几何与重复拉脱电压差计算表面张力，并比较逐差和回归标定的结果。

别名：表面张力系数测定；吊环拉脱法；水的表面张力；surface tension；ring detachment method；force sensor calibration；conditional uncertainty propagation。

主题：液体表面张力；充分润湿；力传感器标定；拉脱力。方法：增减载荷电压标定；逐差法与线性回归比较；吊环内外接触周界计算；拉脱电压差均值统计；重复性与分辨力条件传播 / conditional uncertainty propagation。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-02/surface-tension/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-02/surface-tension/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-02/surface-tension/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/SurfaceTensionLab/Notebooks/SurfaceTensionLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-02/01-%E8%A1%A8%E9%9D%A2%E5%BC%A0%E5%8A%9B%E7%B3%BB%E6%95%B0%E7%9A%84%E6%B5%8B%E5%AE%9A%28%E6%8B%89%E8%84%B1%E6%B3%95%29/%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A-%E8%A1%A8%E9%9D%A2%E5%BC%A0%E5%8A%9B%E7%B3%BB%E6%95%B0%E7%9A%84%E6%B5%8B%E5%AE%9A.pdf)


### 杨氏模量的测量 · Young's Modulus of a Metal Wire by Tensile Loading and an Optical Lever

标识：`course-02/young-modulus`。由加减载荷标尺读数和光杠杆几何反推金属丝伸长，修正直径零差后以逐差及回归计算杨氏模量。

别名：金属杨氏模量；拉伸法杨氏模量；光杠杆测伸长；Young's modulus；tensile wire experiment；optical lever；conditional uncertainty propagation。

主题：弹性形变；轴向拉伸；光杠杆放大；杨氏模量。方法：加减载荷标尺读数平均；测微器正零差修正；逐差与伸长回归比较；光杠杆小角度几何换算；指定标准分量条件传播 / specified uncertainty propagation。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-02/young-modulus/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-02/young-modulus/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-02/young-modulus/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/YoungModulusLab/Notebooks/YoungModulusLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-02/02-%E6%9D%A8%E6%B0%8F%E6%A8%A1%E9%87%8F%E7%9A%84%E6%B5%8B%E9%87%8F/%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A-%E6%8B%89%E4%BC%B8%E6%B3%95%E6%B5%8B%E9%87%8F%E9%87%91%E5%B1%9E%E6%9D%A8%E6%B0%8F%E6%A8%A1%E9%87%8F.pdf)


### 弦振动的研究 · Standing Waves on a Stretched String

标识：`course-02/string-vibration`。从两组弦长与驻波半波数记录复算波长，以对数回归比较张力和频率幂指数与理想弦模型。

别名：弦振动实验；弦上驻波；梅尔德实验；张力与频率幂律；standing waves on a string；Melde's experiment；stretched string vibration；log-log regression。

主题：弦上横波；驻波；张力与波速；频率波长幂律。方法：弦长与半波数复算波长；张力扫描常用对数回归；频率扫描常用对数回归；理论幂指数比较；驻波阶数与形状模型比较。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-02/string-vibration/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-02/string-vibration/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-02/string-vibration/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/StringVibrationLab/Notebooks/StringVibrationLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-02/03-%E5%BC%A6%E6%8C%AF%E5%8A%A8%E7%9A%84%E7%A0%94%E7%A9%B6/%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A-%E5%BC%A6%E6%8C%AF%E5%8A%A8%E7%9A%84%E7%A0%94%E7%A9%B6.pdf)

[虚拟实验](https://hnnuyuxuan.github.io/general-physics-lab/simulations/string-vibration/index.html) · [模型依据](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/docs/string-vibration-model-evidence.md) · [浏览器模型](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/simulations/string-vibration/model.mjs) · [观测对照](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/simulations/string-vibration/observations.json) · [文献题录](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/docs/string-vibration-references.json) · [数值验证](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/docs/simulation/string-vibration-reference.json)


### 声速的测量 · Speed of Sound by Standing-Wave and Phase-Comparison Methods

标识：`course-02/sound-speed`。分别统计驻波法与相位比较法的波长记录，结合频率计算声速，并在给定温度和气体参数下求比热容比。

别名：声速测量实验；驻波法声速；相位比较法声速；超声声速；speed of sound；standing-wave method；phase-comparison method；conditional uncertainty propagation。

主题：空气声速；声驻波；相位差；气体比热容比。方法：两法波长记录分别统计；频率与平均波长换算声速；指定波长频率分量传播 / specified uncertainty propagation；理想气体关系反推比热容比；波长标度敏感性扫描。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-02/sound-speed/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-02/sound-speed/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-02/sound-speed/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/SoundSpeedLab/Notebooks/SoundSpeedLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-02/04-%E5%A3%B0%E9%80%9F%E7%9A%84%E6%B5%8B%E9%87%8F/%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A-%E5%A3%B0%E9%80%9F%E7%9A%84%E6%B5%8B%E9%87%8F.pdf)


### 刚体转动惯量 · Moment of Inertia of Rigid Bodies and the Parallel-Axis Theorem

标识：`course-02/moment-of-inertia`。对已报角加速度求均值、由总惯量差提取附加惯量，并以圆环圆柱几何模型和偏轴距离扫描比较质量分布的作用。

别名：刚体转动惯量测定；圆环转动惯量；平行轴定理；偏轴圆柱惯量；moment of inertia；parallel-axis theorem；rigid body rotation。

主题：质量分布；转动惯量；平行轴定理；圆环与圆柱。方法：已报角加速度均值重算；已报总惯量差分；均匀圆环与圆柱几何计算；圆柱偏轴距离模型扫描。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-02/moment-of-inertia/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-02/moment-of-inertia/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-02/moment-of-inertia/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/MomentOfInertiaLab/Notebooks/MomentOfInertiaLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-02/05-%E5%88%9A%E4%BD%93%E8%BD%AC%E5%8A%A8%E6%83%AF%E9%87%8F/%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A-%E5%88%9A%E4%BD%93%E8%BD%AC%E5%8A%A8%E6%83%AF%E9%87%8F%E7%9A%84%E6%B5%8B%E5%AE%9A.pdf)


### 金属线膨胀系数的测量 · Linear Thermal Expansion of a Metal Rod

标识：`course-02/thermal-expansion`。对八组与讲义同值的温度和千分表读数作逐差及带截距回归，用给定杆长换算线胀系数。

别名：金属线膨胀系数；铜棒热膨胀；千分表伸长测量；linear thermal expansion；coefficient of linear expansion；metal rod expansion；least squares thermal expansion。

主题：线性热膨胀；线胀系数；温度与伸长；有效受热长度。方法：讲义同值温度位移数据复算；等温差逐差平均；带截距温度位移回归；斜率换算线胀系数；指定参考值比较。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-02/thermal-expansion/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-02/thermal-expansion/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-02/thermal-expansion/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/ThermalExpansionLab/Notebooks/ThermalExpansionLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-02/06-%E9%87%91%E5%B1%9E%E7%BA%BF%E8%86%A8%E8%83%80%E7%B3%BB%E6%95%B0%E7%9A%84%E6%B5%8B%E9%87%8F/%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A-%E9%87%91%E5%B1%9E%E7%BA%BF%E8%83%80%E7%B3%BB%E6%95%B0%E7%9A%84%E6%B5%8B%E9%87%8F.pdf)


### 固体导热系数的测量 · Thermal Conductivity and Specific Heat by a Quasi-Steady Heating Method

标识：`course-02/thermal-conductivity`。由中心面和加热面的十六组热电势记录求温升速率与温差，在给定几何和电阻下计算准稳态导热系数及比热容。

别名：固体导热系数；准稳态导热法；热电偶温差测量；thermal conductivity；quasi-steady heating method；specific heat measurement。

主题：傅里叶导热；准稳态热流；比热容；热电偶温差。方法：热电势换算温差；中心面温升线性回归；逐差温升速率比较；给定电阻热流密度计算；末端与平均温差导热估计。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-02/thermal-conductivity/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-02/thermal-conductivity/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-02/thermal-conductivity/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/ThermalConductivityLab/Notebooks/ThermalConductivityLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-02/07-%E5%9B%BA%E4%BD%93%E5%AF%BC%E7%83%AD%E7%B3%BB%E6%95%B0%E7%9A%84%E6%B5%8B%E9%87%8F/%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A-%E5%9B%BA%E4%BD%93%E5%AF%BC%E7%83%AD%E7%B3%BB%E6%95%B0%E7%9A%84%E6%B5%8B%E9%87%8F.pdf)


### 液体粘度系数的测量 · Liquid Viscosity by the Falling-Sphere Method

标识：`course-02/liquid-viscosity`。从小球直径和累计下落时间求区间平均速度，采用斯托克斯低雷诺数及管壁修正计算蓖麻油黏度。

别名：液体粘度系数；液体黏滞系数；落球法；蓖麻油黏度；falling-sphere viscometer；Stokes viscosity；liquid viscosity；specified uncertainty propagation。

主题：斯托克斯阻力；终端速度；低雷诺数流动；管壁修正。方法：小球直径零差修正；累计时间斜率拟合；跨间隔逐差时间比较；有限管径黏度修正；直径时间指定分量传播 / specified uncertainty propagation。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-02/liquid-viscosity/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-02/liquid-viscosity/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-02/liquid-viscosity/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/LiquidViscosityLab/Notebooks/LiquidViscosityLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-02/08-%E6%B6%B2%E4%BD%93%E7%B2%98%E5%BA%A6%E7%B3%BB%E6%95%B0%E7%9A%84%E6%B5%8B%E9%87%8F/%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A-%E6%B6%B2%E4%BD%93%E7%B2%98%E6%BB%9E%E7%B3%BB%E6%95%B0%E7%9A%84%E6%B5%8B%E9%87%8F.pdf)


### 波尔共振实验 · Pohl Resonance: Free, Damped and Forced Oscillations

标识：`course-02/pohl-resonance`。结合自由、阻尼和受迫振动记录，以累计时间对数回归求衰减率，并比较实测共振峰与线性幅相模型。

别名：波尔共振；波耳共振；弹性摆轮阻尼振动；受迫振动幅相特性；Pohl's pendulum；Pohl resonance；forced and damped oscillations；damped harmonic oscillator。

主题：阻尼振动；受迫共振；振幅包络；幅频与相频响应。方法：周期累计建立衰减时间轴；对数振幅回归；跨周期逐差衰减率计算；四象限相位模型比较；阻尼比例稳态响应扫描。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-02/pohl-resonance/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-02/pohl-resonance/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-02/pohl-resonance/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/PohlResonanceLab/Notebooks/PohlResonanceLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-02/%E6%B3%A2%E5%B0%94%E5%85%B1%E6%8C%AF%E5%AE%9E%E9%AA%8C/%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A-%E6%B3%A2%E5%B0%94%E5%85%B1%E6%8C%AF%E5%AE%9E%E9%AA%8C.pdf)


### 惯性秤的应用 · Mass Measurement with an Inertial Balance

标识：`course-02/inertial-balance`。用八组标准质量的周期平方建立含截距定标，反推圆柱惯性质量，并从斜率和截距求等效劲度与空载质量。

别名：惯性秤；周期法测质量；惯性质量定标；inertial balance；mass from oscillation period；period-squared calibration；calibration uncertainty。

主题：惯性质量；简谐振动；质量定标；空载等效质量。方法：标准质量周期平方回归；逐差定标斜率比较；未知物周期反演质量；定标参数协方差传播 / calibration covariance propagation；等效劲度与空载质量计算。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-02/inertial-balance/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-02/inertial-balance/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-02/inertial-balance/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/InertialBalanceLab/Notebooks/InertialBalanceLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-02/%E6%83%AF%E6%80%A7%E7%A7%A4%E7%9A%84%E5%BA%94%E7%94%A8/%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A-%E6%83%AF%E6%80%A7%E7%A7%A4%E7%9A%84%E5%BA%94%E7%94%A8.pdf)


## 普通物理实验 3 · 13项

### 万用电表的使用 · Use of Digital and Analog Multimeters

标识：`course-03/multimeter`。比较数字式与指针式万用表的电压电阻记录和标称值，并以串联欧姆表模型解释刻度疏密。

别名：万用电表使用；数字万用表；指针万用表；欧姆档刻度；multimeter；digital and analog meters；ohmmeter scale。

主题：电压与电阻测量；量程与分辨率；欧姆刻度非线性；标称值比较。方法：两类仪表示值对照；相对标称偏差计算；指定读格界限条件估计；串联欧姆表归一化模型；电阻比工作点扫描。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/multimeter/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/multimeter/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/multimeter/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/MultimeterLab/Notebooks/MultimeterLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-03/1%E4%B8%87%E7%94%A8%E7%94%B5%E8%A1%A8%E7%9A%84%E4%BD%BF%E7%94%A8/%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A-%E4%B8%87%E7%94%A8%E7%94%B5%E8%A1%A8%E7%9A%84%E4%BD%BF%E7%94%A8.pdf)


### 制流分压电路 · Current-Limiting and Loaded Voltage-Divider Circuits

标识：`course-03/current-voltage-divider`。在源表标度下比较三种负载比的制流和分压记录，以固定形状幅度估计及归一化扫描分析调节特性。

别名：制流分压电路；滑动变阻器两种接法；限流电路；负载分压；current-limiting circuit；loaded voltage divider；rheostat circuits。

主题：直流电阻电路；分压负载效应；调节范围；归一化电路响应。方法：三负载比位置扫描记录比较；固定电路形状单幅度最小二乘；曲线残差计算；无量纲负载比模型扫描。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/current-voltage-divider/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/current-voltage-divider/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/current-voltage-divider/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/DividerCircuitsLab/Notebooks/DividerCircuitsLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-03/2%E5%88%B6%E6%B5%81%E5%88%86%E5%8E%8B%E7%94%B5%E8%B7%AF/%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A-%E5%88%B6%E6%B5%81%E5%88%86%E5%8E%8B%E7%94%B5.pdf)


### 用稳恒电场模拟静电场 · Simulation of an Electrostatic Field with a Steady Current Field

标识：`course-03/electrostatic-field`。将同轴电极间八个电位对应的汇总半径对数线性化，比较边界解析模型并计算径向电位与场强。

别名：稳恒电流场模拟静电场；静电场模拟；同轴电极等位线；electrostatic field mapping；steady current analogy；coaxial electrodes；equipotential mapping；Laplace equation。

主题：拉普拉斯方程；电流场静电场类比；同轴电位；径向场强。方法：内点汇总半径对数线性化；含截距拟合与残差；同轴边界理论比较；电位与场强解析计算；边界电压模型扫描。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/electrostatic-field/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/electrostatic-field/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/electrostatic-field/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/ElectrostaticFieldLab/Notebooks/ElectrostaticFieldLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-03/3%E7%94%A8%E7%A8%B3%E6%81%92%E7%94%B5%E5%9C%BA%E6%A8%A1%E6%8B%9F%E9%9D%99%E7%94%B5%E5%9C%BA/%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A-%E7%94%A8%E7%A8%B3%E6%81%92%E7%94%B5%E5%9C%BA%E6%A8%A1%E6%8B%9F%E9%9D%99%E7%94%B5%E5%9C%BA.pdf)


### 电表的改装与校准 · Galvanometer Range Extension and Meter Calibration

标识：`course-03/meter-calibration`。用表头参数设计电流电压扩程，依据上下行标准读数重算校准误差，并比较电池变化时的欧姆调零可行性。

别名：电表改装与校准；表头扩程；电流表分流电阻；电压表串联电阻；meter calibration；galvanometer range extension；ammeter and voltmeter conversion。

主题：表头扩程；示值误差；往返差；欧姆表调零。方法：分流和串联电阻设计计算；标准上下行均值比较；示值误差与往返差分列；校准曲线回归；电池电压调零可行域扫描。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/meter-calibration/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/meter-calibration/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/meter-calibration/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/MeterCalibrationLab/Notebooks/MeterCalibrationLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-03/4%E7%94%B5%E8%A1%A8%E7%9A%84%E6%94%B9%E8%A3%85%E4%B8%8E%E6%A0%A1%E5%87%86/%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A-%E7%94%B5%E8%A1%A8%E7%9A%84%E6%94%B9%E8%A3%85%E4%B8%8E%E6%A0%A1%E5%87%86.pdf)


### 霍尔效应的实验研究 · Hall Effect and Four-Polarity Signal Decomposition

标识：`course-03/hall-effect`。对工作电流、励磁电流和位置三组四极性电压分别分解霍尔与背景分量，以系列内参照分析相对场和记录一致性。

别名：霍尔效应实验；霍尔电压；四极性换向法；相对磁场测量；Hall effect；Hall voltage；polarity reversal method。

主题：霍尔效应；电流磁场奇偶对称性；背景电压；相对场投影。方法：四极性电压线性投影；工作电流与励磁扫描分别回归；霍尔共模及单奇分量分解；位置系列相对场归一化；逐点极性记录比较。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/hall-effect/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/hall-effect/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/hall-effect/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/HallEffectLab/Notebooks/HallEffectLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-03/5%E9%9C%8D%E5%B0%94%E6%95%88%E5%BA%94%E7%9A%84%E5%AE%9E%E9%AA%8C%E7%A0%94%E7%A9%B6/%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A-%E9%9C%8D%E5%B0%94%E6%95%88%E5%BA%94%E7%9A%84%E5%AE%9E%E9%AA%8C%E7%A0%94%E7%A9%B6.pdf)


### 电阻伏安特性的测定 · Volt-Ampere Characteristics and Instrument Loading

标识：`course-03/resistor-iv`。分别处理两电阻的内外接伏安记录，比较比值与回归估计、选点和加载模型，并对二极管指定正向区间作半对数分析。

别名：电阻伏安特性；伏安法测电阻；电流表内接外接；二极管正向特性；volt-ampere characteristics；ammeter loading；diode forward characteristic；least squares。

主题：欧姆定律；仪表加载误差；回归区间敏感性；二极管非线性。方法：逐点电阻比值统计；带截距与过原点伏安回归；全点和高电压选点比较；仪表内阻比归一化扫描；二极管指定区间半对数拟合。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/resistor-iv/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/resistor-iv/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/resistor-iv/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/ResistorIVLab/Notebooks/ResistorIVLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-03/6%E7%94%B5%E9%98%BB%E4%BC%8F%E5%AE%89%E7%89%B9%E6%80%A7%E7%9A%84%E6%B5%8B%E5%AE%9A/%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A-%E7%94%B5%E9%98%BB%E4%BC%8F%E5%AE%89%E7%89%B9%E6%80%A7%E7%9A%84%E6%B5%8B%E5%AE%9A.pdf)


### 磁场的描绘 · Axial Magnetic Fields of Single and Helmholtz Coils

标识：`course-03/magnetic-field`。对单线圈与双线圈的两电流轴向记录比较比例和形状，并用明确中点坐标的细线圈模型探索间距与均匀性。

别名：磁场描绘；圆线圈轴向磁场；亥姆霍兹线圈；双线圈均匀场；magnetic field mapping；Helmholtz coils；axial field of a circular coil；Biot-Savart law。

主题：圆电流磁场；磁场叠加；亥姆霍兹条件；轴向均匀性。方法：单双线圈轴向记录比较；两电流响应比例检查；细圆线圈解析场叠加；中点坐标归一化场计算；线圈间距半径比扫描。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/magnetic-field/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/magnetic-field/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/magnetic-field/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/MagneticFieldLab/Notebooks/MagneticFieldLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-03/7%E7%A3%81%E5%9C%BA%E7%9A%84%E6%8F%8F%E7%BB%98/%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A-%E7%A3%81%E5%9C%BA%E7%9A%84%E6%8F%8F%E7%BB%98.pdf)


### 示波器的调节与使用 · Oscilloscope Measurements and Lissajous Figures

标识：`course-03/oscilloscope`。由示波器档位和格数复算三种波形的电压周期，结合李萨如计数求频率，并用理想轨迹比较频率比与相位。

别名：示波器调节使用；示波器读格；李萨如图形；波形有效值；oscilloscope；Lissajous figures；waveform RMS measurement。

主题：波形峰峰值与有效值；周期频率；李萨如频率比；相位差。方法：电压时间档读格换算；波形平方平均有效值计算；李萨如交点计数换算频率；理想波形比较；频率比与相位轨迹扫描。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/oscilloscope/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/oscilloscope/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/oscilloscope/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/OscilloscopeLab/Notebooks/OscilloscopeLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-03/8%E7%A4%BA%E6%B3%A2%E5%99%A8%E7%9A%84%E8%B0%83%E8%8A%82%E4%B8%8E%E4%BD%BF%E7%94%A8/%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A-%E7%A4%BA%E6%B3%A2%E5%99%A8%E7%9A%84%E8%B0%83%E8%8A%82%E5%92%8C%E4%BD%BF%E7%94%A8%E5%AE%9E%E9%AA%8C.pdf)


### 单臂电桥测电阻 · Resistance Measurement with a Wheatstone Bridge

标识：`course-03/wheatstone-bridge`。依据五组比率盘和比较臂示值计算平衡电阻，结合单桥范围条件阅读结果，并用归一化桥电压分析零点灵敏度。

别名：单臂电桥测电阻；单桥测阻；惠斯通电桥；QJ47单电桥；Wheatstone bridge；single bridge resistance measurement；null balance method。

主题：电桥平衡；比较测量；开路桥电压；零点灵敏度。方法：比率盘与比较臂换算电阻；标称偏差计算；说明书量程条件核对；归一化开路桥电压计算；比率臂灵敏度扫描。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/wheatstone-bridge/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/wheatstone-bridge/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/wheatstone-bridge/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/WheatstoneBridgeLab/Notebooks/WheatstoneBridgeLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-03/9%E5%8D%95%E8%87%82%E7%94%B5%E6%A1%A5%E6%B5%8B%E7%94%B5%E9%98%BB/%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A-%E5%8D%95%E8%87%82%E7%94%B5%E6%A1%A5%E6%B5%8B%E7%94%B5%E9%98%BB.pdf)


### 用直流双臂电桥测低电阻 · Low Resistance and Resistivity with a Kelvin Double Bridge

标识：`course-03/kelvin-bridge`。由双臂桥比率与五个长度下的比较臂示值求电阻，比较逐长度和斜率电阻率，并分析共同直径的平方影响。

别名：直流双臂电桥；凯尔文双电桥；低电阻测量；导体电阻率；Kelvin double bridge；low resistance measurement；four-terminal resistance；resistivity。

主题：低电阻比较测量；四端接法；导体电阻率；截面积敏感性。方法：面板比率换算平衡电阻；逐长度电阻率计算；电阻长度含截距回归；拟合斜率反演电阻率；直径平方敏感性扫描。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/kelvin-bridge/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/kelvin-bridge/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/kelvin-bridge/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/KelvinBridgeLab/Notebooks/KelvinBridgeLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-03/10%E7%94%A8%E7%9B%B4%E6%B5%81%E5%8F%8C%E8%87%82%E7%94%B5%E6%A1%A5%E6%B5%8B%E4%BD%8E%E7%94%B5%E9%98%BB/%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A-%E7%9B%B4%E6%B5%81%E5%8F%8C%E8%87%82%E7%94%B5%E6%A1%A5%E6%B5%8B%E4%BD%8E%E7%94%B5%E9%98%BB.pdf)


### RLC串联电路谐振特性的研究 · Resonance of a Series RLC Circuit

标识：`course-03/rlc-resonance`。从两电容和两电阻设置的频响记录定位峰值与半功率带宽，比较品质因数估计并探索理想串联电路幅相响应。

别名：RLC串联谐振；串联电路幅频特性；半功率带宽；品质因数；series RLC resonance；half-power bandwidth；quality factor。

主题：电路谐振；品质因数；幅频响应；电流相位。方法：观测电阻电压峰值定位；半功率交点线性插值；带宽品质因数计算；谐振电压比条件估计；电容与品质因数稳态模型扫描。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/rlc-resonance/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/rlc-resonance/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/rlc-resonance/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/RLCResonanceLab/Notebooks/RLCResonanceLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-03/11RLC%E4%B8%B2%E8%81%94%E7%94%B5%E8%B7%AF%E8%B0%90%E6%8C%AF%E7%89%B9%E6%80%A7%E7%9A%84%E7%A0%94%E7%A9%B6/%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A-RLC%E4%B8%B2%E8%81%94%E7%94%B5%E8%B7%AF%E8%B0%90%E6%8C%AF%E7%89%B9%E6%80%A7%E7%9A%84%E7%A0%94%E7%A9%B6%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A.pdf)

[虚拟实验](https://hnnuyuxuan.github.io/general-physics-lab/simulations/rlc-resonance/index.html) · [模型依据](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/docs/rlc-resonance-model-evidence.md) · [浏览器模型](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/simulations/rlc-resonance/model.mjs) · [观测对照](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/simulations/rlc-resonance/observations.json) · [文献题录](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/docs/rlc-resonance-references.json) · [数值验证](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/docs/simulation/rlc-resonance-reference.json)


### 交流电桥 · Capacitance and Dielectric Loss with an AC Bridge

标识：`course-03/ac-bridge`。由三组交流桥平衡参数计算电容量、串联损耗电阻和损耗因数，并用复平面扫描解释双参数平衡。

别名：交流电桥实验；电容电桥；串联损耗电阻；介质损耗因数；AC bridge；capacitance bridge；dissipation factor；complex impedance。

主题：复阻抗平衡；电容量比较测量；串联损耗等效模型；损耗角。方法：复平衡方程实虚部分离；比率臂电容和损耗换算；三组设置散布比较；损耗因数恒等关系检查；复桥输出双参数扫描。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/ac-bridge/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/ac-bridge/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/ac-bridge/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/ACBridgeLab/Notebooks/ACBridgeLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-03/12%E4%BA%A4%E6%B5%81%E7%94%B5%E6%A1%A5/%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A-%E4%BA%A4%E6%B5%81%E7%94%B5%E6%A1%A5.pdf)


### 光敏传感器光电特性研究 · Photocell Load Response and Circuit Consistency

标识：`course-03/photosensor`。由四位置五十六组取样压降换算负载电流，联合检查端电压与串联回路，并以归一化单二极管模型解释响应形状。

别名：光敏传感器光电特性；硅光电池；取样电阻测电流；光电池负载响应；photocell characteristics；silicon photovoltaic cell；single-diode model。

主题：光电转换；光电池负载回路；取样电流；单二极管归一化模型。方法：取样压降换算电流；端电压与串联回路差检查；共同负载位置响应比较；四位置原记录切换；单二极管无量纲形状扫描。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/photosensor/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/photosensor/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-03/photosensor/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/PhotosensorLab/Notebooks/PhotosensorLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-03/13%E5%85%89%E6%95%8F%E4%BC%A0%E6%84%9F%E5%99%A8%E5%85%89%E7%94%B5%E7%89%B9%E6%80%A7%E7%A0%94%E7%A9%B6/%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A-%E5%85%89%E6%95%8F%E4%BC%A0%E6%84%9F%E5%99%A8%E5%85%89%E7%94%B5%E7%89%B9%E6%80%A7%E7%A0%94%E7%A9%B6.pdf)


## 普通物理实验 4 · 14项

### 分光计的调节与使用 · Adjustment and Use of an Optical Spectrometer

标识：`course-04/spectrometer`。沿自准直、平行光和调平记录核对分光计准备条件，由五组双游标读数计算偏向角与指定标准分量。

别名：分光计调节与使用；望远镜自准直；平行光管调节；双游标测角；optical spectrometer adjustment；autocollimation；dual-vernier angle measurement。

主题：光轴与转轴调节；平行光；偏向角；圆周角差。方法：自准直与调平记录核对；度分读数换算；双游标最短圆周角差平均；五次重复性统计；指定角度分量合成。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/spectrometer/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/spectrometer/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/spectrometer/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/SpectrometerLab/Notebooks/SpectrometerLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-04/01_%E5%AE%9E%E9%AA%8C%E4%B8%80_%E5%88%86%E5%85%89%E8%AE%A1%E7%9A%84%E8%B0%83%E8%8A%82%E4%B8%8E%E4%BD%BF%E7%94%A8_%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A.pdf)


### 用分光计测三棱镜的顶角 · Prism Apex Angle by the Reflection Method

标识：`course-04/prism-apex`。将五组两面反射方向的双游标读数换算为反射夹角和棱镜顶角，处理跨零读数并统计均值与标准分量。

别名：三棱镜顶角；反射法测顶角；分光计顶角测量；prism apex angle；reflection method；angle of a prism。

主题：平面反射几何；棱镜顶角；双游标测角；跨零读数。方法：两面反射方向角差计算；双游标平均后顶角换算；圆周跨零修正；五次均值与重复性统计；指定角度分量合成。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/prism-apex/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/prism-apex/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/prism-apex/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/PrismApexLab/Notebooks/PrismApexLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-04/02_%E5%AE%9E%E9%AA%8C%E4%BA%8C_%E7%94%A8%E5%88%86%E5%85%89%E8%AE%A1%E6%B5%8B%E4%B8%89%E6%A3%B1%E9%95%9C%E7%9A%84%E9%A1%B6%E8%A7%92_%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A_A3%E5%8F%8C%E9%9D%A2%E7%A4%BA%E8%8C%83%E6%A0%BC%E5%BC%8F%E7%89%88.pdf)


### 三棱镜折射率的测定 · Prism Refractive Index by Minimum Deviation

标识：`course-04/prism-refractive-index`。从五组双游标读数求最小偏向角，以给定顶角反演棱镜折射率，并传播指定顶角和偏向角分量。

别名：三棱镜折射率；最小偏向角法；棱镜对称光路；prism refractive index；minimum deviation method；minimum angle of deviation；uncertainty propagation。

主题：斯涅尔定律；最小偏向；棱镜折射率；角度分量传播。方法：双游标偏向角重算；五次最小偏向角平均；给定顶角三角关系反演；角分转弧度导数传播 / uncertainty propagation。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/prism-refractive-index/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/prism-refractive-index/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/prism-refractive-index/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/PrismRefractiveIndexLab/Notebooks/PrismRefractiveIndexLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-04/03_%E5%AE%9E%E9%AA%8C%E4%B8%89_%E4%B8%89%E6%A3%B1%E9%95%9C%E6%8A%98%E5%B0%84%E7%8E%87%E7%9A%84%E6%B5%8B%E5%AE%9A_%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A.pdf)


### 用掠射法测定透明介质的折射率 · Liquid Refractive Index by Grazing Incidence with a Right-Angle Prism

标识：`course-04/grazing-refraction`。由五组明暗分界方向读数求平均出射角，在给定直角棱镜折射率下计算透明液体折射率及指定传播分量。

别名：掠射法测折射率；透明液体折射率；直角棱镜明暗分界；grazing-incidence refractometry；liquid refractive index；right-angle prism method；uncertainty propagation。

主题：掠入射折射；明暗边界；液体棱镜界面；折射率反演。方法：双游标边界角差计算；出射角重复均值统计；直角棱镜折射关系反演；给定棱镜与角度分量传播 / specified uncertainty propagation。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/grazing-refraction/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/grazing-refraction/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/grazing-refraction/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/GrazingRefractionLab/Notebooks/GrazingRefractionLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-04/04_%E5%AE%9E%E9%AA%8C%E5%9B%9B_%E7%94%A8%E6%8E%A0%E5%B0%84%E6%B3%95%E6%B5%8B%E5%AE%9A%E9%80%8F%E6%98%8E%E4%BB%8B%E8%B4%A8%E7%9A%84%E6%8A%98%E5%B0%84%E7%8E%87_%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A.pdf)


### 用透射光栅测定光波波长 · Wavelength Measurement with a Transmission Grating

标识：`course-04/transmission-grating`。对四条谱线的双侧游标记录重算一级衍射角，用绿线标定光栅常数并计算其他波长及双黄线色散。

别名：透射光栅测波长；光栅常数标定；汞灯谱线；双黄线色散；transmission grating；spectral wavelength measurement；angular dispersion；diffraction grating。

主题：光栅衍射；谱线波长；角度色散；标定与回代。方法：同级双侧谱线圆周角差配对；绿线波长标定光栅常数 / diffraction grating calibration；其他谱线波长反演；重复性传播与游标一致性检查；黄线角间隔色散比较。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/transmission-grating/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/transmission-grating/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/transmission-grating/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/TransmissionGratingLab/Notebooks/TransmissionGratingLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-04/05_%E5%AE%9E%E9%AA%8C%E4%BA%94_%E7%94%A8%E9%80%8F%E5%B0%84%E5%85%89%E6%A0%85%E6%B5%8B%E5%AE%9A%E5%85%89%E6%B3%A2%E6%B3%A2%E9%95%BF_%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A.pdf)


### 用光学仪器测量放大率和微小长度 · Optical Magnification and Microscopic Length Measurement

标识：`course-04/optical-magnification`。分别由标尺长度比求两种放大率，以五次目镜标定均值换算细丝宽度，并区分标定和宽度重复性。

别名：光学放大率测量；显微镜投影放大率；望远镜角放大率；测微目镜标定；optical magnification；eyepiece micrometer calibration；microscopic wire diameter；uncertainty propagation。

主题：显微镜与望远镜放大；测微刻度；微小长度；共同标定因子。方法：物像长度比计算；目镜每格值重复标定；共用标定均值换算细丝直径；标定与宽度重复性独立传播 / uncertainty propagation。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/optical-magnification/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/optical-magnification/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/optical-magnification/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/OpticalMagnificationLab/Notebooks/OpticalMagnificationLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-04/06_%E5%AE%9E%E9%AA%8C%E5%85%AD_%E7%94%A8%E5%85%89%E5%AD%A6%E4%BB%AA%E5%99%A8%E6%B5%8B%E9%87%8F%E6%94%BE%E5%A4%A7%E7%8E%87%E5%92%8C%E5%BE%AE%E5%B0%8F%E9%95%BF%E5%BA%A6_%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A.pdf)


### 牛顿环实验 · Newton's Rings and Air-Wedge Interference

标识：`course-04/newton-rings`。由六级暗环直径的隔级差与回归求平凸透镜曲率，再以五次劈尖条纹长度求细丝厚度，并探索选点和中心间隙。

别名：牛顿环实验；空气劈尖；平凸透镜曲率半径；劈尖测细丝；Newton's rings；air-wedge interference；radius of curvature；thin-film interference。

主题：等厚干涉；反射半波损失；曲率半径；劈尖厚度。方法：暗环左右位置求直径；隔级直径平方差计算；全环级含截距拟合与残差；劈尖条纹间隔换算厚度；环级选择和中心间隙模型扫描。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/newton-rings/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/newton-rings/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/newton-rings/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/NewtonRingsLab/Notebooks/NewtonRingsLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-04/07_%E5%AE%9E%E9%AA%8C%E4%B8%83_%E7%89%9B%E9%A1%BF%E7%8E%AF%E5%AE%9E%E9%AA%8C_%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A.pdf)

[虚拟实验](https://hnnuyuxuan.github.io/general-physics-lab/simulations/newton-rings/index.html) · [模型依据](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/docs/newton-rings-model-evidence.md) · [浏览器模型](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/simulations/newton-rings/model.mjs) · [观测对照](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/simulations/newton-rings/observations.json) · [文献题录](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/docs/newton-rings-references.json) · [数值验证](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/docs/simulation/newton-rings-reference.json)


### 迈克尔逊干涉仪的调节和使用 · Laser Wavelength Measurement with a Michelson Interferometer

标识：`course-04/michelson-interferometer`。用五次每次一百条纹的动镜位移记录，按二倍光程差关系计算激光波长并比较重复性及指定参考值。

别名：迈克尔逊干涉仪；动镜位移测波长；条纹计数法；Michelson interferometer；laser wavelength measurement；fringe counting。

主题：分振幅干涉；往返光程差；激光波长；条纹计数。方法：动镜起止位置求位移；往返光程与条纹数换算；五次波长均值和A类统计；指定参考波长相对差比较。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/michelson-interferometer/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/michelson-interferometer/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/michelson-interferometer/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/MichelsonInterferometerLab/Notebooks/MichelsonInterferometerLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-04/08_%E5%AE%9E%E9%AA%8C%E5%85%AB_%E8%BF%88%E5%85%8B%E5%B0%94%E9%80%8A%E5%B9%B2%E6%B6%89%E4%BB%AA%E7%9A%84%E8%B0%83%E8%8A%82%E5%92%8C%E4%BD%BF%E7%94%A8_%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A.pdf)


### 薄透镜焦距的测定 · Focal Length of Thin Convex and Concave Lenses

标识：`course-04/thin-lens`。分别计算四种方法各五次长度记录的凸凹透镜焦距，比较方法均值与重复性，并探索近轴光线和二次成像临界条件。

别名：薄透镜焦距；自准直法；物距像距法；贝塞尔二次成像法；thin lens focal length；Bessel method；concave lens auxiliary imaging。

主题：近轴薄透镜；物像共轭；焦距符号；二次成像条件。方法：自准直焦距统计；物距像距公式逐次计算；二次成像位置差计算；凹透镜虚物距辅助成像；光线几何与双像分支扫描。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/thin-lens/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/thin-lens/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/thin-lens/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/ThinLensLab/Notebooks/ThinLensLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-04/09_%E5%AE%9E%E9%AA%8C%E4%B9%9D_%E8%96%84%E9%80%8F%E9%95%9C%E7%84%A6%E8%B7%9D%E7%9A%84%E6%B5%8B%E5%AE%9A_%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A.pdf)


### 偏振光的观察与分析 · Polarization, Malus's Law and Brewster's Angle

标识：`course-04/polarization`。以五次布儒斯特角求玻璃折射率，对十组检偏器光电流拟合带背景马吕斯关系，并扫描模型角度零点。

别名：偏振光观察分析；马吕斯定律；布儒斯特角；检偏器光强；polarization of light；Malus's law；Brewster angle；uncertainty propagation。

主题：线偏振；反射偏振；马吕斯关系；恒定背景电流。方法：布儒斯特角平均反推折射率；方向余弦平方线性化；光电流带背景拟合与残差；角度重复性传播 / repeatability uncertainty propagation；检偏器零点模型扫描。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/polarization/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/polarization/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/polarization/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/PolarizationLab/Notebooks/PolarizationLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-04/10_%E5%AE%9E%E9%AA%8C%E5%8D%81_%E5%81%8F%E6%8C%AF%E5%85%89%E7%9A%84%E8%A7%82%E5%AF%9F%E4%B8%8E%E5%88%86%E6%9E%90.pdf)


### 用旋光仪测定旋光性溶液的旋光率和浓度 · Optical Rotation and Conditional Solution Concentration by Polarimetry

标识：`course-04/optical-rotation`。从五组双游标平衡读数求旋光角大小，在给定蔗糖比旋光率和管长下计算条件浓度及角度重复性传播分量。

别名：旋光仪实验；旋光率与浓度；蔗糖旋光；旋光角大小；polarimetry；optical rotation；specific rotation and concentration；specified uncertainty propagation。

主题：旋光性；比旋光率；溶液条件浓度；双游标角差。方法：样品前后最短圆周角差；双游标绝对角差平均；给定比旋光率与管长浓度反演；旋光角重复性分量传播 / repeatability uncertainty propagation；两游标一致性比较。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/optical-rotation/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/optical-rotation/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/optical-rotation/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/OpticalRotationLab/Notebooks/OpticalRotationLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-04/11_%E5%AE%9E%E9%AA%8C%E5%8D%81%E4%B8%80_%E7%94%A8%E6%97%8B%E5%85%89%E4%BB%AA%E6%B5%8B%E5%AE%9A%E6%97%8B%E5%85%89%E6%80%A7%E6%BA%B6%E6%B6%B2%E7%9A%84%E6%97%8B%E5%85%89%E7%8E%87%E5%92%8C%E6%B5%93%E5%BA%A6_%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A_A3%E5%8F%8C%E9%9D%A2%E7%A4%BA%E8%8C%83%E6%A0%BC%E5%BC%8F%E7%89%88.pdf)


### 单缝衍射光强分布研究 · Single-Slit Diffraction and Intensity Distribution

标识：`course-04/single-slit-diffraction`。由四级暗纹位置计算狭缝宽度并检查近轴几何，将归一化扫描与该缝宽的理想衍射分布比较。

别名：单缝衍射；夫琅禾费单缝；暗纹法测缝宽；衍射光强分布；single-slit diffraction；Fraunhofer diffraction；sinc-squared intensity；slit width。

主题：夫琅禾费衍射；暗纹几何；狭缝宽度；归一化光强。方法：四级暗纹逐级缝宽反演；过原点缝宽拟合；带截距中心偏移检查；精确正弦几何修正；归一化扫描与缝宽模型比较。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/single-slit-diffraction/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/single-slit-diffraction/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/single-slit-diffraction/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/SingleSlitDiffractionLab/Notebooks/SingleSlitDiffractionLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-04/12_%E5%AE%9E%E9%AA%8C%E5%8D%81%E4%BA%8C_%E5%8D%95%E7%BC%9D%E8%A1%8D%E5%B0%84%E5%85%89%E5%BC%BA%E5%88%86%E5%B8%83%E7%A0%94%E7%A9%B6.pdf)


### 阿贝成像原理和空间滤波 · Abbe Imaging and Spatial Filtering

标识：`course-04/abbe-imaging`。用后焦面五级频谱位置求光栅周期，结合不同空间滤波的记录可见度，以复振幅频谱选择解释像结构。

别名：阿贝成像；空间滤波；光学傅里叶变换；后焦面频谱；Abbe imaging；spatial filtering；Fourier optics；coherent imaging。

主题：相干成像；空间频谱；复振幅滤波；像强度与可见度。方法：正负一级频谱位置平均；全级次位置含截距回归；波长焦距换算光栅周期；记录滤波方式与可见度对照；复振幅滤波关系解释。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/abbe-imaging/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/abbe-imaging/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/abbe-imaging/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/AbbeImagingLab/Notebooks/AbbeImagingLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-04/13_%E5%AE%9E%E9%AA%8C%E5%8D%81%E4%B8%89_%E9%98%BF%E8%B4%9D%E6%88%90%E5%83%8F%E5%8E%9F%E7%90%86%E5%92%8C%E7%A9%BA%E9%97%B4%E6%BB%A4%E6%B3%A2.pdf)


### 全息照相 · Holographic Recording Conditions and Reconstruction Magnification

标识：`course-04/holography`。由三组光强和物像尺寸记录计算光强比、曝光量与再现放大率，并用理想平面波关系推算条纹间距和可见度。

别名：全息照相；物光与参考光；全息记录再现；双束干涉条纹；holography；holographic recording；holographic reconstruction；fringe visibility。

主题：相干干涉记录；光强平衡；理论条纹间距；再现横向放大率。方法：参考物光光强比计算；双束夹角条纹间距静态推算；理想相干可见度计算；平均总光强曝光量换算；物像尺寸比与重复性统计。

[实验入口](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/holography/README.md) · [报告](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/holography/report/report.md) · [Jupyter](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/experiments/course-04/holography/notebooks/analysis.ipynb) · [Wolfram](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/notebook/paclets/HolographyLab/Notebooks/HolographyLab.nb) · [源PDF](https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/pdf/course-04/14_%E5%AE%9E%E9%AA%8C%E5%8D%81%E5%9B%9B_%E5%85%A8%E6%81%AF%E7%85%A7%E7%9B%B8_%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A.pdf)
