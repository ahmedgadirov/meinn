"""
Analytics routes for user action logging and admin analytics.
"""

from flask import Blueprint, request, jsonify
import sqlite3
import time

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

@analytics_bp.route('/user_action', methods=['POST'])
def log_user_action():
    """
    Log a user action (view, click, order, etc.) for analytics and recommendations.
    Expects JSON: { "user_id": str, "action_type": str, "item_id": str, "timestamp": int (optional) }
    """
    try:
        data = request.json
        user_id = data.get('user_id')
        action_type = data.get('action_type')
        item_id = data.get('item_id')
        timestamp = data.get('timestamp', int(time.time()))
        
        if not user_id or not action_type or not item_id:
            return jsonify({
                "success": False,
                "error": "Missing required fields: user_id, action_type, item_id"
            }), 400
        
        # Store the action in the analytics_data.db database
        conn = sqlite3.connect('analytics_data.db')
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                action_type TEXT,
                item_id TEXT,
                timestamp INTEGER
            )
        """)
        cursor.execute("""
            INSERT INTO user_actions (user_id, action_type, item_id, timestamp)
            VALUES (?, ?, ?, ?)
        """, (user_id, action_type, item_id, timestamp))
        conn.commit()
        conn.close()
        
        return jsonify({ "success": True })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@analytics_bp.route('/summary', methods=['GET'])
def get_analytics_summary():
    """
    Get summary analytics for the admin panel.
    Returns top viewed, top added to cart, and top ordered items.
    """
    try:
        conn = sqlite3.connect('analytics_data.db')
        cursor = conn.cursor()
        # Ensure the user_actions table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                action_type TEXT,
                item_id TEXT,
                timestamp INTEGER
            )
        """)
        # Top viewed items
        cursor.execute("""
            SELECT item_id, COUNT(*) as views
            FROM user_actions
            WHERE action_type = 'view'
            GROUP BY item_id
            ORDER BY views DESC
            LIMIT 10
        """)
        top_viewed = [{"item_id": row[0], "views": row[1]} for row in cursor.fetchall()]
        # Top added to cart items
        cursor.execute("""
            SELECT item_id, COUNT(*) as adds
            FROM user_actions
            WHERE action_type = 'add_to_cart'
            GROUP BY item_id
            ORDER BY adds DESC
            LIMIT 10
        """)
        top_added = [{"item_id": row[0], "adds": row[1]} for row in cursor.fetchall()]
        # Top ordered items (if order logging is added in the future)
        cursor.execute("""
            SELECT item_id, COUNT(*) as orders
            FROM user_actions
            WHERE action_type = 'order'
            GROUP BY item_id
            ORDER BY orders DESC
            LIMIT 10
        """)
        top_ordered = [{"item_id": row[0], "orders": row[1]} for row in cursor.fetchall()]
        conn.close()
        return jsonify({
            "success": True,
            "top_viewed": top_viewed,
            "top_added_to_cart": top_added,
            "top_ordered": top_ordered
        })
    except Exception as e:
        import traceback
        print("Error in /api/analytics/summary:", traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
