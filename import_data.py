"""
导入秋招投递数据到数据库
运行: python import_data.py
"""
from app import app, db, JobApplication, User
from datetime import datetime
import re

# 从表格解析的投递数据
JOBS_DATA = [
    # ===== 央国企 =====
    {"company": "中国人民保险", "position": "人保财险-总公司-科技运营岗-2027届校招", "category": "国企", "source": "官网", "apply_date": "2026-07-30", "status": "简历挂", "link": "https://picc.zhiye.com/personal/deliveryRecord", "notes": ""},
    {"company": "中国人民保险", "position": "人保财险-江苏分公司-软件开发岗-2027届校招", "category": "国企", "source": "官网", "apply_date": "2026-07-30", "status": "简历挂", "link": "https://picc.zhiye.com/personal/deliveryRecord", "notes": ""},
    {"company": "山东发展投资控股", "position": "信息系统运维岗", "category": "国企", "source": "官网", "apply_date": "2026-07-31", "status": "笔试挂", "link": "https://sdfz.zhaopin.com/zk/#/pages/application/index", "notes": ""},
    {"company": "中国电子", "position": "中电金信：技术运维工程师", "category": "国企", "source": "官网", "apply_date": "2026-07-31", "status": "流程中", "link": "https://campus.cec.com.cn/collection", "notes": ""},
    {"company": "中国电子", "position": "南京长江电子信息：智能库房管理员", "category": "国企", "source": "官网", "apply_date": "2026-07-31", "status": "简历挂", "link": "https://campus.cec.com.cn/collection", "notes": ""},
    {"company": "中国电子", "position": "南京中电熊猫晶体：生产主管", "category": "国企", "source": "官网", "apply_date": "2026-07-31", "status": "简历挂", "link": "https://campus.cec.com.cn/collection", "notes": ""},
    {"company": "中国电子", "position": "南京三乐集团：技术管理员", "category": "国企", "source": "官网", "apply_date": "2026-07-31", "status": "流程中", "link": "https://campus.cec.com.cn/collection", "notes": ""},
    {"company": "中国物流", "position": "系统管理员", "category": "国企", "source": "官网", "apply_date": "2026-07-31", "status": "流程中", "link": "https://chinalogisticsgroup.hotjob.cn/", "notes": ""},
    {"company": "中国物流", "position": "信息化专员", "category": "国企", "source": "官网", "apply_date": "2026-07-31", "status": "流程中", "link": "https://chinalogisticsgroup.hotjob.cn/", "notes": ""},
    {"company": "中国物流", "position": "储备人才", "category": "国企", "source": "官网", "apply_date": "2026-07-31", "status": "流程中", "link": "https://chinalogisticsgroup.hotjob.cn/", "notes": ""},
    {"company": "中国融通资源开发集团", "position": "接收员(通用物资)", "category": "国企", "source": "官网", "apply_date": "2026-07-31", "status": "面试放弃", "link": "https://www.erongpin.com/army/#/user", "notes": "笔试过，面试放弃，在北京"},
    {"company": "招商局船舶工业集团", "position": "软件开发工程师", "category": "国企", "source": "官网", "apply_date": "2026-08-11", "status": "流程中", "link": "https://cmi.zhiye.com/personal/deliveryRecord", "notes": ""},
    {"company": "苏州智慧国资", "position": "软件研发岗", "category": "国企", "source": "官网", "apply_date": "2026-08-15", "status": "简历挂", "link": "https://zhaopin.szgzjg.com/jobseeker/resume", "notes": "需要留服认证在8-30之前"},
    {"company": "国机集团", "position": "5个岗位", "category": "国企", "source": "官网", "apply_date": "2026-08-21", "status": "流程中", "link": "https://zhaopin.sinomach.com.cn/", "notes": ""},
    {"company": "浙江交通集团", "position": "Web前端开发工程师", "category": "国企", "source": "官网", "apply_date": "2026-08-12", "status": "流程中", "link": "", "notes": ""},
    {"company": "中国太平", "position": "5个岗位", "category": "国企", "source": "官网", "apply_date": "2026-08-31", "status": "流程中", "link": "https://cntp.zhiye.com/personal/deliveryRecord", "notes": ""},
    {"company": "光大证券", "position": "国际-资讯科技", "category": "国企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "", "notes": ""},
    {"company": "中铁一局", "position": "市政环保公司", "category": "国企", "source": "官网", "apply_date": "2026-09-01", "status": "简历挂", "link": "https://zhr.crec.cn/recruit/", "notes": ""},
    {"company": "航空工业雷华电子技术研究所", "position": "4个岗位", "category": "国企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://xiaoyuan.zhaopin.com/scrd/delivery/record", "notes": ""},
    {"company": "中国电子科技55所", "position": "2个岗位", "category": "国企", "source": "官网", "apply_date": "2026-08-21", "status": "流程中", "link": "https://xiaoyuan.zhaopin.com/scrd/delivery/record", "notes": ""},
    {"company": "中船动力(集团)", "position": "2个岗位", "category": "国企", "source": "官网", "apply_date": "2026-08-21", "status": "流程中", "link": "https://xiaoyuan.zhaopin.com/scrd/delivery/record", "notes": ""},
    {"company": "国电南京自动化", "position": "开发", "category": "国企", "source": "官网", "apply_date": "2026-08-21", "status": "流程中", "link": "https://xiaoyuan.zhaopin.com/scrd/delivery/record", "notes": ""},
    {"company": "东风奕派汽车科技", "position": "3个岗位", "category": "国企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://xiaoyuan.zhaopin.com/scrd/delivery/record", "notes": ""},
    {"company": "招商银行", "position": "2个岗位", "category": "国企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://career.cmbchina.com/center/history", "notes": ""},
    {"company": "航天恒星", "position": "待定", "category": "国企", "source": "官网", "apply_date": "", "status": "流程中", "link": "https://spacestar.zhiye.com/", "notes": "要成绩单"},
    {"company": "紫光同芯", "position": "封测-无锡", "category": "国企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://app.mokahr.com/campus-recruitment/tsinghuaic/39656", "notes": ""},
    {"company": "博时基金", "position": "2个岗位", "category": "国企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://bosera.hotjob.cn/", "notes": ""},
    {"company": "华金证券", "position": "1个岗位", "category": "国企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://wecruit.hotjob.cn/", "notes": ""},
    {"company": "浪潮集团", "position": "2个岗位", "category": "国企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://inspur.hcmcloud.cn/recruit#/my_resume", "notes": "在线测评todo"},
    {"company": "光大证券", "position": "香港", "category": "国企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://ebscn.zhiye.com/personal/deliveryRecord", "notes": ""},
    {"company": "紫金矿业", "position": "信息化类", "category": "国企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://join.zjky.cn/", "notes": ""},
    {"company": "中国电子科技38所", "position": "2个岗位", "category": "国企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://xiaoyuan.zhaopin.com/scrd/delivery/record", "notes": ""},
    {"company": "新华三集团", "position": "售前支持工程师", "category": "国企", "source": "官网", "apply_date": "", "status": "流程中", "link": "https://career.h3c.com/", "notes": ""},
    {"company": "南京中新赛克", "position": "待定", "category": "国企", "source": "官网", "apply_date": "", "status": "流程中", "link": "https://recruit.sinovatio.com/positions", "notes": "10-13截至"},
    {"company": "中汽", "position": "27提前批次", "category": "国企", "source": "官网", "apply_date": "", "status": "流程中", "link": "https://mp.weixin.qq.com/s/6gFAYRnHtyiGKJqZkMSTqA", "notes": ""},
    {"company": "中国建筑第八工程", "position": "待定", "category": "国企", "source": "官网", "apply_date": "", "status": "流程中", "link": "https://job.cscec8b.com.cn/", "notes": "10-28截至"},

    # ===== 外企 =====
    {"company": "特斯拉", "position": "前端软件开发实习生", "category": "外企", "source": "官网", "apply_date": "2026-08-04", "status": "流程中", "link": "https://app.mokahr.com/campus-recruitment/tesla/41460", "notes": ""},
    {"company": "日邮物流", "position": "2个岗位", "category": "外企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://app.mokahr.com/campus-recruitment/yusen/73956", "notes": ""},
    {"company": "塞拉尼斯", "position": "生产工程师-南京", "category": "外企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://xiaoyuan.zhaopin.com/scrd/delivery/record", "notes": ""},
    {"company": "卡特比勒", "position": "研发类-电子/电气/软件、测试方向", "category": "外企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://cat.wd5.myworkdayjobs.com/", "notes": ""},
    {"company": "联想", "position": "前端开发", "category": "外企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://talent.lenovo.com.cn/account/apply", "notes": ""},

    # ===== 私企 =====
    {"company": "经纬横润", "position": "2个岗位", "category": "私企", "source": "官网", "apply_date": "2026-08-21", "status": "流程中", "link": "https://app.mokahr.com/campus-recruitment/jingweihengrun/168294", "notes": ""},
    {"company": "多维联合集团", "position": "2个岗位", "category": "私企", "source": "官网", "apply_date": "2026-08-21", "status": "流程中", "link": "https://app.mokahr.com/campus-recruitment/duowei/142740", "notes": ""},
    {"company": "海四达", "position": "2个岗位", "category": "私企", "source": "官网", "apply_date": "2026-08-21", "status": "流程中", "link": "https://highstar.zhiye.com/personal/deliveryRecord", "notes": ""},
    {"company": "思格新能源", "position": "管培生", "category": "私企", "source": "官网", "apply_date": "2026-08-21", "status": "流程中", "link": "https://jobs.sigenergy.com/campus/position/application", "notes": ""},
    {"company": "小米", "position": "Web前端开发工程师", "category": "私企", "source": "官网", "apply_date": "2026-08-12", "status": "简历挂", "link": "https://xiaomi.jobs.f.mioffice.cn/", "notes": "筛简历挂了"},
    {"company": "阳光电源", "position": "前端开发工程师-AI方向-南京", "category": "私企", "source": "官网", "apply_date": "2026-08-12", "status": "简历挂", "link": "https://app.mokahr.com/campus-recruitment/sungrow/94416", "notes": "筛简历挂了"},
    {"company": "特来电新能源", "position": "前端开发", "category": "私企", "source": "官网", "apply_date": "2026-08-21", "status": "流程中", "link": "https://hr.teld.cn/recruit", "notes": ""},
    {"company": "海信集团", "position": "待定", "category": "私企", "source": "官网", "apply_date": "", "status": "流程中", "link": "", "notes": ""},
    {"company": "泰科电子", "position": "3个岗位", "category": "私企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://q.yingjiesheng.com/pc/personal", "notes": ""},
    {"company": "帝奥微", "position": "软件开发岗-南通", "category": "私企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://neitui.italent.cn/dioo/", "notes": ""},
    {"company": "无锡理奇", "position": "应届生岗", "category": "私企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://richsys1.zhiye.com/personal/deliveryRecord", "notes": ""},
    {"company": "赛斌医药", "position": "AI信息化", "category": "私企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://safeglp.zhiye.com/personal/deliveryRecord", "notes": ""},
    {"company": "华沿机器人", "position": "软件开发岗", "category": "私企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "", "notes": ""},
    {"company": "拉普拉斯", "position": "2个岗位", "category": "私企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "", "notes": ""},
    {"company": "麦田能源", "position": "2个岗位", "category": "私企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://fox-ess.zhiye.com/campus/jobs", "notes": ""},
    {"company": "信捷电气", "position": "2个岗位", "category": "私企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://xinje.zhiye.com/personal/deliveryRecord", "notes": ""},
    {"company": "飞壤科技", "position": "2个岗位", "category": "私企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "", "notes": ""},
    {"company": "帆软", "position": "前端开发", "category": "私企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "", "notes": "服务号"},
    {"company": "海康威视", "position": "前端2个", "category": "私企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://campushr.hikvision.com/myDelivery", "notes": "在线测评todo"},
    {"company": "烽火通信", "position": "2个岗位", "category": "私企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://app.mokahr.com/campus-recruitment/whfhtx/73922", "notes": ""},
    {"company": "恒生科技", "position": "1个岗位", "category": "私企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://campus.hundsun.com/personal/deliveryRecord", "notes": ""},

    # ===== 招聘平台 =====
    # 智联只算单投13个，不算网申16个
    {"company": "国聘网", "position": "11个岗位", "category": "招聘平台", "source": "国聘", "apply_date": "2026-08-01", "status": "流程中", "link": "https://www.guopin.com/", "notes": "挂2个，2个不合适，多益网络初筛通过", "pass_screening": 1},
    {"company": "应届生求职网", "position": "32个岗位", "category": "招聘平台", "source": "应届生", "apply_date": "2026-08-01", "status": "流程中", "link": "https://www.yingjiesheng.com/", "notes": "挂4个，3个已读不回，4个不合适", "pass_screening": 0},
    {"company": "智联招聘", "position": "13个岗位(单投)", "category": "招聘平台", "source": "智联", "apply_date": "2026-08-01", "status": "流程中", "link": "https://www.zhaopin.com/", "notes": "挂1个，2个已读不回，1个感兴趣", "pass_screening": 1},
    {"company": "51Job", "position": "6个岗位", "category": "招聘平台", "source": "51job", "apply_date": "2026-08-01", "status": "流程中", "link": "https://www.51job.com/", "notes": "1个已读不回", "pass_screening": 0},
]


def import_data():
    with app.app_context():
        # 创建默认用户（如果不存在）
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin')
            admin.set_password('123456')
            db.session.add(admin)
            db.session.commit()
            print("创建默认用户: admin / 123456")
            print("请登录后及时修改密码！")

        user_id = admin.id

        count = 0
        for job_data in JOBS_DATA:
            # 检查是否已存在
            existing = JobApplication.query.filter_by(
                user_id=user_id,
                company=job_data['company'],
                position=job_data['position']
            ).first()

            if existing:
                print(f"跳过已存在: {job_data['company']} - {job_data['position']}")
                continue

            job = JobApplication(
                user_id=user_id,
                company=job_data['company'],
                position=job_data['position'],
                category=job_data['category'],
                source=job_data['source'],
                apply_date=datetime.strptime(job_data['apply_date'], '%Y-%m-%d').date() if job_data['apply_date'] else None,
                status=job_data['status'],
                link=job_data.get('link', ''),
                notes=job_data.get('notes', ''),
                pass_screening=job_data.get('pass_screening', 0),
                in_exam=job_data.get('in_exam', 0),
                in_interview=job_data.get('in_interview', 0),
            )
            db.session.add(job)
            count += 1
            print(f"添加: {job_data['company']} - {job_data['position']}")

        db.session.commit()
        print(f"\n成功导入 {count} 条记录！")
        print(f"默认登录账号: admin / 123456")


if __name__ == '__main__':
    import_data()
