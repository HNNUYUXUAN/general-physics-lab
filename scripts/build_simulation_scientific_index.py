"""Build the public simulation scientific index from reviewed repository records.

The optional literature manifests permit actual local PDF hash checks; ordinary
clones use published reading records and explicitly record not_requested.
"""
from pathlib import Path
import argparse,collections,datetime,hashlib,json,re

THEORY_MAP = {'pendulum': ('mechanics', '有限摆角无阻尼单摆、周期积分', '原摆长/球径与教学初角、重力输入', '理想质点、定长轻绳；角度以弧度进入方程', '椭圆积分、ODE、守恒与步长收敛'),
 'density': ('mechanics',
             '阿基米德浮力与比重瓶质量守恒',
             '原空瓶均值/采用水密度；待测物密度为教学输入',
             '完整浸没、同温同容积称量；部分浸没另列',
             '独立力平衡求根、体积及数值灵敏度'),
 'collisions': ('mechanics', '一维动量守恒与恢复系数碰撞', '原滑块质量/入射速度；恢复系数和挡片为教学输入', '无外力冲量、瞬时碰撞；有向速度', '独立冲量方程、动量与能量极限'),
 'newton-second-law': ('mechanics',
                       '恒总质量加速与有限挡片过门',
                       '原挂码系列/门距；总质量与反向力为教学输入',
                       '理想轻绳滑轮、恒加速度；区间测速和瞬时量分组',
                       'ODE门事件、有限挡片解析偏差与零宽极限'),
 'inertial-balance': ('mechanics',
                      '含空载有效质量的小位移振子',
                      '原标准质量定标；未知物不进入定标',
                      '线性无阻尼有效模型、标准范围与扩展教学域分列',
                      'ODE周期与标准/未知分组反演'),
 'young-modulus': ('mechanics',
                   '线弹性伸长与反射光杠杆',
                   '原几何/零差；模量与实体直径为教学输入',
                   '轴向线弹性、动足几何；小角回归与精确前向分列',
                   '独立刚度离散与反射向量'),
 'surface-tension': ('mechanics',
                     '吊环双周界、润湿角与传感器定标',
                     '原环径/参考表面张力；传感器及膜重为教学输入',
                     '准静态、同基线；膜重和接触角分项',
                     '周界数值积分、独立标定回归与力平衡'),
 'moment-of-inertia': ('mechanics',
                       '悬挂平动与平台转动耦合、配对消摩擦',
                       '原装载几何/塔轮；平台惯量及挂码为教学输入',
                       '不滑轻绳、恒摩擦；只取正转八次半圈',
                       '径向质量积分、约束方程与ODE门事件'),
 'pohl-resonance': ('mechanics',
                    '小角黏滞阻尼受迫扭振完整初值解',
                    '固有周期/阻尼/力矩为独立小角教学输入',
                    '线性欠阻尼小角；原大角观测单列',
                    'DOP853、复频响应与输入/耗散能量平衡'),
 'string-vibration': ('mechanics',
                      '固定端均匀弦本征模态',
                      '原长度/张力；文献线密度0.570g/m',
                      '小横振、恒张力；归一化振幅表示模态',
                      '离散本征值、网格收敛与幂律极限'),
 'doppler-verification': ('acoustics',
                          '固定源、匀速移动接收器单程多普勒',
                          '原载频/温度；运动速度为教学控制',
                          '静止均匀空气；接收器不穿越声源',
                          '独立波前与接收轨迹交点'),
 'doppler-application': ('acoustics',
                         '弹簧振子移动接收器与有向频移',
                         '原振子质量/静态基线；弹簧质量等为教学输入',
                         '单程声路；均匀弹簧有效质量近似',
                         '机械ODE、迟滞传播相位导数与静动态反演'),
 'sound-speed': ('acoustics',
                 '往返几何级数驻波、单程相位定位',
                 '原频率/比较声速；往返因子和电子相位为教学输入',
                 '驻波腔与低反馈相位情景分列',
                 '有限多路径复和、标序回归与相位间隔'),
 'rlc-resonance': ('circuits',
                   '串联RLC线性稳态复阻抗',
                   '原L/C；电源幅度和总损耗按各自身份登记',
                   '集总、恒幅正弦、等效总串联损耗',
                   '独立复数节点方程、半功率与频率极限'),
 'current-voltage-divider': ('circuits',
                             '串联制流与负载三端分压器',
                             '电源/电阻/负载比为独立教学值',
                             '理想电源、线性滑片；原读数单位待确认',
                             '270组独立节点矩阵、滑片两端极限'),
 'resistor-iv': ('circuits', '有限电表内阻的内外接伏安电路', '待测电阻与电表内阻为教学值', '欧姆电阻、实际端电压；原二极管观测单列', '162组独立节点/并联支路方程'),
 'wheatstone-bridge': ('circuits', '单臂电桥与有限检流计', '绝对阻值/电源/检流计为教学值', '正电阻、线性支路；零检测与失衡分列', '独立双节点矩阵与平衡反演'),
 'ac-bridge': ('circuits', '有损电容的复阻抗电桥', '原第一组校准情景与指定标准臂', '串联等效损耗、频率无关元件', '复数节点矩阵、实虚双平衡条件'),
 'oscilloscope': ('circuits',
                  '时域波形、格数游标和XY相位',
                  '原示意幅频；显示刻度/频比为教学值',
                  '理想显示窗口、溢出裁切；波形RMS分定义',
                  '独立能量积分、游标换算与屏幕边界'),
 'multimeter': ('circuits', '电压档加载、串联欧姆档与调零', '输入内阻/计数/灵敏度为教学表型', '更换电池后基准欧姆刻度保留身份', '81组独立回路、短接/中点/溢出'),
 'meter-calibration': ('circuits',
                       '表头分流、串联扩程与误差校准',
                       '原表头设计；内阻由源设计反推，trim为教学值',
                       '理想线性表头；标准输入和往返记录分列',
                       '独立节点/串联矩阵与已知扩程算例'),
 'kelvin-bridge': ('circuits', '双臂电桥与连接电阻补偿', '主副比率、低阻和连接阻为教学值', '主副比率匹配/失配与不可达平衡分列', '四节点矩阵、短接极限及失配修正'),
 'electrostatic-field': ('fields',
                         '同心电极Laplace边值与径向场',
                         '原同心几何/电压；探针位置为教学控制',
                         '均匀介质轴对称；边界与方位等势',
                         '1/r积分、通量与二维差分二阶收敛'),
 'magnetic-field': ('fields',
                    '单/双圆线圈轴向Biot–Savart场',
                    '原半径/匝数/间距；原未定单位读数分列',
                    '理想薄线圈轴线上场；中心均匀性局部',
                    '三维电流元叉乘积分、对称与中心二阶导数'),
 'hall-effect': ('fields', '线性霍尔电压与四极性投影', '灵敏度/磁场/偏置为教学参数', '均匀线性样品；同奇偶副项可残留', '独立四分量方程、换向与零场极限'),
 'thin-lens': ('geometrical-optics',
               '近轴薄透镜与Bessel二次成像',
               '原焦距校准情景；物屏比为教学扫描',
               '实虚物像有向距离、D=4f临界',
               'ABCD矩阵、成像求根与双位置极限'),
 'spectrometer': ('geometrical-optics', '双游标圆周方向差测角', '原观测与独立偏心扰动', '角差小于180°；跨零读数与对置游标', '复数圆周角差与扰动抵消'),
 'prism-apex': ('geometrical-optics',
                '双面反射矢量与顶角',
                '原顶角观测；教学面方向/偏心扰动',
                '40°–80°顶角、法线无向、两反射最短夹角',
                '反射矢量点积与圆周测角'),
 'prism-refractive-index': ('geometrical-optics',
                            '两面Snell折射与最小偏向',
                            '原角度观测；相对折射率为教学输入',
                            '均匀非吸收棱镜、可出射域与对称最小值',
                            '独立光线几何、数值极小与有向读角'),
 'grazing-refraction': ('geometrical-optics',
                        '液体至直角棱镜的掠射折射',
                        '原已知棱镜/角度；液体折射率教学情景',
                        '90°第一面掠射、出射介质身份固定',
                        '独立两界面折射和双游标角度反演'),
 'optical-magnification': ('geometrical-optics',
                           '薄透镜测微标定与开普勒望远镜',
                           '焦距/物距/分划及细丝为独立教学值',
                           '近轴无像差；参数变化后重新标定',
                           'ABCD成像求根、角放大矩阵与共享标定'),
 'newton-rings': ('wave-optics', '空气薄膜双光束反射干涉', '原波长/环读数；曲率及间隙教学设置', '近法向、等振幅、近轴膜厚', '独立复场、暗环求根与直径平方回归'),
 'single-slit-diffraction': ('wave-optics',
                             '单缝Fraunhofer孔径积分',
                             '原波长/屏距；缝宽独立教学设置',
                             '标量均匀平面波、声明Fresnel筛选域',
                             '独立孔径积分、暗纹及中心连续极限'),
 'polarization': ('wave-optics',
                  'Jones波片/投影与Fresnel反射',
                  '满幅响应/背景/折射率为教学值',
                  '完全相干偏振；非吸收各向同性单界面',
                  '复矩阵、电磁边界与布儒斯特极限'),
 'transmission-grating': ('wave-optics',
                          '有限多缝复振幅与单缝包络',
                          '原波长/测角；缝数和几何教学场景',
                          '均匀单色、有限缝Fraunhofer场',
                          '逐缝复和、主极大/缺级与角度几何'),
 'optical-rotation': ('wave-optics',
                      '线性旋光与双半视场等亮',
                      '原条件比旋光率/管长；浓度为教学输入',
                      '理想Jones等效双场、选择暗等亮分支',
                      '独立旋转投影、180°周期读角与浓度反演'),
 'michelson-interferometer': ('wave-optics',
                              '两平面波等厚直条纹与往返光程',
                              '原波长/位移；小倾角教学场景',
                              '近轴、等振幅完全相干；固定点周期计数',
                              '独立复场、镜移λ/2极限与数值计数'),
 'abbe-imaging': ('wave-optics',
                  '相干4f复振幅滤波',
                  '原波长/焦距；物体/孔径/网格为教学输入',
                  '周期边界、整数周期物体；Nyquist与强度谐波',
                  'NumPy FFT完整复场、Parseval及网格加倍'),
 'holography': ('wave-optics',
                '离轴相干记录、边带解调与Fresnel再现',
                '原波长/距离尺度；复物场/参考/载频为教学输入',
                '近轴标量、周期边界；边带隔离与采样',
                '独立FFT复场、网格/域加倍及精确角谱比较'),
 'thermal-expansion': ('thermofluids',
                       '工程线膨胀与均温一阶热响应',
                       '原长度/参考系数；τ和读数偏移为教学输入',
                       '均温自由杆、常系数；平衡与有限时间分列',
                       'DOP853热响应、空间应变积分与回归'),
 'liquid-viscosity': ('thermofluids',
                      '浮力重力与Stokes壁面修正',
                      '原球径/管径/密度；黏度与释放位置为教学输入',
                      'Re≤0.1、d/D≤0.1；长筒忽略端部模型',
                      '独立Radau门事件与终速极限'),
 'vaporization-heat': ('thermofluids',
                       '混合量热与湿蒸汽/热损失分项',
                       '原质量/采用比热；液滴/损失为教学情景',
                       '完全混合凝结、同称量构成；预计末温<99℃',
                       'Brent能量平衡求根及表观潜热恒等式'),
 'mechanical-equivalent-heat': ('thermofluids',
                                '集中热容电加热与Newton环境热交换',
                                '原采用J/cal；总热容/环境交换为教学输入',
                                '均温恒热容、恒电功；带符号环境热量',
                                'DOP853温度与换热积分、加热/冷却极限'),
 'thermal-conductivity': ('thermofluids',
                          '一维恒热流热方程与准稳态',
                          '原几何/密度/热电换算；λ/c为教学物性',
                          '中心绝热、外恒热流、常物性',
                          '独立Fourier级数、有限体积能量与网格收敛'),
 'photosensor': ('detectors',
                 'BPW34光电流与跨阻电路',
                 '官方950nm/5V/25℃典型点；反馈和零点教学设置',
                 '声明辐照域、理想运放线性区与输出饱和',
                 '独立KCL工作点、暗零点和功率/响应度换算')}

GUIDE_TEMPLATE = r"""# 虚拟实验的科学依据与复现

这套虚拟实验把装置操作与可核查的物理关系连接起来：改变条件，取得读数，再用方程和独立计算解释结果。每个实验的科学入口包含模型、参数身份、适用范围和验证方法；[机器清单](series-scientific-manifest.json)逐项连接45个实验、46份已核读参考资料及计算记录。

## 如何阅读一个实验

1. 从实验的模型依据文档确认方程、初始条件、边界条件和符号约定，再按页码或公式号查阅引用。
2. 对照参数说明区分原报告观测、原作者采用常数、文献条件值、拟合校准量和独立教学输入。材料参数连同温度、波长、偏压或样品条件一起使用。
3. 在声明的软件域内操作。测量区间平均值、瞬时量、稳态量和有限时间结果各有明确含义；共享标定量与待测读数保持分组。
4. 查看独立参考记录中的算法、容差、实际误差和源文件哈希，然后执行相同验证。

原始报告回答“这次测到了什么”，虚拟模型回答“在这些假设和参数下会发生什么”。观测、自动模型记录与操作读数分别保存，便于检验模型、测量方法与参数敏感性。

## 公共理论地图

| 方向 | 实验数 | 共同理论与重点 | 独立验证方式 |
|---|---:|---|---|
| 力学与测量 | 10 | 守恒、线性响应、本征模态、几何放大、定标 | 约束方程、ODE、质量积分、离散本征值与收敛 |
| 声学与频率测量 | 3 | 波前、移动接收器、复相位与往返叠加 | 轨迹交点、相位导数、独立多路径复和 |
| 电路与仪表 | 9 | Kirchhoff方程、复阻抗、加载、平衡与扩程 | 独立节点矩阵、回路方程和能量积分 |
| 电磁场 | 3 | Laplace边值、Biot–Savart积分、换向奇偶性 | 边界与通量、矢量线积分、四分量反演 |
| 几何光学与测角 | 6 | Snell定律、反射矢量、近轴矩阵、圆周读角 | 向量光线、ABCD矩阵、成像求根与圆周差 |
| 波动光学与计算成像 | 8 | 复振幅叠加、偏振投影、孔径积分与傅里叶传播 | 独立复场、FFT、能量、网格和域收敛 |
| 热学与流体 | 5 | 能量平衡、集中热容、热方程、低Re拖曳 | 独立求根/ODE、Fourier级数与离散能量平衡 |
| 光电器件 | 1 | 有条件器件响应、跨阻读出与工作点 | 独立KCL、零点校正、功率与响应度换算 |

公共理论可以复用，具体装置仍需逐项映射。相同方程下的符号、测量定义和参数条件也可能不同：串联损耗决定RLC相位约定，单程移动接收器关系区别于反射双程，光强始终由实际复振幅取模平方得到。

## 可复用的全文依据

以下资料已在逐实验文献记录中核读和定位。每一处复用的页码、用途与适用边界见机器清单的 `references[].uses`。

| 文献 | 当前复用方向 | 采用位置与边界 |
|---|---|---|
| 宋羽飞等，2023，[多普勒仪器改进](https://doi.org/10.14139/j.cnki.cn22-1228.2023.02.020) | 多普勒验证、弹簧振子多普勒应用 | p91–92单程固定源/移动接收器关系；振子动力学另行推导 |
| 蔡晨等，2016，[电热法热功当量](https://doi.org/10.16854/j.cnki.1000-0712.2016.0080) | 热功当量、线膨胀升温 | p53–54集中热容、Newton换热与指数响应；具体热容和时间常数分别登记 |
| 杨铁柱等，2017，[单臂、双臂电桥](https://doi.org/10.16854/j.cnki.1000-0712.2017.06.010) | 单臂电桥、双臂电桥 | 各自拓扑与平衡关系；连接电阻及主副比率按装置映射 |
| 杨铁柱等，2021，[电表改装与校准](https://doi.org/10.14139/j.cnki.cn22-1228.2021.05.023) | 电表改装；制流、伏安、万用表的基础电路关系 | p99–100串并联及有限输入阻抗；后三项的专项装置依据正在补齐 |
| 徐崇，2009，[掠入射折射率测量](https://doi.org/10.14139/j.cnki.cn22-1228.2009.01.005) | 掠射法、分光计、棱镜顶角读角 | p10–12光路及双游标程序；液体直角棱镜与一般测角用途分别定位 |
| 刘文晶等，2023，[棱镜顶角反射法](https://doi.org/10.14139/j.cnki.cn22-1228.2023.02.017) | 棱镜顶角、分光计 | p78–79反射装置与机械调节；反射方向按独立矢量几何计算 |
| 时俊仙等，2024，[偏振实验拓展](https://doi.org/10.3969/j.issn.1672-4305.2024.04.011) | 偏振、旋光 | 偏振投影与旋光关系；波片、半视场及材料条件在各实验中明确 |

单摆的不确定度文献、BPW34官方器件数据表、光学和材料专项论文分别保存在对应参考清单中。DOI、出版题录、原文定位和文件哈希构成可核查的引用；完整原文按出版机构的获取条件阅读。

## 当前覆盖与补充方向

核查快照：2026年10月17日。39项已有完整的科学接入依据；其余6项正在补齐专项覆盖。部署进度以[仿真登记表](../simulations/registry.json)为准，逐项科学覆盖以机器清单为准。

| 实验 | 已具备依据与验证 | 正在补充的专项内容 |
|---|---|---|
| 制流分压 | 串联关系、原分压接线与270组节点验证 | 三端滑片带负载分压装置 |
| 电阻伏安特性 | 串并联加载、162组节点验证 | 内外接伏安接线及其测量误差 |
| 万用电表 | 电压档加载、欧姆回路推导与81组验证 | 欧姆档调零、电池变化及表型规格 |
| 光学放大与微小长度 | 成像/测微流程、ABCD矩阵及共享标定验证 | 测微分划、望远镜角放大及标定传播全文定位 |
| 阿贝成像 | 相干两阶段、二维FT、孔径操作与复场验证 | 完整4f物理坐标和离散采样 |
| 全息照相 | 离轴记录、边带滤波及独立复场再现 | Fresnel频域传递函数与离散传播适用域 |

来源中的公式和单位问题保存在各实验核查记录中。例如转动惯量论文的连续两圈中点间隔按时间轴独立校正，准稳态导热边界按量纲与能量守恒核对。更正后的关系再经过独立数值检验。

## 复现入口

在项目根目录安装项目Python环境，并准备Node.js，执行单项或全体检查：

```text
python scripts/validate_simulations.py --experiment course-01/pendulum
python scripts/validate_simulations.py --all
```

统一命令依登记表执行JavaScript语法检查、模型测试和独立Python参考计算。验证记录包含实际运行环境、参数、容差、未修约误差及输入/代码哈希；具体方法随物理问题选择。动力学核对守恒或耗散，场与传热核对边界和离散收敛，计算光学同时核对复场、采样与传播近似。

扩展实验时，沿“方程与条件 → 参数身份 → 独立参考 → 操作读数 → 前端检查”的顺序维护。改变共享算法、输入、参数域或模型定义后，重跑受影响实验，并用新哈希关联文献证据、数值记录和页面验收。
"""

READ = {'full_text_reviewed', 'verified-fulltext', 'obtained_and_read',
        'obtained_and_read_from_rendered_pages', 'fulltext_read'}
LEGACY = {'pendulum', 'rlc-resonance', 'newton-rings', 'string-vibration'}
GROUPS = {'mechanics':'力学与测量','acoustics':'声学与频率测量','circuits':'电路与仪表',
          'fields':'电磁场','geometrical-optics':'几何光学与测角','wave-optics':'波动光学与计算成像',
          'thermofluids':'热学与流体','detectors':'光电器件'}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def inside(root, relative):
    path = (root / relative).resolve()
    if Path(relative).is_absolute() or not path.is_relative_to(root.resolve()):
        raise ValueError('Resource must be relative to repository: '+str(relative))
    return path

def normalize_hashes(root, folder, values):
    result = {}
    for name, value in (values or {}).items():
        path = inside(root, name) if '/' in name or '\\' in name else folder / name
        if not path.resolve().is_relative_to(root.resolve()):
            raise ValueError('Hash resource outside repository')
        result[path.relative_to(root).as_posix()] = value
    return result

def valid_sha(value):
    return isinstance(value,str) and bool(re.fullmatch('[0-9a-f]{64}',value))

def reference_fields(ref):
    status = ref.get('readingStatus',ref.get('full_text_status',ref.get('review_status')))
    sha = ref.get('fulltextSha256',ref.get('pdf_sha256',ref.get('source_pdf',{}).get('sha256')))
    locators = ref.get('locators',[])
    valid = status in READ and valid_sha(sha) and bool(locators) and all(bool(x) for x in locators)
    return status,sha,locators,valid

def local_literature(manifests):
    """Return file verification outcomes without exposing local archive paths."""
    result = {}
    for filename in manifests:
        document = read(filename)
        for item in document.get('papers',document.get('references',[])):
            sha = item.get('sha256',item.get('pdf_sha256'))
            if not valid_sha(sha):
                continue
            name = item.get('local_file')
            if not name:
                result[sha] = {'status':'not_available'}
                continue
            path = Path(name) if Path(name).is_absolute() else filename.parent / name
            status = item.get('reading_status',item.get('full_text_status'))
            if status not in READ:
                outcome = {'status':'reading_not_confirmed'}
            elif not path.is_file():
                outcome = {'status':'not_available'}
            else:
                actual = digest(path)
                outcome = {'status':'matched' if actual == sha else 'mismatch','actual_sha256':actual}
            if result.get(sha,{}).get('status') != 'matched':
                result[sha] = outcome
    return result

def collect(root, manifests=()):
    root = root.resolve()
    registry_path = inside(root,'simulations/registry.json')
    registry = read(registry_path)
    entries = registry['simulations']
    if len(entries) != registry.get('experiment_count',len(entries)):
        raise ValueError('Registry experiment count does not match entries')
    if len({e['experiment_id'] for e in entries}) != len(entries) or len({e['slug'] for e in entries}) != len(entries):
        raise ValueError('Duplicate registry experiment identity')
    local = local_literature(manifests)
    papers, experiments = {}, []
    for entry in entries:
        slug, resources = entry['slug'],entry['resources']
        folder = inside(root,resources['simulation_model']).parent
        issues, hashes = [], {}
        for name in resources.values():
            path = inside(root,name)
            if path.is_file(): hashes[name] = digest(path)
            else: issues.append('missing_resource:'+name)
        ev_path = inside(root,resources['model_evidence'])
        ref_path = inside(root,resources['references_json'])
        ev = ev_path.read_text(encoding='utf-8') if ev_path.is_file() else ''
        doc = read(ref_path) if ref_path.is_file() else {}
        identity = doc.get('experiment_id',doc.get('experimentId',doc.get('experiment')))
        if identity and identity not in {entry['experiment_id'],slug}: issues.append('reference_identity_mismatch')
        refs = doc.get('references',[])
        if not refs or len({r.get('id') for r in refs}) != len(refs): issues.append('missing_or_duplicate_references')
        ids = []
        for ref in refs:
            status,pdf_sha,locators,valid = reference_fields(ref)
            if not valid: issues.append('reference_reading_record_incomplete:'+str(ref.get('id')))
            key = 'doi:'+ref['doi'].lower() if ref.get('doi') else 'sha256:'+pdf_sha if pdf_sha else 'title:'+ref['title']
            verification = local.get(pdf_sha,{'status':'not_available'}) if manifests else {'status':'not_requested'}
            if verification['status'] == 'mismatch': issues.append('local_pdf_hash_mismatch:'+ref['id'])
            if key not in papers:
                paper = {k:ref[k] for k in ['title','authors','journal','year','volume','issue','pages','doi','document_number','revision','revision_date'] if k in ref}
                url = 'https://doi.org/'+ref['doi'] if ref.get('doi') else ref.get('url')
                if url and (not url.startswith('https://') or any(s in url.lower() for s in ['webvpn','vpn.','localhost','127.0.0.1'])): url = None
                paper.update(identity=key,url=url,pdf_sha256=pdf_sha,reading_status=status,uses=[],used_by=[],reference_ids=[],local_pdf_verification=verification)
                papers[key] = paper
            paper = papers[key]
            if ref['id'] not in paper['reference_ids']: paper['reference_ids'].append(ref['id'])
            paper['used_by'].append(entry['experiment_id'])
            paper['uses'].append({'experiment_id':entry['experiment_id'],'reference_id':ref['id'],
                'reading_status':status,'pdf_sha256':pdf_sha,'reading_record_verified':valid,'locators':locators,
                'application':ref.get('application',ref.get('uses',[])),'scope':ref.get('scope')})
            ids.append(key)
        vr_path = inside(root,resources['simulation_validation'])
        vr = read(vr_path) if vr_path.is_file() else {}
        vr_status = vr.get('status',vr.get('browser_verification',{}).get('status'))
        model_sha = vr.get('model_sha256',vr.get('modelSha256',vr.get('browser_verification',{}).get('model_sha256')))
        if vr_status != 'passed' or model_sha != hashes.get(resources['simulation_model']): issues.append('independent_reference_stale_or_missing')
        frontend_name = entry.get('frontend_validation')
        frontend = read(inside(root,frontend_name)) if frontend_name and inside(root,frontend_name).is_file() else {}
        if frontend_name and not frontend: issues.append('frontend_record_missing')
        if frontend and frontend.get('status') != 'passed': issues.append('frontend_record_not_passed')
        fh = normalize_hashes(root,folder,frontend.get('source_hashes',frontend.get('source_files',frontend.get('source_sha256',{}))))
        for name,expected in fh.items():
            path = inside(root,name)
            if not path.is_file() or digest(path) != expected: issues.append('frontend_source_changed:'+name)
        scientific = frontend.get('scientific_evidence',{})
        if slug not in LEGACY:
            bindings = normalize_hashes(root,root,scientific.get('decision_source_files',{}))
            required = {resources[k] for k in ['model_evidence','references_json','simulation_model']}
            if scientific.get('status') != 'verified' or not required <= bindings.keys():
                issues.append('scientific_decision_missing')
            for name,expected in bindings.items():
                if hashes.get(name,digest(inside(root,name)) if inside(root,name).is_file() else None) != expected: issues.append('scientific_decision_source_changed:'+name)
            required_runtime = {v for k,v in resources.items() if k.startswith('simulation_') and k != 'simulation_validation'}
            if not required_runtime <= fh.keys(): issues.append('frontend_runtime_hash_coverage_incomplete')
            by_id = {r['id']:r for r in refs}
            core = scientific.get('core_references',[])
            if not core: issues.append('core_references_missing')
            for ref in core:
                current = by_id.get(ref.get('id'))
                if not current or reference_fields(current)[1] != ref.get('pdf_sha256'): issues.append('core_reference_binding_changed')
        registered = entry.get('status') in {'validated','published'} and entry.get('evidence_status') == 'verified' and entry.get('frontend_status') == 'passed'
        ready = registered and not issues
        group,model,parameters,scope,validation = THEORY_MAP.get(slug,('other',entry['title'],'见逐实验参数说明','见逐实验范围说明','见独立参考记录'))
        experiments.append({'experiment_id':entry['experiment_id'],'slug':slug,'title':entry['title'],
            'theory_group':group,'readiness':'scientific_ready' if ready else 'review_required',
            'registered_deployment_status':entry['status'],'model_version':entry['model_version'],
            'review_basis':'registered_legacy_verified' if slug in LEGACY else 'public_frontend_scientific_decision',
            'coverage':{'model':model,'parameter_identity':parameters,'scope':scope,'independent_validation':validation},
            'evidence_headings':re.findall(r'^## (.+)$',ev,re.M),'references':ids,'resources':resources,
            'source_hashes':hashes,'frontend_validation':frontend_name,'issues':issues,
            'reproduction':{'node_tests':entry['tests'],'python_validator':entry['validator'],
                'reference_run_status':vr_status,'reference_model_sha256':model_sha}})
    for paper in papers.values():
        paper['fulltext_reading_record_verified'] = all(u['reading_record_verified'] for u in paper['uses'])
    return {'schema_version':2,'generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'experiment_count':len(entries),'scientific_ready_count':sum(e['readiness']=='scientific_ready' for e in experiments),
        'review_required_count':sum(e['readiness']!='scientific_ready' for e in experiments),
        'cited_reference_count':len(papers),'fulltext_read_reference_count':sum(p['fulltext_reading_record_verified'] for p in papers.values()),
        'local_pdf_verification_requested':bool(manifests),'registry_snapshot_sha256':digest(registry_path),
        'readiness_definition':'公开登记状态、核读记录、独立计算及当前公开验收哈希共同核对；本地全文核验另行标识。',
        'theory_groups':[{'id':g,'title':title,'experiment_ids':[e['experiment_id'] for e in experiments if e['theory_group']==g]} for g,title in GROUPS.items()],
        'references':list(papers.values()),'experiments':experiments}

def guide(index):
    text = GUIDE_TEMPLATE
    text = re.sub(r'\d+份已核读参考资料',str(index['fulltext_read_reference_count'])+'份已核读参考资料',text)
    text = text.replace('45个实验',str(index['experiment_count'])+'个实验')
    start,end = text.index('核查快照：'),text.index('\n来源中的公式')
    date = index['generated_at_utc'][:10]
    coverage = f'核查快照（UTC）：{date}。{index["scientific_ready_count"]}项的公开科学与前端验收记录已核对。'
    pending = [e for e in index['experiments'] if e['readiness'] != 'scientific_ready']
    if pending:
        coverage += f'其余{len(pending)}项的当前状态及需复核内容见机器清单。'
    coverage += '部署进度以[仿真登记表](../simulations/registry.json)为准。\n'
    coverage += '\n索引记录公开引用中的全文核读状态、定位和PDF哈希。本地文件核验按可选文献归档清单执行，实际状态另行记录；常规克隆检查使用公开证据和源文件哈希。\n'
    text = text[:start]+coverage+text[end:]
    text = text.replace('## 当前覆盖与补充方向','## 科学覆盖')
    text = text.replace('后三项的专项装置依据正在补齐','各实验专项依据在逐项清单中定位')
    return text

def comparable(index):
    """Ignore run-local verification facts while preserving public source bindings."""
    result = json.loads(json.dumps(index))
    result.pop('generated_at_utc',None)
    result.pop('local_pdf_verification_requested',None)
    for reference in result['references']:
        reference.pop('local_pdf_verification',None)
    return result

def comparable_guide(text):
    return re.sub(r'核查快照（UTC）：\d{4}-\d{2}-\d{2}', '核查快照（UTC）：<date>',text.replace('\r\n','\n')).strip()

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output-root',type=Path,help='输出项目根目录；默认与repo-root相同')
    parser.add_argument('--literature-manifest',type=Path,action='append',default=[])
    parser.add_argument('--literature-report',type=Path,help='可选独立本地全文核验记录；不影响公开索引的CI比较')
    parser.add_argument('--require-all-ready',action='store_true')
    parser.add_argument('--check',action='store_true',help='只核对并输出统计，不写文件')
    args = parser.parse_args(argv)
    index = collect(args.repo_root,args.literature_manifest)
    result = {k:index[k] for k in ['experiment_count','scientific_ready_count','review_required_count','cited_reference_count','fulltext_read_reference_count','local_pdf_verification_requested']}
    result['issues'] = {e['slug']:e['issues'] for e in index['experiments'] if e['issues']}
    print(json.dumps(result,ensure_ascii=False))
    if args.require_all_ready and index['review_required_count']: return 1
    folder = (args.output_root or args.repo_root)/'docs'
    if args.check:
        manifest_file = folder/'series-scientific-manifest.json'
        guide_file = folder/'series-scientific-guide.md'
        if not manifest_file.is_file() or not guide_file.is_file():
            print('Scientific index outputs are missing; run generator before --check.')
            return 1
        if comparable(read(manifest_file)) != comparable(index):
            print('Scientific manifest is stale: public resources, references or acceptance bindings changed.')
            return 1
        if comparable_guide(guide_file.read_text(encoding='utf-8')) != comparable_guide(guide(index)):
            print('Scientific guide is stale.')
            return 1
    else:
        folder.mkdir(parents=True,exist_ok=True)
        (folder/'series-scientific-manifest.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (folder/'series-scientific-guide.md').write_text(guide(index),encoding='utf-8')
        if args.literature_report:
            args.literature_report.parent.mkdir(parents=True,exist_ok=True)
            args.literature_report.write_text(json.dumps({'checked_at_utc':index['generated_at_utc'],'references':[{'identity':r['identity'],'pdf_sha256':r['pdf_sha256'],'verification':r['local_pdf_verification']}for r in index['references']]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
