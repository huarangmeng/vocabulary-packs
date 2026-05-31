#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERSION = "2026.06.01"
TAG = f"vocab-{VERSION}"
BOOK_ID = "ielts-academic-core"
FILE_NAME = f"{BOOK_ID}-{VERSION}.vocabpack"
DOWNLOAD_URL = (
    "https://github.com/huarangmeng/vocabulary-packs/releases/download/"
    f"{TAG}/{FILE_NAME}"
)


RAW_ENTRIES = [
    ("analyse", "分析；剖析", "verb", "to examine information carefully in order to understand patterns, causes, or meaning", "Researchers analyse survey responses before drawing conclusions.", "研究人员在得出结论前会分析问卷回答。", ["examine", "study", "evaluate"], ["analysis", "analyst", "analytical"]),
    ("approach", "方法；处理方式", "noun", "a way of dealing with a problem, task, or topic", "A comparative approach can reveal differences between education systems.", "比较性方法可以揭示教育体系之间的差异。", ["method", "strategy", "way"], ["approaches", "approached", "approaching"]),
    ("area", "领域；区域；方面", "noun", "a particular subject, field, or part of a place", "Public health is an area that requires long-term investment.", "公共卫生是一个需要长期投入的领域。", ["field", "sector", "region"], ["areas"]),
    ("assess", "评估；评价", "verb", "to judge the quality, value, size, or importance of something", "The course uses essays to assess students' critical thinking.", "这门课程通过论文评估学生的批判性思维。", ["evaluate", "judge", "appraise"], ["assessment", "assessed", "assessing"]),
    ("assume", "假设；认为", "verb", "to accept something as true without complete proof", "Many models assume that consumers make rational choices.", "许多模型假设消费者会做出理性选择。", ["suppose", "presume", "believe"], ["assumption", "assumed", "assuming"]),
    ("benefit", "好处；使受益", "noun", "an advantage or positive result", "Flexible working hours can benefit both employees and employers.", "弹性工作时间可以让员工和雇主双方受益。", ["advantage", "gain", "value"], ["benefits", "beneficial"]),
    ("concept", "概念；观念", "noun", "an abstract idea or general principle", "The concept of sustainability is central to modern urban planning.", "可持续性的概念是现代城市规划的核心。", ["idea", "principle", "notion"], ["concepts", "conceptual"]),
    ("consistent", "一致的；稳定的", "adjective", "not changing and following the same pattern or standard", "Consistent practice is more effective than occasional intensive study.", "稳定练习比偶尔高强度学习更有效。", ["steady", "regular", "uniform"], ["consistency", "consistently"]),
    ("constitute", "构成；组成", "verb", "to form or be considered as part of a whole", "Transport emissions constitute a major share of urban pollution.", "交通排放构成了城市污染的重要部分。", ["form", "make up", "compose"], ["constitution", "constituent"]),
    ("context", "背景；语境", "noun", "the situation or conditions in which something exists or happens", "Words are easier to remember when they are learned in context.", "词汇在语境中学习时更容易记住。", ["background", "setting", "situation"], ["contexts", "contextual"]),
    ("contract", "合同；契约", "noun", "a formal agreement between people or organizations", "A clear contract can reduce disputes between companies.", "清晰的合同可以减少公司之间的纠纷。", ["agreement", "deal", "arrangement"], ["contracts", "contractual"]),
    ("create", "创造；建立", "verb", "to make something new or bring something into existence", "Technology can create opportunities for remote education.", "技术可以为远程教育创造机会。", ["produce", "generate", "build"], ["creation", "creative", "created"]),
    ("data", "数据；资料", "noun", "facts or information used for analysis or decision-making", "Reliable data is essential for evidence-based policy.", "可靠数据对于循证政策至关重要。", ["information", "figures", "evidence"], ["dataset", "database"]),
    ("define", "定义；界定", "verb", "to explain the meaning or limits of something", "The essay should clearly define its key terms.", "论文应清楚界定关键术语。", ["explain", "describe", "specify"], ["definition", "defined", "defining"]),
    ("derive", "获得；源自", "verb", "to get something from a particular source", "Many economic theories derive from observations of market behaviour.", "许多经济理论源自对市场行为的观察。", ["obtain", "come from", "originate"], ["derived", "derivation"]),
    ("distribute", "分配；分发", "verb", "to share or spread something among people or places", "Governments must distribute resources fairly during a crisis.", "政府在危机期间必须公平分配资源。", ["allocate", "share", "spread"], ["distribution", "distributed"]),
    ("economy", "经济；经济体", "noun", "the system of production, trade, and money in a country or region", "A strong economy depends on education, infrastructure, and innovation.", "强劲经济依赖教育、基础设施和创新。", ["market", "financial system"], ["economic", "economist"]),
    ("environment", "环境；周围条件", "noun", "the natural world or the conditions in which people live and work", "Urban design can improve the local environment.", "城市设计可以改善当地环境。", ["surroundings", "conditions", "ecosystem"], ["environmental", "environmentally"]),
    ("establish", "建立；确立", "verb", "to create, prove, or make something accepted", "The study establishes a link between sleep and memory.", "该研究确立了睡眠与记忆之间的联系。", ["set up", "prove", "found"], ["established", "establishment"]),
    ("estimate", "估计；估算", "verb", "to calculate an amount or value approximately", "Experts estimate that demand will increase over the next decade.", "专家估计未来十年需求将会增加。", ["calculate", "approximate", "project"], ["estimation", "estimated"]),
    ("evident", "明显的；显而易见的", "adjective", "easy to see, notice, or understand", "The benefits of early language exposure are evident in many studies.", "许多研究都明显显示早期语言接触的好处。", ["clear", "obvious", "apparent"], ["evidence", "evidently"]),
    ("factor", "因素；要素", "noun", "one of the things that affects a result or situation", "Income is only one factor influencing access to education.", "收入只是影响教育机会的因素之一。", ["element", "cause", "influence"], ["factors"]),
    ("finance", "金融；资金", "noun", "money management or money available for a project", "Public finance affects the quality of healthcare services.", "公共财政会影响医疗服务质量。", ["funding", "money", "capital"], ["financial", "financing"]),
    ("formula", "公式；方案", "noun", "a fixed method, rule, or mathematical expression", "There is no simple formula for solving urban congestion.", "解决城市拥堵没有简单公式。", ["method", "rule", "equation"], ["formulas", "formulae"]),
    ("function", "功能；作用", "noun", "the purpose or role of a person, thing, or system", "Libraries still perform an important social function.", "图书馆仍然发挥着重要的社会功能。", ["role", "purpose", "use"], ["functional", "functioning"]),
    ("identify", "识别；确定", "verb", "to recognize or find out what something is", "The report identifies several causes of student stress.", "报告确定了学生压力的几个原因。", ["recognize", "detect", "determine"], ["identity", "identification"]),
    ("income", "收入", "noun", "money that a person or organization receives regularly", "Household income often affects children's educational opportunities.", "家庭收入通常影响儿童的教育机会。", ["earnings", "salary", "revenue"], ["incomes"]),
    ("indicate", "表明；显示", "verb", "to show that something exists or is likely to be true", "Recent figures indicate a decline in public transport use.", "最新数据显示公共交通使用率下降。", ["show", "suggest", "signal"], ["indication", "indicator"]),
    ("individual", "个人；个体", "noun", "a single person considered separately from a group", "Digital learning allows each individual to progress at a suitable pace.", "数字学习允许每个个体按合适节奏进步。", ["person", "member", "citizen"], ["individuals", "individually"]),
    ("interpret", "解释；理解", "verb", "to explain the meaning of information, words, or events", "Students should interpret charts rather than simply describe them.", "学生应解释图表，而不是只描述图表。", ["explain", "understand", "read"], ["interpretation", "interpreted"]),
    ("involve", "涉及；包含", "verb", "to include something as a necessary part", "Effective planning involves cooperation between different departments.", "有效规划涉及不同部门之间的合作。", ["include", "require", "entail"], ["involved", "involvement"]),
    ("issue", "问题；议题", "noun", "an important topic or problem for discussion", "Water scarcity is a serious issue in many regions.", "水资源短缺是许多地区的严重问题。", ["problem", "topic", "matter"], ["issues"]),
    ("labour", "劳动；劳动力", "noun", "work or the workers available in an economy", "Automation can change the demand for skilled labour.", "自动化会改变对熟练劳动力的需求。", ["work", "workforce", "employment"], ["labor", "labourer"]),
    ("legal", "法律的；合法的", "adjective", "connected with the law or allowed by law", "Legal protection is necessary for consumer rights.", "消费者权益需要法律保护。", ["lawful", "judicial", "legitimate"], ["legally", "legislation"]),
    ("major", "主要的；重大的", "adjective", "very important, large, or serious", "Climate change is a major challenge for coastal cities.", "气候变化是沿海城市面临的重大挑战。", ["important", "significant", "large"], ["majority"]),
    ("method", "方法；方式", "noun", "a planned way of doing something", "The research method should match the question being studied.", "研究方法应与所研究的问题相匹配。", ["approach", "technique", "procedure"], ["methods", "methodology"]),
    ("occur", "发生；出现", "verb", "to happen or exist in a particular situation", "Errors often occur when data is collected too quickly.", "数据收集过快时经常会出现错误。", ["happen", "arise", "take place"], ["occurrence", "occurred"]),
    ("percent", "百分之", "noun", "one part in every hundred", "The number of international students rose by ten percent.", "国际学生人数增长了百分之十。", ["percentage", "proportion"], ["percentage"]),
    ("period", "时期；阶段", "noun", "a length of time", "The Industrial Revolution was a period of rapid technological change.", "工业革命是技术快速变革的时期。", ["era", "stage", "time"], ["periods", "periodic"]),
    ("policy", "政策；方针", "noun", "a plan or principle used by a government or organization", "Housing policy can influence the structure of a city.", "住房政策会影响城市结构。", ["strategy", "plan", "rule"], ["policies"]),
    ("principle", "原则；原理", "noun", "a basic rule or belief that guides action", "The principle of fairness should guide public decision-making.", "公平原则应指导公共决策。", ["rule", "standard", "belief"], ["principles", "principal"]),
    ("process", "过程；流程", "noun", "a series of actions or changes that lead to a result", "Language learning is a gradual process.", "语言学习是一个渐进过程。", ["procedure", "sequence", "development"], ["processes", "processing"]),
    ("require", "需要；要求", "verb", "to need something or make something necessary", "High-quality research requires accurate data.", "高质量研究需要准确数据。", ["need", "demand", "necessitate"], ["requirement", "required"]),
    ("research", "研究；调查", "noun", "careful study intended to discover new information", "Medical research has improved life expectancy.", "医学研究提高了预期寿命。", ["study", "investigation", "inquiry"], ["researcher", "researched"]),
    ("respond", "回应；反应", "verb", "to say or do something as a reaction", "Cities must respond quickly to changes in population.", "城市必须快速应对人口变化。", ["reply", "react", "answer"], ["response", "responsive"]),
    ("role", "角色；作用", "noun", "the function or position someone or something has", "Parents play an important role in early education.", "父母在早期教育中发挥重要作用。", ["function", "part", "position"], ["roles"]),
    ("sector", "部门；行业；领域", "noun", "a part of an economy, society, or activity", "The tourism sector creates many seasonal jobs.", "旅游行业创造了许多季节性工作。", ["industry", "field", "area"], ["sectors"]),
    ("significant", "显著的；重要的", "adjective", "large or important enough to be noticed", "There was a significant improvement in test performance.", "考试表现有显著提升。", ["important", "notable", "substantial"], ["significance", "significantly"]),
    ("similar", "相似的", "adjective", "almost the same but not exactly the same", "Similar problems can be found in many developing cities.", "许多发展中城市都存在相似问题。", ["alike", "comparable", "related"], ["similarity", "similarly"]),
    ("source", "来源；源头", "noun", "the place, person, or thing that something comes from", "Renewable energy can reduce dependence on fossil fuel sources.", "可再生能源可以减少对化石燃料来源的依赖。", ["origin", "basis", "root"], ["sources"]),
    ("specific", "具体的；特定的", "adjective", "clearly defined or relating to one particular thing", "The task requires specific examples rather than general opinions.", "这个任务需要具体例子，而不是泛泛的观点。", ["particular", "precise", "defined"], ["specifically", "specification"]),
    ("structure", "结构；体系", "noun", "the way parts are arranged to form a whole", "A clear essay structure helps readers follow the argument.", "清晰的文章结构有助于读者理解论证。", ["organization", "framework", "arrangement"], ["structural", "structured"]),
    ("theory", "理论", "noun", "an explanation based on ideas or evidence", "The theory explains why people migrate to large cities.", "该理论解释了人们为何迁往大城市。", ["explanation", "model", "hypothesis"], ["theories", "theoretical"]),
    ("vary", "变化；不同", "verb", "to be different or to change according to the situation", "Learning outcomes vary according to teaching quality.", "学习成果会因教学质量而异。", ["differ", "change", "fluctuate"], ["variation", "varied", "various"]),
]


SUPPLEMENTAL_TERMS_TEXT = """
academic|学术的；学院的|adjective
accurate|准确的；精确的|adjective
achieve|实现；达到|verb
acquire|获得；习得|verb
adapt|适应；改编|verb
adequate|足够的；合格的|adjective
adjust|调整；适应|verb
affect|影响|verb
allocate|分配；拨出|verb
alternative|替代方案；可替代的|noun
ambiguous|模糊的；有歧义的|adjective
annual|年度的；每年的|adjective
apparent|明显的；表面上的|adjective
application|应用；申请|noun
approximate|近似的；估算|adjective
aspect|方面；层面|noun
attitude|态度；看法|noun
authority|权威；当局|noun
availability|可获得性；可用性|noun
aware|意识到的|adjective
capacity|能力；容量|noun
category|类别；范畴|noun
challenge|挑战；质疑|noun
circumstance|情况；环境|noun
cite|引用；引证|verb
civil|公民的；民事的|adjective
clarify|澄清；阐明|verb
classical|经典的；传统的|adjective
code|代码；规范|noun
coherent|连贯的；一致的|adjective
coincide|同时发生；一致|verb
collaborate|合作；协作|verb
commission|委员会；委托|noun
communicate|交流；传达|verb
community|社区；群体|noun
compensate|补偿；弥补|verb
complex|复杂的|adjective
component|组成部分；部件|noun
compound|复合物；复合的|noun
comprehensive|全面的；综合的|adjective
compute|计算|verb
concentrate|集中；专注|verb
conclude|总结；得出结论|verb
conduct|实施；进行|verb
consequence|后果；结果|noun
considerable|相当大的；重要的|adjective
constant|持续的；常量|adjective
constrain|限制；约束|verb
construct|建构；构造|verb
consult|咨询；查阅|verb
consume|消费；消耗|verb
contemporary|当代的；同时期的|adjective
contribute|贡献；促成|verb
conventional|传统的；常规的|adjective
coordinate|协调；坐标|verb
core|核心；核心的|noun
corporate|公司的；企业的|adjective
correspond|对应；通信|verb
criteria|标准；准则|noun
crucial|关键的；至关重要的|adjective
culture|文化|noun
cycle|周期；循环|noun
debate|辩论；争论|noun
decade|十年|noun
decline|下降；衰退|verb
deduce|推断；演绎|verb
demonstrate|证明；展示|verb
deny|否认；拒绝|verb
design|设计；方案|noun
despite|尽管|preposition
detect|发现；检测|verb
device|设备；装置|noun
dimension|维度；方面|noun
diminish|减少；削弱|verb
distinct|不同的；明显的|adjective
diverse|多样的|adjective
document|文件；记录|noun
domestic|国内的；家庭的|adjective
dominate|支配；占主导|verb
draft|草稿；起草|noun
dynamic|动态的；有活力的|adjective
efficient|高效的|adjective
eliminate|消除；淘汰|verb
emerge|出现；显现|verb
empirical|经验的；实证的|adjective
enable|使能够；促成|verb
encounter|遇到；遭遇|verb
energy|能源；能量|noun
enforce|执行；强制实施|verb
enhance|提升；增强|verb
enormous|巨大的|adjective
ensure|确保|verb
entity|实体；存在物|noun
equivalent|等同物；等价的|noun
error|错误；误差|noun
ethnic|民族的；族群的|adjective
evaluate|评价；评估|verb
eventual|最终的|adjective
exclude|排除；不包括|verb
expand|扩大；扩展|verb
expert|专家；专业的|noun
explicit|明确的；清楚的|adjective
export|出口；输出|verb
expose|暴露；揭示|verb
external|外部的|adjective
facilitate|促进；使便利|verb
feature|特征；特点|noun
final|最终的|adjective
focus|焦点；集中|noun
formal|正式的；形式上的|adjective
framework|框架；体系|noun
fund|资金；资助|noun
gender|性别；社会性别|noun
generate|产生；生成|verb
global|全球的|adjective
goal|目标|noun
grade|等级；分数|noun
grant|拨款；授予|noun
guarantee|保证；担保|verb
guideline|指导方针|noun
hypothesis|假设；假说|noun
illustrate|说明；举例说明|verb
impact|影响；冲击|noun
implement|实施；执行|verb
imply|暗示；意味着|verb
impose|强加；征收|verb
incentive|激励；动机|noun
initial|最初的；初始的|adjective
innovate|创新|verb
input|投入；输入|noun
insight|洞察；见解|noun
inspect|检查；审查|verb
instance|例子；实例|noun
institute|机构；建立|noun
instruction|指导；说明|noun
integrate|整合；融入|verb
intelligence|智力；情报|noun
interact|互动；相互作用|verb
internal|内部的|adjective
invest|投资；投入|verb
investigate|调查；研究|verb
isolate|隔离；分离|verb
journal|期刊；日志|noun
justify|证明合理；为……辩护|verb
label|标签；标记|noun
layer|层；层次|noun
lecture|讲座；授课|noun
liberal|自由的；开放的|adjective
license|许可；许可证|noun
link|联系；连接|noun
locate|定位；位于|verb
maintain|维持；维护|verb
manual|手册；手动的|noun
margin|边缘；差额|noun
mature|成熟的|adjective
mechanism|机制；机械装置|noun
media|媒体|noun
medical|医学的；医疗的|adjective
mental|心理的；精神的|adjective
migrate|迁移；移居|verb
minimum|最小值；最低的|noun
monitor|监测；监督|verb
mutual|相互的；共同的|adjective
network|网络；人脉|noun
neutral|中立的|adjective
normal|正常的；常规的|adjective
objective|目标；客观的|noun
obtain|获得；取得|verb
obvious|明显的|adjective
occupy|占据；占用|verb
option|选择；选项|noun
outcome|结果；成果|noun
output|产出；输出|noun
overall|总体的；整体的|adjective
participate|参与|verb
partner|伙伴；合作方|noun
perceive|感知；认为|verb
perspective|视角；观点|noun
phase|阶段；时期|noun
physical|身体的；物理的|adjective
pose|提出；造成|verb
positive|积极的；正面的|adjective
potential|潜力；潜在的|noun
previous|之前的|adjective
primary|主要的；初级的|adjective
prior|先前的；优先的|adjective
professional|专业的；职业的|adjective
project|项目；课题|noun
promote|促进；推广|verb
proportion|比例；部分|noun
prospect|前景；可能性|noun
publish|出版；发表|verb
purchase|购买；采购|verb
pursue|追求；从事|verb
qualitative|定性的|adjective
quote|引用；报价|verb
radical|激进的；根本的|adjective
random|随机的|adjective
range|范围；区间|noun
ratio|比率；比例|noun
rational|理性的；合理的|adjective
recover|恢复；收回|verb
region|地区；区域|noun
regulate|监管；调节|verb
relevant|相关的|adjective
remove|移除；去除|verb
rely|依赖；依靠|verb
reside|居住；存在于|verb
resolve|解决；决定|verb
resource|资源|noun
restrict|限制；约束|verb
retain|保留；保持|verb
revenue|收入；收益|noun
reverse|逆转；相反的|verb
scheme|方案；计划|noun
scope|范围；领域|noun
secure|安全的；获得|adjective
select|选择；挑选|verb
sequence|顺序；序列|noun
shift|转变；轮班|noun
site|地点；场所|noun
stable|稳定的|adjective
statistic|统计数据|noun
status|状态；地位|noun
stress|压力；强调|noun
style|风格；方式|noun
submit|提交；呈递|verb
subsequent|随后的；后来的|adjective
subsidy|补贴；补助|noun
substitute|替代品；替代|noun
sufficient|足够的|adjective
summary|摘要；总结|noun
survive|生存；幸存|verb
suspend|暂停；悬挂|verb
sustain|维持；支撑|verb
symbol|符号；象征|noun
target|目标；对象|noun
task|任务|noun
technical|技术的；专业的|adjective
technique|技巧；技术|noun
technology|技术；科技|noun
temporary|临时的；暂时的|adjective
tense|紧张的；时态|adjective
terminate|终止；结束|verb
theme|主题|noun
tradition|传统|noun
transfer|转移；转让|verb
transform|转变；改造|verb
transport|交通；运输|noun
trend|趋势|noun
trigger|触发；引发|verb
ultimate|最终的；根本的|adjective
undergo|经历；经受|verb
uniform|统一的；制服|adjective
unique|独特的|adjective
valid|有效的；合理的|adjective
vehicle|车辆；媒介|noun
version|版本；说法|noun
welfare|福利；福祉|noun
whereas|然而；鉴于|conjunction
widespread|广泛的；普遍的|adjective
academic writing|学术写作|phrase
critical thinking|批判性思维|phrase
climate change|气候变化|phrase
economic growth|经济增长|phrase
public transport|公共交通|phrase
renewable energy|可再生能源|phrase
higher education|高等教育|phrase
urban planning|城市规划|phrase
population growth|人口增长|phrase
social media|社交媒体|phrase
government policy|政府政策|phrase
environmental protection|环境保护|phrase
technological innovation|技术创新|phrase
global economy|全球经济|phrase
income inequality|收入不平等|phrase
healthcare system|医疗体系|phrase
consumer behaviour|消费者行为|phrase
living standards|生活水平|phrase
natural resources|自然资源|phrase
labour market|劳动力市场|phrase
energy consumption|能源消耗|phrase
academic performance|学业表现|phrase
cultural diversity|文化多样性|phrase
public awareness|公众意识|phrase
scientific research|科学研究|phrase
policy makers|政策制定者|phrase
long-term impact|长期影响|phrase
short-term solution|短期解决方案|phrase
data analysis|数据分析|phrase
research method|研究方法|phrase
evidence-based policy|循证政策|phrase
social responsibility|社会责任|phrase
economic development|经济发展|phrase
human activity|人类活动|phrase
education system|教育体系|phrase
work-life balance|工作与生活平衡|phrase
traffic congestion|交通拥堵|phrase
air pollution|空气污染|phrase
water scarcity|水资源短缺|phrase
digital technology|数字技术|phrase
traditional culture|传统文化|phrase
social interaction|社会互动|phrase
quality of life|生活质量|phrase
public services|公共服务|phrase
urban population|城市人口|phrase
local community|本地社区|phrase
international trade|国际贸易|phrase
environmental issue|环境问题|phrase
learning outcome|学习成果|phrase
personal development|个人发展|phrase
"""


def slugify(text: str) -> str:
    return "-".join(part for part in re.sub(r"[^a-z0-9]+", "-", text.lower()).split("-") if part)


def parse_supplemental_terms() -> list[tuple[str, str, str]]:
    terms = []
    for line in SUPPLEMENTAL_TERMS_TEXT.strip().splitlines():
        english, chinese, part_of_speech = line.split("|")
        terms.append((english.strip(), chinese.strip(), part_of_speech.strip()))
    return terms


def build_definition(english: str, part_of_speech: str) -> str:
    if part_of_speech == "verb":
        return f"to express an academic action or process related to {english.replace('-', ' ')}"
    if part_of_speech == "adjective":
        return f"describing a quality or condition often discussed in academic contexts"
    if part_of_speech == "phrase":
        return f"a common IELTS academic expression used to discuss {english.lower()}"
    return f"a common academic term used in IELTS reading, writing, speaking, or listening contexts"


def build_example(english: str, part_of_speech: str) -> str:
    if part_of_speech == "verb":
        return f"Researchers often need to {english} evidence before reaching a conclusion."
    if part_of_speech == "adjective":
        return f"The essay presents a {english} point in a clear academic context."
    if part_of_speech == "phrase":
        return f"The topic of {english} is frequently discussed in IELTS academic tasks."
    return f"The term {english} is useful when explaining an academic issue."


def build_example_zh(english: str, chinese: str, part_of_speech: str) -> str:
    if part_of_speech == "phrase":
        return f"“{english}”这个表达常用于雅思学术类任务中讨论“{chinese}”。"
    return f"“{english}”这个词常用于雅思学术语境中表达“{chinese}”。"


def main() -> None:
    entries = []
    for index, (word, zh, pos, definition, example_en, example_zh, synonyms, family) in enumerate(RAW_ENTRIES, start=1):
        entries.append(
            {
                "id": f"{BOOK_ID}:{word}",
                "order": index,
                "type": "WordOrPhrase",
                "englishText": word,
                "chinesePrompt": zh,
                "partOfSpeech": pos,
                "definitionEn": definition,
                "exampleEn": example_en,
                "exampleZh": example_zh,
                "synonyms": synonyms,
                "wordFamily": family,
                "difficulty": "B2-C1",
                "tags": ["IELTS", "Academic", "Core"],
            }
        )

    existing_ids = {entry["id"] for entry in entries}
    for english, chinese, part_of_speech in parse_supplemental_terms():
        entry_key = slugify(english)
        entry_id = f"{BOOK_ID}:{entry_key}"
        if entry_id in existing_ids:
            continue
        existing_ids.add(entry_id)
        entries.append(
            {
                "id": entry_id,
                "order": len(entries) + 1,
                "type": "WordOrPhrase",
                "englishText": english,
                "chinesePrompt": chinese,
                "partOfSpeech": part_of_speech,
                "definitionEn": build_definition(english, part_of_speech),
                "exampleEn": build_example(english, part_of_speech),
                "exampleZh": build_example_zh(english, chinese, part_of_speech),
                "synonyms": [],
                "wordFamily": [],
                "difficulty": "B2-C1",
                "tags": ["IELTS", "Academic", "Core"],
            }
        )

    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    package_manifest = {
        "schemaVersion": 1,
        "bookId": BOOK_ID,
        "bookVersion": VERSION,
        "title": "雅思学术核心词库",
        "description": "面向 IELTS Academic 阅读、写作和口语场景的核心学术词汇，包含中文提示、英文释义、例句、同义词和词族。",
        "itemCount": len(entries),
        "createdAt": created_at,
        "entryFile": "entries.jsonl",
    }

    output_dir = ROOT / "dist" / "vocabpacks"
    output_dir.mkdir(parents=True, exist_ok=True)
    package_path = output_dir / FILE_NAME
    with zipfile.ZipFile(package_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as package:
        package.writestr("manifest.json", json.dumps(package_manifest, ensure_ascii=False, indent=2) + "\n")
        package.writestr(
            "entries.jsonl",
            "\n".join(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) for entry in entries) + "\n",
        )

    digest = hashlib.sha256(package_path.read_bytes()).hexdigest()
    size_bytes = package_path.stat().st_size

    catalog = {
        "schemaVersion": 1,
        "catalogVersion": VERSION,
        "generatedAt": created_at,
        "minAppVersion": "1.0.0",
        "books": [
            {
                "id": BOOK_ID,
                "title": "雅思学术核心词库",
                "description": "面向 IELTS Academic 阅读、写作和口语场景的核心学术词汇。",
                "version": VERSION,
                "itemCount": len(entries),
                "sizeBytes": size_bytes,
                "sha256": digest,
                "fileName": FILE_NAME,
                "tags": ["IELTS", "Academic", "B2-C1"],
                "urls": [DOWNLOAD_URL],
            }
        ],
    }

    manifest_dir = ROOT / "manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    catalog_text = json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"
    (manifest_dir / "latest.json").write_text(catalog_text, encoding="utf-8")
    (manifest_dir / f"{VERSION}.json").write_text(catalog_text, encoding="utf-8")
    (output_dir / "latest.json").write_text(catalog_text, encoding="utf-8")
    latest_digest = hashlib.sha256((output_dir / "latest.json").read_bytes()).hexdigest()
    (output_dir / "latest.json.sha256").write_text(f"{latest_digest}  latest.json\n", encoding="utf-8")

    print(f"Generated: {package_path}")
    print(f"Entries: {len(entries)}")
    print(f"Size: {size_bytes} bytes")
    print(f"SHA-256: {digest}")


if __name__ == "__main__":
    main()
