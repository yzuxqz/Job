from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "jobs.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Database Model
class JobApplication(db.Model):
    __tablename__ = 'job_applications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company = db.Column(db.String(200), nullable=False)
    position = db.Column(db.String(300), nullable=False)
    category = db.Column(db.String(50), default='国企')  # 国企/央企, 外企, 私企
    source = db.Column(db.String(50), default='官网')  # 官网, 国聘, 应届生, 智联, 51job, boss
    apply_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default='流程中')
    exam_date = db.Column(db.Date, nullable=True)
    link = db.Column(db.String(500), nullable=True)
    notes = db.Column(db.Text, nullable=True)
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
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


# Create tables
with app.app_context():
    db.create_all()


# ==================== API Routes ====================

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


# Get all applications
@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    category = request.args.get('category', 'all')
    status = request.args.get('status', 'all')
    source = request.args.get('source', 'all')
    search = request.args.get('search', '')

    query = JobApplication.query

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


# Get single application
@app.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    job = JobApplication.query.get_or_404(job_id)
    return jsonify(job.to_dict())


# Create new application
@app.route('/api/jobs', methods=['POST'])
def create_job():
    data = request.get_json()

    job = JobApplication(
        company=data.get('company', ''),
        position=data.get('position', ''),
        category=data.get('category', '国企'),
        source=data.get('source', '官网'),
        apply_date=datetime.strptime(data['apply_date'], '%Y-%m-%d').date() if data.get('apply_date') else None,
        status=data.get('status', '流程中'),
        exam_date=datetime.strptime(data['exam_date'], '%Y-%m-%d').date() if data.get('exam_date') else None,
        link=data.get('link', ''),
        notes=data.get('notes', ''),
    )

    db.session.add(job)
    db.session.commit()
    return jsonify(job.to_dict()), 201


# Update application
@app.route('/api/jobs/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    job = JobApplication.query.get_or_404(job_id)
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

    db.session.commit()
    return jsonify(job.to_dict())


# Delete application
@app.route('/api/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    job = JobApplication.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    return jsonify({'message': '删除成功'})


# Get statistics
@app.route('/api/stats', methods=['GET'])
def get_stats():
    total = JobApplication.query.count()
    pending = JobApplication.query.filter(JobApplication.status.in_(['流程中', '笔试通过', '面试中'])).count()
    rejected = JobApplication.query.filter(JobApplication.status.in_(['简历挂', '笔试挂'])).count()
    interview = JobApplication.query.filter_by(status='面试中').count()
    written = JobApplication.query.filter(JobApplication.status.in_(['笔试通过', '笔试挂'])).count()
    offer = JobApplication.query.filter_by(status='已拿offer').count()

    # Category stats
    state_count = JobApplication.query.filter_by(category='国企').count()
    state_reject = JobApplication.query.filter_by(category='国企', status='简历挂').count() + \
                   JobApplication.query.filter_by(category='国企', status='笔试挂').count()
    foreign_count = JobApplication.query.filter_by(category='外企').count()
    foreign_reject = JobApplication.query.filter_by(category='外企', status='简历挂').count() + \
                     JobApplication.query.filter_by(category='外企', status='笔试挂').count()
    private_count = JobApplication.query.filter_by(category='私企').count()
    private_reject = JobApplication.query.filter_by(category='私企', status='简历挂').count() + \
                     JobApplication.query.filter_by(category='私企', status='笔试挂').count()

    return jsonify({
        'total': total,
        'pending': pending,
        'rejected': rejected,
        'interview': interview,
        'written': written,
        'offer': offer,
        'categories': {
            'state': {'count': state_count, 'reject': state_reject},
            'foreign': {'count': foreign_count, 'reject': foreign_reject},
            'private': {'count': private_count, 'reject': private_reject},
        }
    })


# Batch import
@app.route('/api/jobs/import', methods=['POST'])
def batch_import():
    data = request.get_json()
    jobs = data.get('jobs', [])

    for job_data in jobs:
        job = JobApplication(
            company=job_data.get('company', ''),
            position=job_data.get('position', ''),
            category=job_data.get('category', '国企'),
            source=job_data.get('source', '官网'),
            apply_date=datetime.strptime(job_data['apply_date'], '%Y-%m-%d').date() if job_data.get('apply_date') else None,
            status=job_data.get('status', '流程中'),
            exam_date=datetime.strptime(job_data['exam_date'], '%Y-%m-%d').date() if job_data.get('exam_date') else None,
            link=job_data.get('link', ''),
            notes=job_data.get('notes', ''),
        )
        db.session.add(job)

    db.session.commit()
    return jsonify({'message': f'成功导入 {len(jobs)} 条记录'}), 201


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
