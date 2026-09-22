from datetime import datetime
from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Cho phép Netlify gửi request tới server này
visits = []

@app.route('/log', methods=['POST', 'GET'])
def log_visit():
  if request.headers.get('X-Forwarded-For'):
    ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
  else:
    ip = request.remote_addr
    
  ip_type = 'IPv6' if ':' in ip else 'IPv4'

  user_agent = request.headers.get('User-Agent')
  method = request.method
  path = request.args.get('path', '/')
  time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

  visit_data = {
      'ip': ip,
      'ip_type': ip_type,
      'method': method,
      'path': path,
      'user_agent': user_agent,
      'time': time_str,
  }

  visits.append(visit_data)

  # Giới hạn lưu 200 lượt truy cập gần nhất để tránh tốn RAM
  if len(visits) > 200:
    visits.pop(0)

  return jsonify({'status': 'success'}), 200


@app.route('/checkinfo', methods=['GET'])
def check_info():
  html_template = """
   <!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analytics Dashboard - Access Logs</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --border-color: #334155;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --primary: #38bdf8;
            --primary-hover: #0284c7;
            --ipv4-bg: rgba(34, 197, 94, 0.15);
            --ipv4-color: #4ade80;
            --ipv6-bg: rgba(56, 189, 248, 0.15);
            --ipv6-color: #38bdf8;
            --table-hover: #26334d;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-main);
            padding: 2rem;
            min-height: 100vh;
        }

        .container {
            max-width: 1280px;
            margin: 0 auto;
        }

        /* Header section */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
        }

        .header h1 {
            font-size: 1.5rem;
            font-weight: 700;
            letter-spacing: -0.025em;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .header h1::before {
            content: '';
            display: inline-block;
            width: 8px;
            height: 24px;
            background: var(--primary);
            border-radius: 4px;
        }

        .subtitle {
            color: var(--text-muted);
            font-size: 0.875rem;
            margin-top: 4px;
        }

        /* Stat Cards */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .stat-card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .stat-card .label {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            font-weight: 600;
        }

        .stat-card .value {
            font-size: 1.875rem;
            font-weight: 700;
            color: var(--text-main);
        }

        /* Table Section */
        .table-card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        }

        .table-wrapper {
            width: 100%;
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 0.875rem;
        }

        th {
            background-color: rgba(15, 23, 42, 0.6);
            color: var(--text-muted);
            font-weight: 600;
            padding: 1rem;
            border-bottom: 1px solid var(--border-color);
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
            white-space: nowrap;
        }

        td {
            padding: 1rem;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-main);
            vertical-align: middle;
        }

        tr:last-child td {
            border-bottom: none;
        }

        tr:hover td {
            background-color: var(--table-hover);
        }

        /* Badges */
        .badge {
            display: inline-flex;
            align-items: center;
            padding: 2px 8px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
        }

        .badge.ipv4 {
            background-color: var(--ipv4-bg);
            color: var(--ipv4-color);
            border: 1px solid rgba(74, 222, 128, 0.3);
        }

        .badge.ipv6 {
            background-color: var(--ipv6-bg);
            color: var(--ipv6-color);
            border: 1px solid rgba(56, 189, 248, 0.3);
        }

        .method {
            font-weight: 700;
            font-family: monospace;
            color: #f59e0b;
        }

        .ip-address {
            font-family: monospace;
            font-size: 0.9rem;
            font-weight: 600;
        }

        .user-agent {
            color: var(--text-muted);
            font-size: 0.8rem;
            max-width: 320px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            display: block;
        }

        .path-code {
            background: rgba(0, 0, 0, 0.2);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
            color: var(--primary);
        }

        @media (max-width: 768px) {
            body {
                padding: 1rem;
            }
            .header {
                flex-direction: column;
                align-items: flex-start;
                gap: 8px;
            }
        }
    </style>
</head>
<body>

    <div class="container">
        <!-- Header -->
        <div class="header">
            <div>
                <h1>Nhật ký hệ thống</h1>
                <p class="subtitle">m1nhquaanz.netlify.app</p>
            </div>
        </div>

        <!-- Dashboard Stat Cards -->
        <div class="stats-grid">
            <div class="stat-card">
                <span class="label">Tổng Lượt Ghi Nhận</span>
                <span class="value">{{ visits|length }}</span>
            </div>
            <div class="stat-card">
                <span class="label">Trạng Thái API</span>
                <span class="value" style="color: #4ade80;">Active</span>
            </div>
        </div>

        <!-- Data Table -->
        <div class="table-card">
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>Thời gian</th>
                            <th>Địa chỉ IP</th>
                            <th>Loại IP</th>
                            <th>Phương thức</th>
                            <th>Đường dẫn</th>
                            <th>Trình duyệt / Thiết bị</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for v in visits | reverse %}
                        <tr>
                            <td style="white-space: nowrap; color: var(--text-muted);">{{ v.time }}</td>
                            <td class="ip-address">{{ v.ip }}</td>
                            <td>
                                <span class="badge {{ 'ipv6' if v.ip_type == 'IPv6' else 'ipv4' }}">
                                    {{ v.ip_type }}
                                </span>
                            </td>
                            <td class="method">{{ v.method }}</td>
                            <td><span class="path-code">{{ v.path }}</span></td>
                            <td><span class="user-agent" title="{{ v.user_agent }}">{{ v.user_agent }}</span></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

</body>
</html>
    """
  return render_template_string(html_template, visits=visits)


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)
