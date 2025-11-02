import sqlite3
from datetime import datetime
import hashlib
import secrets

def get_database_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect('resume_data.db')
    return conn

def init_database():
    """Initialize database tables"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT,
        phone TEXT,
        location TEXT,
        linkedin TEXT,
        github TEXT,
        portfolio TEXT,
        bio TEXT,
        profile_picture TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        is_active BOOLEAN DEFAULT 1
    )
    ''')
    
    # Create resume_data table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resume_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        linkedin TEXT,
        github TEXT,
        portfolio TEXT,
        summary TEXT,
        target_role TEXT,
        target_category TEXT,
        education TEXT,
        experience TEXT,
        projects TEXT,
        skills TEXT,
        template TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create resume_skills table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resume_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER,
        skill_name TEXT NOT NULL,
        skill_category TEXT NOT NULL,
        proficiency_score REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (resume_id) REFERENCES resume_data (id)
    )
    ''')
    
    # Create resume_analysis table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resume_analysis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER,
        ats_score REAL,
        keyword_match_score REAL,
        format_score REAL,
        section_score REAL,
        missing_skills TEXT,
        recommendations TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (resume_id) REFERENCES resume_data (id)
    )
    ''')
    
    # Admin tables removed - no longer needed
    
    conn.commit()
    conn.close()

def save_resume_data(data, user_id=None):
    """Save resume data to database"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        personal_info = data.get('personal_info', {})
        
        cursor.execute('''
        INSERT INTO resume_data (
            user_id, name, email, phone, linkedin, github, portfolio,
            summary, target_role, target_category, education, 
            experience, projects, skills, template
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            personal_info.get('full_name', ''),
            personal_info.get('email', ''),
            personal_info.get('phone', ''),
            personal_info.get('linkedin', ''),
            personal_info.get('github', ''),
            personal_info.get('portfolio', ''),
            data.get('summary', ''),
            data.get('target_role', ''),
            data.get('target_category', ''),
            str(data.get('education', [])),
            str(data.get('experience', [])),
            str(data.get('projects', [])),
            str(data.get('skills', [])),
            data.get('template', '')
        ))
        
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error saving resume data: {str(e)}")
        conn.rollback()
        return None
    finally:
        conn.close()

def save_analysis_data(resume_id, analysis):
    """Save resume analysis data"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT INTO resume_analysis (
            resume_id, ats_score, keyword_match_score,
            format_score, section_score, missing_skills,
            recommendations
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            resume_id,
            float(analysis.get('ats_score', 0)),
            float(analysis.get('keyword_match_score', 0)),
            float(analysis.get('format_score', 0)),
            float(analysis.get('section_score', 0)),
            analysis.get('missing_skills', ''),
            analysis.get('recommendations', '')
        ))
        
        conn.commit()
    except Exception as e:
        print(f"Error saving analysis data: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

def get_resume_stats():
    """Get statistics about resumes"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Get total resumes
        cursor.execute('SELECT COUNT(*) FROM resume_data')
        total_resumes = cursor.fetchone()[0]
        
        # Get average ATS score
        cursor.execute('SELECT AVG(ats_score) FROM resume_analysis')
        avg_ats_score = cursor.fetchone()[0] or 0
        
        # Get recent activity
        cursor.execute('''
        SELECT name, target_role, created_at 
        FROM resume_data 
        ORDER BY created_at DESC 
        LIMIT 5
        ''')
        recent_activity = cursor.fetchall()
        
        return {
            'total_resumes': total_resumes,
            'avg_ats_score': round(avg_ats_score, 2),
            'recent_activity': recent_activity
        }
    except Exception as e:
        print(f"Error getting resume stats: {str(e)}")
        return None
    finally:
        conn.close()

# Admin logging functions removed

def get_all_resume_data():
    """Get all resume data for admin dashboard"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Get resume data joined with analysis data
        cursor.execute('''
        SELECT 
            r.id,
            r.name,
            r.email,
            r.phone,
            r.linkedin,
            r.github,
            r.portfolio,
            r.target_role,
            r.target_category,
            r.created_at,
            a.ats_score,
            a.keyword_match_score,
            a.format_score,
            a.section_score
        FROM resume_data r
        LEFT JOIN resume_analysis a ON r.id = a.resume_id
        ORDER BY r.created_at DESC
        ''')
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting resume data: {str(e)}")
        return []
    finally:
        conn.close()

# Admin verification functions removed

def save_ai_analysis_data(resume_id, analysis_data):
    """Save AI analysis data to the database"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Check if the ai_analysis table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id INTEGER,
                model_used TEXT,
                resume_score INTEGER,
                job_role TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resume_id) REFERENCES resume_data (id)
            )
        """)
        
        # Insert the analysis data
        cursor.execute("""
            INSERT INTO ai_analysis (
                resume_id, model_used, resume_score, job_role
            ) VALUES (?, ?, ?, ?)
        """, (
            resume_id,
            analysis_data.get('model_used', ''),
            analysis_data.get('resume_score', 0),
            analysis_data.get('job_role', '')
        ))
        
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error saving AI analysis data: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def get_ai_analysis_stats():
    """Get statistics about AI analyzer usage"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Check if the ai_analysis table exists
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='ai_analysis'
        """)
        
        if not cursor.fetchone():
            return {
                "total_analyses": 0,
                "model_usage": [],
                "average_score": 0,
                "top_job_roles": []
            }
        
        # Get total number of analyses
        cursor.execute("SELECT COUNT(*) FROM ai_analysis")
        total_analyses = cursor.fetchone()[0]
        
        # Get model usage statistics
        cursor.execute("""
            SELECT model_used, COUNT(*) as count
            FROM ai_analysis
            GROUP BY model_used
            ORDER BY count DESC
        """)
        model_usage = [{"model": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        # Get average resume score
        cursor.execute("SELECT AVG(resume_score) FROM ai_analysis")
        average_score = cursor.fetchone()[0] or 0
        
        # Get top job roles
        cursor.execute("""
            SELECT job_role, COUNT(*) as count
            FROM ai_analysis
            GROUP BY job_role
            ORDER BY count DESC
            LIMIT 5
        """)
        top_job_roles = [{"role": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        return {
            "total_analyses": total_analyses,
            "model_usage": model_usage,
            "average_score": round(average_score, 1),
            "top_job_roles": top_job_roles
        }
    except Exception as e:
        print(f"Error getting AI analysis stats: {e}")
        return {
            "total_analyses": 0,
            "model_usage": [],
            "average_score": 0,
            "top_job_roles": []
        }
    finally:
        conn.close()

def get_detailed_ai_analysis_stats():
    """Get detailed statistics about AI analyzer usage including daily trends"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Check if the ai_analysis table exists
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='ai_analysis'
        """)
        
        if not cursor.fetchone():
            return {
                "total_analyses": 0,
                "model_usage": [],
                "average_score": 0,
                "top_job_roles": [],
                "daily_trend": [],
                "score_distribution": [],
                "recent_analyses": []
            }
        
        # Get total number of analyses
        cursor.execute("SELECT COUNT(*) FROM ai_analysis")
        total_analyses = cursor.fetchone()[0]
        
        # Get model usage statistics
        cursor.execute("""
            SELECT model_used, COUNT(*) as count
            FROM ai_analysis
            GROUP BY model_used
            ORDER BY count DESC
        """)
        model_usage = [{"model": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        # Get average resume score
        cursor.execute("SELECT AVG(resume_score) FROM ai_analysis")
        average_score = cursor.fetchone()[0] or 0
        
        # Get top job roles
        cursor.execute("""
            SELECT job_role, COUNT(*) as count
            FROM ai_analysis
            GROUP BY job_role
            ORDER BY count DESC
            LIMIT 5
        """)
        top_job_roles = [{"role": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        # Get daily trend for the last 7 days
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM ai_analysis
            WHERE created_at >= date('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY date
        """)
        daily_trend = [{"date": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        # Get score distribution
        score_ranges = [
            {"min": 0, "max": 20, "range": "0-20"},
            {"min": 21, "max": 40, "range": "21-40"},
            {"min": 41, "max": 60, "range": "41-60"},
            {"min": 61, "max": 80, "range": "61-80"},
            {"min": 81, "max": 100, "range": "81-100"}
        ]
        
        score_distribution = []
        for range_info in score_ranges:
            cursor.execute("""
                SELECT COUNT(*) FROM ai_analysis 
                WHERE resume_score >= ? AND resume_score <= ?
            """, (range_info["min"], range_info["max"]))
            count = cursor.fetchone()[0]
            score_distribution.append({"range": range_info["range"], "count": count})
        
        # Get recent analyses
        cursor.execute("""
            SELECT model_used, resume_score, job_role, datetime(created_at) as date
            FROM ai_analysis
            ORDER BY created_at DESC
            LIMIT 5
        """)
        recent_analyses = [
            {
                "model": row[0],
                "score": row[1],
                "job_role": row[2],
                "date": row[3]
            } for row in cursor.fetchall()
        ]
        
        return {
            "total_analyses": total_analyses,
            "model_usage": model_usage,
            "average_score": round(average_score, 1),
            "top_job_roles": top_job_roles,
            "daily_trend": daily_trend,
            "score_distribution": score_distribution,
            "recent_analyses": recent_analyses
        }
    except Exception as e:
        print(f"Error getting detailed AI analysis stats: {e}")
        return {
            "total_analyses": 0,
            "model_usage": [],
            "average_score": 0,
            "top_job_roles": [],
            "daily_trend": [],
            "score_distribution": [],
            "recent_analyses": []
        }
    finally:
        conn.close()

def reset_ai_analysis_stats():
    """Reset AI analysis statistics by truncating the ai_analysis table"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Check if the ai_analysis table exists
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='ai_analysis'
        """)
        
        if not cursor.fetchone():
            return {"success": False, "message": "AI analysis table does not exist"}
        
        # Delete all records from the ai_analysis table
        cursor.execute("DELETE FROM ai_analysis")
        conn.commit()
        
        return {"success": True, "message": "AI analysis statistics have been reset successfully"}
    except Exception as e:
        conn.rollback()
        print(f"Error resetting AI analysis stats: {e}")
        return {"success": False, "message": f"Error resetting AI analysis statistics: {str(e)}"}
    finally:
        conn.close()

# User Authentication Functions
def hash_password(password):
    """Hash a password for storing"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return salt + password_hash.hex()

def verify_password(stored_password, provided_password):
    """Verify a stored password against provided password"""
    salt = stored_password[:32]
    stored_hash = stored_password[32:]
    password_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return stored_hash == password_hash.hex()

def create_user(username, email, password, full_name=""):
    """Create a new user"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Check if user already exists
        cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
        if cursor.fetchone():
            return {"success": False, "message": "Username or email already exists"}
        
        # Hash password and create user
        password_hash = hash_password(password)
        cursor.execute('''
        INSERT INTO users (username, email, password_hash, full_name)
        VALUES (?, ?, ?, ?)
        ''', (username, email, password_hash, full_name))
        
        conn.commit()
        user_id = cursor.lastrowid
        return {"success": True, "message": "User created successfully", "user_id": user_id}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error creating user: {str(e)}"}
    finally:
        conn.close()

def authenticate_user(username, password):
    """Authenticate a user"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        SELECT id, username, email, password_hash, full_name, is_active
        FROM users WHERE username = ? OR email = ?
        ''', (username, username))
        
        user = cursor.fetchone()
        if not user:
            return {"success": False, "message": "User not found"}
        
        if not user[5]:  # is_active
            return {"success": False, "message": "Account is deactivated"}
        
        if verify_password(user[3], password):
            # Update last login
            cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user[0],))
            conn.commit()
            
            return {
                "success": True,
                "user": {
                    "id": user[0],
                    "username": user[1],
                    "email": user[2],
                    "full_name": user[4]
                }
            }
        else:
            return {"success": False, "message": "Invalid password"}
    except Exception as e:
        return {"success": False, "message": f"Authentication error: {str(e)}"}
    finally:
        conn.close()

def get_user_profile(user_id):
    """Get user profile information"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        SELECT username, email, full_name, phone, location, linkedin, 
               github, portfolio, bio, profile_picture, created_at, last_login
        FROM users WHERE id = ?
        ''', (user_id,))
        
        user = cursor.fetchone()
        if user:
            return {
                "username": user[0],
                "email": user[1],
                "full_name": user[2],
                "phone": user[3],
                "location": user[4],
                "linkedin": user[5],
                "github": user[6],
                "portfolio": user[7],
                "bio": user[8],
                "profile_picture": user[9],
                "created_at": user[10],
                "last_login": user[11]
            }
        return None
    except Exception as e:
        print(f"Error getting user profile: {str(e)}")
        return None
    finally:
        conn.close()

def update_user_profile(user_id, profile_data):
    """Update user profile information"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        UPDATE users SET 
            full_name = ?, phone = ?, location = ?, linkedin = ?,
            github = ?, portfolio = ?, bio = ?
        WHERE id = ?
        ''', (
            profile_data.get('full_name', ''),
            profile_data.get('phone', ''),
            profile_data.get('location', ''),
            profile_data.get('linkedin', ''),
            profile_data.get('github', ''),
            profile_data.get('portfolio', ''),
            profile_data.get('bio', ''),
            user_id
        ))
        
        conn.commit()
        return {"success": True, "message": "Profile updated successfully"}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error updating profile: {str(e)}"}
    finally:
        conn.close()