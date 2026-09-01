"""
导入招聘平台每日岗位记录
运行: python import_platform_daily.py
"""
from app import app, db, PlatformDailyRecord, User
from datetime import datetime

# 初始数据：根据现有招聘平台记录
INITIAL_RECORDS = [
    {"date": "2026-08-01", "platform": "国聘网", "positions_count": 11, "positions_added": 11, "note": "初始导入"},
    {"date": "2026-08-01", "platform": "应届生求职网", "positions_count": 32, "positions_added": 32, "note": "初始导入"},
    {"date": "2026-08-01", "platform": "智联招聘", "positions_count": 13, "positions_added": 13, "note": "单投13个"},
    {"date": "2026-08-01", "platform": "51Job", "positions_count": 6, "positions_added": 6, "note": "初始导入"},
]


def import_data():
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("请先运行 import_data.py 创建用户")
            return

        user_id = admin.id
        count = 0

        for record_data in INITIAL_RECORDS:
            # 检查是否已存在
            existing = PlatformDailyRecord.query.filter_by(
                user_id=user_id,
                date=datetime.strptime(record_data['date'], '%Y-%m-%d').date(),
                platform=record_data['platform']
            ).first()

            if existing:
                print(f"跳过已存在: {record_data['date']} - {record_data['platform']}")
                continue

            record = PlatformDailyRecord(
                user_id=user_id,
                date=datetime.strptime(record_data['date'], '%Y-%m-%d').date(),
                platform=record_data['platform'],
                positions_count=record_data['positions_count'],
                positions_added=record_data['positions_added'],
                note=record_data.get('note', ''),
            )
            db.session.add(record)
            count += 1
            print(f"添加: {record_data['date']} - {record_data['platform']} ({record_data['positions_count']}个岗位)")

        db.session.commit()
        print(f"\n成功导入 {count} 条记录！")


if __name__ == '__main__':
    import_data()
