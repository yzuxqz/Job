from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from functools import wraps
import os
import hashlib
import secrets

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

app.config['SECRET_KEY'] = secrets.token_hex(32)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "jobs.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ==================== Database Models ====================

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    salt = db.Column(db.String(32), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.salt = secrets.token_hex(16)
        self.password_hash = hashlib.sha256((password + self.salt).encode()).hexdigest()

    def check_password(self, password):
        return self.password_hash == hashlib.sha256((password + self.salt).encode()).hexdigest()

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Session(db.Model):
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class JobApplication(db.Model):
    __tablename__ = 'job_applications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    position = db.Column(db.String(300), nullable=False)
    category = db.Column(db.String(50), default='国企')
    source = db.Column(db.String(50), default='官网')
    apply_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default='流程中')
    exam_date = db.Column(db.Date, nullable=True)
    link = db.Column(db.String(500), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    # 招聘平台专用字段
    pass_screening = db.Column(db.Integer, default=0)
    in_exam = db.Column(db.Integer, default=0)
    in_interview = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'company': self.company,
            'position': self.position,
            'category': self.category,
            'source': self.source,
            'apply_date': self.apply_date.isoformat() if self.apply_date else None,
            'status': self.status,
            'exam_date': self.exam_date.isoformat() if self.exam_date else None,
            'link': self.link or '',
            'notes': self.notes or '',
            'pass_screening': self.pass_screening or 0,
            'in_exam': self.in_exam or 0,
            'in_interview': self.in_interview or 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


with app.app_context():
    db.create_all()


# ==================== Auth Helpers ====================

def generate_token():
    return secrets.token_hex(32)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': '请先登录'}), 401

        session = Session.query.filter_by(token=token).first()
        if not session or session.expires_at < datetime.utcnow():
            return jsonify({'error': '登录已过期，请重新登录'}), 401

        request.user_id = session.user_id
        return f(*args, **kwargs)
    return decorated_function


# ==================== Auth API ====================

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    if len(username) < 3:
        return jsonify({'error': '用户名至少3个字符'}), 400
    if len(password) < 6:
        return jsonify({'error': '密码至少6个字符'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'error': '用户名已存在'}), 409

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': '注册成功', 'user': user.to_dict()}), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'error': '用户名或密码错误'}), 401

    token = generate_token()
    expires_at = datetime.utcnow() + timedelta(days=30)
    session = Session(user_id=user.id, token=token, expires_at=expires_at)
    db.session.add(session)
    db.session.commit()

    return jsonify({
        'message': '登录成功',
        'token': token,
        'user': user.to_dict()
    })


@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    session = Session.query.filter_by(token=token).first()
    if session:
        db.session.delete(session)
        db.session.commit()
    return jsonify({'message': '已退出登录'})


@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user():
    user = User.query.get(request.user_id)
    return jsonify({'user': user.to_dict()})


@app.route('/api/auth/change-password', methods=['POST'])
@login_required
def change_password():
    data = request.get_json()
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')

    if len(new_password) < 6:
        return jsonify({'error': '新密码至少6个字符'}), 400

    user = User.query.get(request.user_id)
    if not user.check_password(old_password):
        return jsonify({'error': '原密码错误'}), 400

    user.set_password(new_password)
    db.session.commit()
    Session.query.filter_by(user_id=user.id).delete()
    db.session.commit()

    return jsonify({'message': '密码修改成功，请重新登录'})


# ==================== Job API ====================

@app.route('/api/jobs', methods=['GET'])
@login_required
def get_jobs():
    category = request.args.get('category', 'all')
    status = request.args.get('status', 'all')
    source = request.args.get('source', 'all')
    search = request.args.get('search', '')

    query = JobApplication.query.filter_by(user_id=request.user_id)

    if category != 'all':
        query = query.filter_by(category=category)
    if status != 'all':
        query = query.filter_by(status=status)
    if source != 'all':
        query = query.filter_by(source=source)
    if search:
        query = query.filter(
            db.or_(
                JobApplication.company.contains(search),
                JobApplication.position.contains(search)
            )
        )

    jobs = query.order_by(JobApplication.apply_date.desc()).all()
    return jsonify([job.to_dict() for job in jobs])


@app.route('/api/jobs/<int:job_id>', methods=['GET'])
@login_required
def get_job(job_id):
    job = JobApplication.query.filter_by(id=job_id, user_id=request.user_id).first_or_404()
    return jsonify(job.to_dict())


@app.route('/api/jobs', methods=['POST'])
@login_required
def create_job():
    data = request.get_json()

    job = JobApplication(
        user_id=request.user_id,
        company=data.get('company', ''),
        position=data.get('position', ''),
        category=data.get('category', '国企'),
        source=data.get('source', '官网'),
        apply_date=datetime.strptime(data['apply_date'], '%Y-%m-%d').date() if data.get('apply_date') else None,
        status=data.get('status', '流程中'),
        exam_date=datetime.strptime(data['exam_date'], '%Y-%m-%d').date() if data.get('exam_date') else None,
        link=data.get('link', ''),
        notes=data.get('notes', ''),
        pass_screening=data.get('pass_screening', 0),
        in_exam=data.get('in_exam', 0),
        in_interview=data.get('in_interview', 0),
    )

    db.session.add(job)
    db.session.commit()
    return jsonify(job.to_dict()), 201


@app.route('/api/jobs/<int:job_id>', methods=['PUT'])
@login_required
def update_job(job_id):
    job = JobApplication.query.filter_by(id=job_id, user_id=request.user_id).first_or_404()
    data = request.get_json()

    job.company = data.get('company', job.company)
    job.position = data.get('position', job.position)
    job.category = data.get('category', job.category)
    job.source = data.get('source', job.source)
    job.apply_date = datetime.strptime(data['apply_date'], '%Y-%m-%d').date() if data.get('apply_date') else job.apply_date
    job.status = data.get('status', job.status)
    job.exam_date = datetime.strptime(data['exam_date'], '%Y-%m-%d').date() if data.get('exam_date') else job.exam_date
    job.link = data.get('link', job.link)
    job.notes = data.get('notes', job.notes)
    job.pass_screening = data.get('pass_screening', job.pass_screening)
    job.in_exam = data.get('in_exam', job.in_exam)
    job.in_interview = data.get('in_interview', job.in_interview)

    db.session.commit()
    return jsonify(job.to_dict())


@app.route('/api/jobs/<int:job_id>', methods=['DELETE'])
@login_required
def delete_job(job_id):
    job = JobApplication.query.filter_by(id=job_id, user_id=request.user_id).first_or_404()
    db.session.delete(job)
    db.session.commit()
    return jsonify({'message': '删除成功'})


@app.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    import re
    from datetime import date

    user_id = request.user_id
    base_query = JobApplication.query.filter_by(user_id=user_id)
    today = date.today()

    # 计算招聘平台总岗位数
    platform_query = base_query.filter_by(category='招聘平台')
    platform_total_positions = 0
    platform_no_reply = 0  # 从备注中提取已读不回

    for p in platform_query.all():
        # 从岗位字段提取数字
        pos = p.position
        if pos:
            numbers = re.findall(r'\d+', pos)
            if numbers:
                platform_total_positions += int(numbers[0])

        # 从备注中提取已读不回数量
        if p.notes:
            # 匹配 "X个已读不回" 或 "X个已读"
            match = re.search(r'(\d+)\s*个\s*已读\s*不回', p.notes)
            if match:
                platform_no_reply += int(match.group(1))

    # 非招聘平台记录（有投递时间的才算）
    normal_query = base_query.filter(JobApplication.category != '招聘平台')
    # 有投递时间的记录
    dated_query = normal_query.filter(JobApplication.apply_date.isnot(None))
    # 无投递时间的记录
    undated_query = normal_query.filter(JobApplication.apply_date.is_(None))

    # 总投递 = 有投递时间的记录 + 招聘平台岗位数
    total = dated_query.count() + platform_total_positions

    # 超1月不回复：有投递时间 + 流程中 + 投递时间超过1个月
    over_1month = 0
    for job in dated_query.filter(JobApplication.status.in_(['流程中', '笔试通过', '面试中'])).all():
        if job.apply_date:
            days_diff = (today - job.apply_date).days
            if days_diff > 30:
                over_1month += 1

    # 已读不回：从招聘平台备注中提取
    no_reply = platform_no_reply

    # 已挂：简历挂 + 笔试挂
    rejected = normal_query.filter(JobApplication.status.in_(['简历挂', '笔试挂'])).count()

    # 进面：面试中 + 面试放弃（没去也算）
    interview = normal_query.filter(JobApplication.status.in_(['面试中', '面试放弃'])).count()

    # 笔试：笔试通过 + 笔试挂
    written = normal_query.filter(JobApplication.status.in_(['笔试通过', '笔试挂'])).count()

    # Offer
    offer = normal_query.filter_by(status='已拿offer').count()

    # 流程中 = 有投递时间 - 已挂 - 超1月 - 已读不回
    pending = dated_query.count() - rejected - over_1month

    # Category stats
    categories = ['国企', '外企', '私企', '招聘平台']
    cat_stats = {}
    for cat in categories:
        cat_query = base_query.filter_by(category=cat)
        if cat == '招聘平台':
            cat_stats[cat] = {
                'count': cat_query.count(),
                'positions': platform_total_positions,
                'reject': 0
            }
        else:
            cat_stats[cat] = {
                'count': cat_query.count(),
                'reject': cat_query.filter(JobApplication.status.in_(['简历挂', '笔试挂'])).count()
            }

    return jsonify({
        'total': total,
        'pending': pending,
        'rejected': rejected,
        'interview': interview,
        'written': written,
        'offer': offer,
        'over_1month': over_1month,
        'no_reply': no_reply,
        'categories': cat_stats
    })


@app.route('/api/jobs/import', methods=['POST'])
@login_required
def batch_import():
    data = request.get_json()
    jobs = data.get('jobs', [])

    for job_data in jobs:
        job = JobApplication(
            user_id=request.user_id,
            company=job_data.get('company', ''),
            position=job_data.get('position', ''),
            category=job_data.get('category', '国企'),
            source=job_data.get('source', '官网'),
            apply_date=datetime.strptime(job_data['apply_date'], '%Y-%m-%d').date() if job_data.get('apply_date') else None,
            status=job_data.get('status', '流程中'),
            exam_date=datetime.strptime(job_data['exam_date'], '%Y-%m-%d').date() if job_data.get('exam_date') else None,
            link=job_data.get('link', ''),
            notes=job_data.get('notes', ''),
            pass_screening=job_data.get('pass_screening', 0),
            in_exam=job_data.get('in_exam', 0),
            in_interview=job_data.get('in_interview', 0),
        )
        db.session.add(job)

    db.session.commit()
    return jsonify({'message': f'成功导入 {len(jobs)} 记录'}), 201


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
