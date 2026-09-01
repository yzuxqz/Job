"""
导入秋招投递数据到数据库
运行: python import_data.py
"""
from app import app, db, JobApplication
from datetime import datetime

# 从表格解析的投递数据
JOBS_DATA = [
    # ===== 国企/央企 =====
    {"company": "中国人民保险", "position": "人保财险-总公司-科技类1-科技运营岗-2027届校招", "category": "国企", "source": "官网", "apply_date": "2026-07-30", "status": "简历挂", "link": "https://picc.zhiye.com/personal/deliveryRecord", "notes": ""},
    {"company": "中国人民保险", "position": "人保财险-江苏分公司-科技类1-软件开发岗-2027届校招", "category": "国企", "source": "官网", "apply_date": "2026-07-30", "status": "简历挂", "link": "https://picc.zhiye.com/personal/deliveryRecord", "notes": ""},
    {"company": "山东发展投资控股集团有限公司", "position": "信息系统运维岗", "category": "国企", "source": "官网", "apply_date": "2026-07-31", "status": "笔试挂", "link": "https://sdfz.zhaopin.com/zk/#/pages/application/index", "notes": ""},
    {"company": "中国电子", "position": "中电金信数字科技集团股份有限公司：技术运维工程师", "category": "国企", "source": "官网", "apply_date": "2026-07-31", "status": "流程中", "link": "https://campus.cec.com.cn/collection", "notes": ""},
    {"company": "中国电子", "position": "南京长江电子信息产业集团有限公司：智能库房管理员", "category": "国企", "source": "官网", "apply_date": "2026-07-31", "status": "简历挂", "link": "https://campus.cec.com.cn/collection", "notes": ""},
    {"company": "中国电子", "position": "南京中电熊猫晶体科技有限公司：生产主管", "category": "国企", "source": "官网", "apply_date": "2026-07-31", "status": "简历挂", "link": "https://campus.cec.com.cn/collection", "notes": ""},
    {"company": "中国电子", "position": "南京三乐集团有限公司：技术管理员", "category": "国企", "source": "官网", "apply_date": "2026-07-31", "status": "流程中", "link": "https://campus.cec.com.cn/collection", "notes": ""},
    {"company": "中国物流", "position": "2026秋季校园招聘 系统管理员", "category": "国企", "source": "官网", "apply_date": "2026-07-31", "status": "流程中", "link": "https://chinalogisticsgroup.hotjob.cn/", "notes": ""},
    {"company": "中国物流", "position": "2026秋季校园招聘 信息化专员", "category": "国企", "source": "官网", "apply_date": "2026-07-31", "status": "流程中", "link": "https://chinalogisticsgroup.hotjob.cn/", "notes": ""},
    {"company": "中国物流", "position": "2026秋季校园招聘 储备人才", "category": "国企", "source": "官网", "apply_date": "2026-07-31", "status": "流程中", "link": "https://chinalogisticsgroup.hotjob.cn/", "notes": ""},
    {"company": "中国融通资源开发集团有限公司南京分公司", "position": "接收员(通用物资)", "category": "国企", "source": "官网", "apply_date": "2026-07-31", "status": "面试放弃", "link": "https://www.erongpin.com/army/#/user", "notes": "笔试过，2026-08-16，面试放弃，在北京"},
    {"company": "招商局船舶工业集团有限公司", "position": "软件开发工程师", "category": "国企", "source": "官网", "apply_date": "2026-08-11", "status": "流程中", "link": "https://cmi.zhiye.com/personal/deliveryRecord", "notes": ""},
    {"company": "苏州智慧国资招聘", "position": "软件研发岗", "category": "国企", "source": "官网", "apply_date": "2026-08-15", "status": "简历挂", "link": "https://zhaopin.szgzjg.com/jobseeker/resume", "notes": "需要留服认证在8-30之前"},
    {"company": "国机集团", "position": "5个岗位", "category": "国企", "source": "官网", "apply_date": "2026-08-21", "status": "流程中", "link": "https://zhaopin.sinomach.com.cn/", "notes": ""},
    {"company": "浙江交通集团", "position": "Web前端开发工程师", "category": "国企", "source": "官网", "apply_date": "2026-08-12", "status": "流程中", "link": "", "notes": ""},
    {"company": "中国太平", "position": "5个岗位", "category": "国企", "source": "官网", "apply_date": "2026-08-31", "status": "流程中", "link": "https://cntp.zhiye.com/personal/deliveryRecord", "notes": ""},
    {"company": "光大证券", "position": "国际-资讯科技", "category": "国企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "", "notes": ""},
    {"company": "中铁一局", "position": "市政环保公司", "category": "国企", "source": "官网", "apply_date": "2026-09-01", "status": "简历挂", "link": "https://zhr.crec.cn/recruit/", "notes": ""},
    {"company": "中国航空工业集团公司雷华电子技术研究所", "position": "4个岗位", "category": "国企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://xiaoyuan.zhaopin.com/scrd/delivery/record", "notes": ""},
    {"company": "中国电子科技集团公司第五十五研究所", "position": "2个岗位", "category": "国企", "source": "官网", "apply_date": "2026-08-21", "status": "流程中", "link": "https://xiaoyuan.zhaopin.com/scrd/delivery/record", "notes": ""},
    {"company": "中船动力(集团)有限公司", "position": "2个岗位", "category": "国企", "source": "官网", "apply_date": "2026-08-21", "status": "流程中", "link": "https://xiaoyuan.zhaopin.com/scrd/delivery/record", "notes": ""},
    {"company": "国电南京自动化股份有限公司", "position": "开发", "category": "国企", "source": "官网", "apply_date": "2026-08-21", "status": "流程中", "link": "https://xiaoyuan.zhaopin.com/scrd/delivery/record", "notes": ""},
    {"company": "东风奕派汽车科技公司", "position": "3个岗位", "category": "国企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://xiaoyuan.zhaopin.com/scrd/delivery/record", "notes": ""},
    {"company": "招商银行", "position": "2个岗位", "category": "国企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://career.cmbchina.com/center/history", "notes": ""},
    {"company": "航天恒星", "position": "待定", "category": "国企", "source": "官网", "apply_date": "", "status": "流程中", "link": "https://spacestar.zhiye.com/", "notes": "要成绩单"},
    {"company": "紫光同芯", "position": "封测-无锡", "category": "国企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://app.mokahr.com/campus-recruitment/tsinghuaic/39656", "notes": ""},
    {"company": "博时基金", "position": "2个岗位", "category": "国企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://bosera.hotjob.cn/", "notes": ""},
    {"company": "华金证券", "position": "1个岗位", "category": "国企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://wecruit.hotjob.cn/", "notes": ""},
    {"company": "浪潮集团", "position": "2个岗位", "category": "国企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://inspur.hcmcloud.cn/recruit#/my_resume", "notes": "在线测评todo"},
    {"company": "光大证券", "position": "香港", "category": "国企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://ebscn.zhiye.com/personal/deliveryRecord", "notes": ""},
    {"company": "紫金矿业", "position": "信息化类", "category": "国企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://join.zjky.cn/", "notes": ""},
    {"company": "中国电子科技集团公司第三十八研究所", "position": "2个岗位", "category": "国企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://xiaoyuan.zhaopin.com/scrd/delivery/record", "notes": ""},

    # ===== 外企 =====
    {"company": "特斯拉", "position": "2027届 - 前端软件开发实习生", "category": "外企", "source": "官网", "apply_date": "2026-08-04", "status": "流程中", "link": "https://app.mokahr.com/campus-recruitment/tesla/41460", "notes": ""},
    {"company": "日邮物流", "position": "2个岗位", "category": "外企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://app.mokahr.com/campus-recruitment/yusen/73956", "notes": ""},
    {"company": "塞拉尼斯", "position": "生产工程师-南京", "category": "外企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://xiaoyuan.zhaopin.com/scrd/delivery/record", "notes": ""},
    {"company": "卡特比勒", "position": "2027校园招聘: 研发类-电子/电气/软件、测试方向", "category": "外企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://cat.wd5.myworkdayjobs.com/", "notes": ""},
    {"company": "联想", "position": "前端开发", "category": "外企", "source": "官网", "apply_date": "2026-09-01", "status": "流程中", "link": "https://talent.lenovo.com.cn/account/apply", "notes": ""},

    # ===== 上市私企 =====
    {"company": "经纬横润", "position": "2个岗位", "category": "私企", "source": "官网", "apply_date": "2026-08-21", "status": "流程中", "link": "https://app.mokahr.com/campus-recruitment/jingweihengrun/168294", "notes": ""},
    {"company": "多维联合集团", "position": "2个岗位", "category": "私企", "source": "官网", "apply_date": "2026-08-21", "status": "流程中", "link": "https://app.mokahr.com/campus-recruitment/duowei/142740", "notes": ""},
    {"company": "海四达", "position": "2个岗位", "category": "私企", "source": "官网", "apply_date": "2026-08-21", "status": "流程中", "link": "https://highstar.zhiye.com/personal/deliveryRecord", "notes": ""},
    {"company": "思格新能源", "position": "管培生", "category": "私企", "source": "官网", "apply_date": "2026-08-21", "status": "流程中", "link": "https://jobs.sigenergy.com/campus/position/application", "notes": ""},
    {"company": "小米", "position": "Web前端开发工程师", "category": "私企", "source": "官网", "apply_date": "2026-08-12", "status": "简历挂", "link": "https://xiaomi.jobs.f.mioffice.cn/", "notes": "2026-8-14，8-19挂了，应该是筛简历了"},
    {"company": "阳光电源", "position": "前端开发工程师-AI方向-南京", "category": "私企", "source": "官网", "apply_date": "2026-08-12", "status": "简历挂", "link": "https://app.mokahr.com/campus-recruitment/sungrow/94416", "notes": "2026-8-14，8-20挂了，应该是筛简历了"},
    {"company": "特来电新能源股份有限公司", "position": "前端开发", "category": "私企", "source": "官网", "apply_date": "2026-08-21", "status": "流程中", "link": "https://hr.teld.cn/recruit", "notes": ""},
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
]


def import_data():
    with app.app_context():
        # 清空现有数据（可选）
        # db.session.query(JobApplication).delete()

        count = 0
        for job_data in JOBS_DATA:
            # 检查是否已存在（根据公司和岗位）
            existing = JobApplication.query.filter_by(
                company=job_data['company'],
                position=job_data['position']
            ).first()

            if existing:
                print(f"跳过已存在: {job_data['company']} - {job_data['position']}")
                continue

            job = JobApplication(
                company=job_data['company'],
                position=job_data['position'],
                category=job_data['category'],
                source=job_data['source'],
                apply_date=datetime.strptime(job_data['apply_date'], '%Y-%m-%d').date() if job_data['apply_date'] else None,
                status=job_data['status'],
                link=job_data.get('link', ''),
                notes=job_data.get('notes', ''),
            )
            db.session.add(job)
            count += 1
            print(f"添加: {job_data['company']} - {job_data['position']}")

        db.session.commit()
        print(f"\n成功导入 {count} 条记录！")


if __name__ == '__main__':
    import_data()
