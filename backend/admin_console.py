"""
Admin Console UI for iAmSmartGate
Web-based admin interface
"""
from flask import Flask, render_template_string, request, redirect, url_for
import requests
import json
from datetime import datetime

# HTML template for admin console
ADMIN_CONSOLE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>iAmSmartGate Admin Console</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #3f4140 0%, #1d2c2a 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #1d2c2a 0%, #3f4140 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 2em;
            margin-bottom: 10px;
        }
        .header p {
            opacity: 0.8;
            font-size: 0.9em;
        }
        .tabs {
            display: flex;
            background: #f7fafc;
            border-bottom: 2px solid #e2e8f0;
            position: relative;
            overflow: hidden;
        }
        .tabs-wrapper {
            display: flex;
            transition: transform 0.5s ease-in-out;
            width: 100%;
        }
        .tabs-container {
            display: flex;
            position: relative;
            overflow: hidden;
        }
        .tab {
            flex: 0 0 auto;
            min-width: 150px;
            padding: 15px;
            text-align: center;
            cursor: pointer;
            background: #f7fafc;
            border: none;
            font-size: 1em;
            font-weight: 600;
            color: #4a5568;
            transition: all 0.3s;
        }
        .tab:hover {
            background: #edf2f7;
        }
        .tab.active {
            background: white;
            color: #4DB8A8;
            border-bottom: 3px solid #4DB8A8;
        }
        .carousel-nav {
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(77, 184, 168, 0.9);
            color: white;
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 1.5em;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10;
            transition: all 0.3s;
        }
        .carousel-nav:hover {
            background: #3A9D8F;
            transform: translateY(-50%) scale(1.1);
        }
        .carousel-prev {
            left: 10px;
        }
        .carousel-next {
            right: 10px;
        }
        .content {
            padding: 30px;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .controls {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: 600;
        }
        .btn-primary {
            background: #4DB8A8;
            color: white;
        }
        .btn-primary:hover {
            background: #3A9D8F;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(77, 184, 168, 0.3);
        }
        .btn-danger {
            background: #f56565;
            color: white;
        }
        .btn-danger:hover {
            background: #e53e3e;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(245, 101, 101, 0.3);
        }
        .btn-success {
            background: #48bb78;
            color: white;
        }
        .btn-success:hover {
            background: #38a169;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(72, 187, 120, 0.3);
        }
        .btn-warning {
            background: #ed8936;
            color: white;
        }
        .btn-warning:hover {
            background: #dd6b20;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: linear-gradient(135deg, #4DB8A8 0%, #3A9D8F 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .stat-card h3 {
            font-size: 2em;
            margin-bottom: 5px;
        }
        .stat-card p {
            opacity: 0.9;
            font-size: 0.9em;
        }
        .table-container {
            overflow-x: auto;
            margin-top: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
        }
        th {
            background: #f7fafc;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #4a5568;
            border-bottom: 2px solid #e2e8f0;
        }
        td {
            padding: 12px;
            border-bottom: 1px solid #e2e8f0;
        }
        tr:hover {
            background: #f7fafc;
        }
        .status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }
        .status-process { background: #fef3c7; color: #92400e; }
        .status-pass { background: #d1fae5; color: #065f46; }
        .status-nopass { background: #fee2e2; color: #991b1b; }
        .status-used { background: #e0e7ff; color: #3730a3; }
        .status-revoked { background: #fecaca; color: #7f1d1d; }
        .log-entry {
            padding: 10px;
            margin: 5px 0;
            background: #f7fafc;
            border-left: 4px solid #4DB8A8;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        .log-success { border-left-color: #48bb78; }
        .log-error { border-left-color: #f56565; }
        .log-warning { border-left-color: #ed8936; }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #4a5568;
        }
        .form-group input, .form-group select {
            width: 100%;
            padding: 10px;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            font-size: 1em;
        }
        .site-group {
            background: #f7fafc;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .site-group h3 {
            margin-bottom: 15px;
            color: #2d3748;
        }
        .site-stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
        }
        .site-stat {
            text-align: center;
            padding: 10px;
            background: white;
            border-radius: 6px;
        }
        .site-stat .number {
            font-size: 1.5em;
            font-weight: bold;
            color: #4DB8A8;
        }
        .site-stat .label {
            font-size: 0.8em;
            color: #718096;
        }
        .refresh-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: #4DB8A8;
            color: white;
            border: none;
            font-size: 1.5em;
            cursor: pointer;
            box-shadow: 0 5px 20px rgba(77, 184, 168, 0.4);
            transition: all 0.3s;
        }
        .refresh-btn:hover {
            transform: scale(1.1) rotate(180deg);
        }
        .system-status {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-weight: 600;
            text-align: center;
        }
        .system-active {
            background: #d1fae5;
            color: #065f46;
        }
        .system-paused {
            background: #fee2e2;
            color: #991b1b;
        }
        .hsm-section {
            background: #f7fafc;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            border: 2px solid #4DB8A8;
        }
        .hsm-section h3 {
            color: #2d3748;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .hsm-query-form {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        .hsm-result {
            background: white;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #4DB8A8;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            word-break: break-all;
        }
        .signature-log {
            background: white;
            padding: 10px;
            margin: 5px 0;
            border-radius: 6px;
            border-left: 4px solid #48bb78;
            font-size: 0.9em;
        }
        .signature-log.failed {
            border-left-color: #f56565;
        }
        .signature-log .timestamp {
            color: #718096;
            font-size: 0.85em;
        }
        .signature-log .user-id {
            font-weight: 600;
            color: #4DB8A8;
        }
    
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Admin Console</h1>
            <p>iAM SmartGate Management & Dashboard</p>
        </div>
        
        <div class="tabs">
            <button class="carousel-nav carousel-prev" onclick="scrollTabs(-1)">‹</button>
            <div class="tabs-container" id="tabs-container">
                <div class="tabs-wrapper" id="tabs-wrapper">
                    <button class="tab active" onclick="showTab('dashboard')">
                        <div style="font-size: 1.5em;">📊</div>
                        <div>Dashboard</div>
                    </button>
                    <button class="tab" onclick="showTab('pending')">
                        <div style="font-size: 1.5em;">⏳</div>
                        <div>Pending Passes</div>
                    </button>
                    <button class="tab" onclick="showTab('all-passes')">
                        <div style="font-size: 1.5em;">📋</div>
                        <div>All Passes</div>
                    </button>
                    <button class="tab" onclick="showTab('logs')">
                        <div style="font-size: 1.5em;">📝</div>
                        <div>Audit Logs</div>
                    </button>
                    <button class="tab" onclick="showTab('control')">
                        <div style="font-size: 1.5em;">⚙️</div>
                        <div>System Control</div>
                    </button>
                    <button class="tab" onclick="showTab('register')">
                        <div style="font-size: 1.5em;">➕</div>
                        <div>Register Gate</div>
                    </button>
                    <button class="tab" onclick="showTab('hsm')">
                        <div style="font-size: 1.5em;">🔐</div>
                        <div>Quantum Safe HSM</div>
                    </button>
                </div>
            </div>
            <button class="carousel-nav carousel-next" onclick="scrollTabs(1)">›</button>
        </div>
        
        <div class="content">
            <!-- Dashboard Tab -->
            <div id="dashboard" class="tab-content active">
                <div id="system-status-banner" class="system-status system-active">
                    ✅ System Active
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px;">
                    <div style="background: #d1fae5; color: #065f46; padding: 15px; border-radius: 8px; text-align: center;">
                        <div style="font-weight: 600; margin-bottom: 5px;">iAM Smart API</div>
                        <div style="font-size: 1.2em; font-weight: bold;">🟢</div>
                    </div>
                    <div style="background: #d1fae5; color: #065f46; padding: 15px; border-radius: 8px; text-align: center;">
                        <div style="font-weight: 600; margin-bottom: 5px;">Quantum-Safe HSM</div>
                        <div style="font-size: 1.2em; font-weight: bold;">🟢</div>
                    </div>
                    <div style="background: #d1fae5; color: #065f46; padding: 15px; border-radius: 8px; text-align: center;">
                        <div style="font-weight: 600; margin-bottom: 5px;">Quantum-Safe SSL</div>
                        <div style="font-size: 1.2em; font-weight: bold;">🟢</div>
                    </div>
                </div>
                
                <div class="stats" id="stats-container">
                    <!-- Stats will be loaded here -->
                </div>
                
                <div id="site-groups-container">
                    <!-- Site groups will be loaded here -->
                </div>
            </div>
            
            <!-- Pending Passes Tab -->
            <div id="pending" class="tab-content">
                <h2 style="margin-bottom: 20px;">Pending Pass Applications</h2>
                <div class="table-container">
                    <table id="pending-table">
                        <thead>
                            <tr>
                                <th>Pass ID</th>
                                <th>User ID</th>
                                <th>Site</th>
                                <th>Purpose</th>
                                <th>Visit Date</th>
                                <th>Applied</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="pending-tbody">
                            <!-- Pending passes will be loaded here -->
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- All Passes Tab -->
            <div id="all-passes" class="tab-content">
                <h2 style="margin-bottom: 20px;">All Passes</h2>
                <div class="controls">
                    <select id="status-filter" onchange="loadAllPasses()">
                        <option value="">All Statuses</option>
                        <option value="In Process">In Process</option>
                        <option value="Pass">Pass</option>
                        <option value="No Pass">No Pass</option>
                        <option value="Used">Used</option>
                        <option value="Revoked">Revoked</option>
                    </select>
                    <select id="site-filter" onchange="loadAllPasses()">
                        <option value="">All Sites</option>
                        <option value="SITE001">Main Campus</option>
                        <option value="SITE002">Student Halls</option>
                        <option value="SITE003">Research Center</option>
                        <option value="SITE004">Library</option>
                    </select>
                </div>
                <div class="table-container">
                    <table id="all-passes-table">
                        <thead>
                            <tr>
                                <th>Pass ID</th>
                                <th>User ID</th>
                                <th>Site</th>
                                <th>Purpose</th>
                                <th>Status</th>
                                <th>Visit Date</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="all-passes-tbody">
                            <!-- All passes will be loaded here -->
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Audit Logs Tab -->
            <div id="logs" class="tab-content">
                <h2 style="margin-bottom: 20px;">Recent Audit Logs</h2>
                <div id="logs-container" style="max-height: 600px; overflow-y: auto;">
                    <!-- Logs will be loaded here -->
                </div>
            </div>
            
            <!-- System Control Tab -->
            <div id="control" class="tab-content">
                <h2 style="margin-bottom: 20px;">System Control</h2>
                
                <div class="controls">
                    <button class="btn btn-danger" onclick="pauseSystem(true)">⏸️ Pause All Access</button>
                    <button class="btn btn-success" onclick="pauseSystem(false)">▶️ Resume All Access</button>
                </div>
                
                <h3 style="margin-top: 30px; margin-bottom: 15px;">Site-Specific Controls</h3>
                <div class="controls">
                    <button class="btn btn-warning" onclick="pauseSite('SITE001', true)">Pause Main Campus</button>
                    <button class="btn btn-warning" onclick="pauseSite('SITE002', true)">Pause Student Halls</button>
                    <button class="btn btn-warning" onclick="pauseSite('SITE003', true)">Pause Research Center</button>
                    <button class="btn btn-warning" onclick="pauseSite('SITE004', true)">Pause Library</button>
                </div>
                <div class="controls">
                    <button class="btn btn-success" onclick="pauseSite('SITE001', false)">Resume Main Campus</button>
                    <button class="btn btn-success" onclick="pauseSite('SITE002', false)">Resume Student Halls</button>
                    <button class="btn btn-success" onclick="pauseSite('SITE003', false)">Resume Research Center</button>
                    <button class="btn btn-success" onclick="pauseSite('SITE004', false)">Resume Library</button>
                </div>
            </div>
            
            <!-- Register Gate Tab -->
            <div id="register" class="tab-content">
                <h2 style="margin-bottom: 20px;">Register New Gate</h2>
                <form onsubmit="registerGate(event)" style="max-width: 500px;">
                    <div class="form-group">
                        <label>Tablet ID</label>
                        <input type="text" id="tablet-id" required placeholder="GATE001">
                    </div>
                    <div class="form-group">
                        <label>GPS Location</label>
                        <input type="text" id="gps-location" required placeholder="22.3193,114.1694">
                    </div>
                    <div class="form-group">
                        <label>Site</label>
                        <select id="gate-site" required>
                            <option value="SITE001">Main Campus</option>
                            <option value="SITE002">Student Halls</option>
                            <option value="SITE003">Research Center</option>
                            <option value="SITE004">Library</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary" style="width: 100%;">Register Gate</button>
                </form>
            </div>
            
            <!-- Quantum Safe HSM Tab -->
            <div id="hsm" class="tab-content">
                <h2 style="margin-bottom: 20px;">🔐 Quantum Safe HSM Console</h2>
                
                <!-- PKCS#11 Interface Section -->
                <div class="hsm-section">
                    <h3>
                        <span style="background: #4DB8A8; color: white; padding: 5px 10px; border-radius: 5px; font-size: 0.8em;">PKCS#11</span>
                        Public Key Query Interface
                    </h3>
                    <p style="color: #718096; margin-bottom: 15px;">Query HSM for user public keys via PKCS#11 interface</p>
                    
                    <div class="hsm-query-form">
                        <input type="text" id="hsm-user-id" placeholder="Enter User ID (e.g., USER001)" 
                               style="flex: 1; padding: 10px; border: 1px solid #e2e8f0; border-radius: 6px;">
                        <button class="btn btn-primary" onclick="queryPublicKey()">🔍 Query Public Key</button>
                    </div>
                    
                    <div id="hsm-query-result" style="display: none;">
                        <h4 style="margin-bottom: 10px; color: #2d3748;">Query Result:</h4>
                        <div class="hsm-result" id="hsm-result-content"></div>
                    </div>
                </div>
                
                <!-- Signature Logs Section -->
                <div class="hsm-section">
                    <h3>
                        <span style="background: #48bb78; color: white; padding: 5px 10px; border-radius: 5px; font-size: 0.8em;">LOGS</span>
                        Signature Request & Verification Log
                    </h3>
                    <p style="color: #718096; margin-bottom: 15px;">Real-time log of HSM signature operations</p>
                    
                    <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                        <button class="btn btn-success" onclick="loadSignatureLogs()">🔄 Refresh Logs</button>
                        <select id="log-filter" onchange="loadSignatureLogs()" 
                                style="padding: 10px; border: 1px solid #e2e8f0; border-radius: 6px;">
                            <option value="all">All Operations</option>
                            <option value="sign">Sign Only</option>
                            <option value="verify">Verify Only</option>
                            <option value="success">Success Only</option>
                            <option value="failed">Failed Only</option>
                        </select>
                    </div>
                    
                    <div id="signature-logs-container" style="max-height: 500px; overflow-y: auto;">
                        <!-- Signature logs will be loaded here -->
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <button class="refresh-btn" onclick="refreshData()" title="Refresh Data">↻</button>
    
    <script>
        const API_BASE = 'http://localhost:5000';
        let currentTabScroll = 0;
        
        function scrollTabs(direction) {
            const wrapper = document.getElementById('tabs-wrapper');
            const tabs = document.querySelectorAll('.tab');
            const tabWidth = tabs[0].offsetWidth;
            
            currentTabScroll += direction;
            const maxScroll = tabs.length - 4; // Show 4 tabs at a time
            
            if (currentTabScroll < 0) currentTabScroll = 0;
            if (currentTabScroll > maxScroll) currentTabScroll = maxScroll;
            
            wrapper.style.transform = `translateX(-${currentTabScroll * tabWidth}px)`;
        }
        
        function showTab(tabName) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            event.target.closest('.tab').classList.add('active');
            document.getElementById(tabName).classList.add('active');
            
            if (tabName === 'dashboard') loadDashboard();
            if (tabName === 'pending') loadPendingPasses();
            if (tabName === 'all-passes') loadAllPasses();
            if (tabName === 'logs') loadAuditLogs();
            if (tabName === 'hsm') loadSignatureLogs();
        }
        
        async function loadDashboard() {
            try {
                const [statsRes, statusRes] = await Promise.all([
                    fetch(`${API_BASE}/admin/statistics`),
                    fetch(`${API_BASE}/admin/system-status`)
                ]);
                
                const stats = await statsRes.json();
                const status = await statusRes.json();
                
                // Update system status banner
                const banner = document.getElementById('system-status-banner');
                if (status.global_pause) {
                    banner.className = 'system-status system-paused';
                    banner.textContent = '⏸️ System Paused';
                } else {
                    banner.className = 'system-status system-active';
                    banner.textContent = '✅ System Active';
                }
                
                // Update stats cards
                document.getElementById('stats-container').innerHTML = `
                    <div class="stat-card">
                        <h3>${stats.total_users || 0}</h3>
                        <p>Total Users</p>
                    </div>
                    <div class="stat-card">
                        <h3>${stats.total_gates || 0}</h3>
                        <p>Total Gates</p>
                    </div>
                    <div class="stat-card">
                        <h3>${stats.passes_in_process || 0}</h3>
                        <p>Pending Requests</p>
                    </div>
                    <div class="stat-card">
                        <h3>${stats.passes_pass || 0}</h3>
                        <p>Approved Passes</p>
                    </div>
                    <div class="stat-card">
                        <h3>${stats.passes_used || 0}</h3>
                        <p>Used Passes</p>
                    </div>
                    <div class="stat-card">
                        <h3>${stats.passes_revoked || 0}</h3>
                        <p>Revoked Passes</p>
                    </div>
                `;
                
                // Update site groups
                if (stats.by_site) {
                    const siteNames = {
                        'SITE001': 'Main Campus',
                        'SITE002': 'Student Halls',
                        'SITE003': 'Research Center',
                        'SITE004': 'Library'
                    };
                    
                    let html = '<h2 style="margin-top: 30px; margin-bottom: 20px;">Site Statistics</h2>';
                    for (const [siteId, siteStats] of Object.entries(stats.by_site)) {
                        const isPaused = status.site_pauses[siteId] || false;
                        html += `
                            <div class="site-group">
                                <h3>${siteNames[siteId]} ${isPaused ? '⏸️ (Paused)' : '✅'}</h3>
                                <div class="site-stats">
                                    <div class="site-stat">
                                        <div class="number">${siteStats.approved}</div>
                                        <div class="label">Approved</div>
                                    </div>
                                    <div class="site-stat">
                                        <div class="number">${siteStats.requested}</div>
                                        <div class="label">Pending</div>
                                    </div>
                                    <div class="site-stat">
                                        <div class="number">${siteStats.used}</div>
                                        <div class="label">Used</div>
                                    </div>
                                    <div class="site-stat">
                                        <div class="number">${siteStats.revoked}</div>
                                        <div class="label">Revoked</div>
                                    </div>
                                </div>
                            </div>
                        `;
                    }
                    document.getElementById('site-groups-container').innerHTML = html;
                }
            } catch (err) {
                console.error('Error loading dashboard:', err);
            }
        }
        
        async function loadPendingPasses() {
            try {
                const res = await fetch(`${API_BASE}/admin/pending-passes`);
                const data = await res.json();
                
                const tbody = document.getElementById('pending-tbody');
                tbody.innerHTML = data.passes.map(pass => `
                    <tr>
                        <td>${pass.pass_id}</td>
                        <td>${pass.iamsmart_id}</td>
                        <td>${pass.site_id}</td>
                        <td>${pass.purpose_id}</td>
                        <td>${new Date(pass.visit_date_time).toLocaleString()}</td>
                        <td>${new Date(pass.created_timestamp).toLocaleString()}</td>
                        <td>
                            <button class="btn btn-success" style="padding: 6px 12px; margin-right: 5px;" onclick="approvePass('${pass.pass_id}')">✓ Approve</button>
                            <button class="btn btn-danger" style="padding: 6px 12px;" onclick="rejectPass('${pass.pass_id}')">✗ Reject</button>
                        </td>
                    </tr>
                `).join('');
            } catch (err) {
                console.error('Error loading pending passes:', err);
            }
        }
        
        async function loadAllPasses() {
            try {
                const status = document.getElementById('status-filter').value;
                const site = document.getElementById('site-filter').value;
                
                let url = `${API_BASE}/admin/all-passes?`;
                if (status) url += `status=${status}&`;
                if (site) url += `site_id=${site}`;
                
                const res = await fetch(url);
                const data = await res.json();
                
                const tbody = document.getElementById('all-passes-tbody');
                tbody.innerHTML = data.passes.map(pass => `
                    <tr>
                        <td>${pass.pass_id}</td>
                        <td>${pass.iamsmart_id}</td>
                        <td>${pass.site_id}</td>
                        <td>${pass.purpose_id}</td>
                        <td><span class="status status-${pass.status.toLowerCase().replace(' ', '')}">${pass.status}</span></td>
                        <td>${new Date(pass.visit_date_time).toLocaleString()}</td>
                        <td>
                            ${pass.status === 'Pass' && !pass.revoked_flag ? 
                                `<button class="btn btn-danger" style="padding: 6px 12px;" onclick="revokePass('${pass.pass_id}')">🚫 Revoke</button>` 
                                : '-'}
                        </td>
                    </tr>
                `).join('');
            } catch (err) {
                console.error('Error loading all passes:', err);
            }
        }
        
        async function loadAuditLogs() {
            try {
                const res = await fetch(`${API_BASE}/admin/audit-logs?limit=100`);
                const data = await res.json();
                
                const container = document.getElementById('logs-container');
                container.innerHTML = data.logs.map(log => {
                    let className = 'log-entry';
                    if (log.result && log.result.includes('SUCCESS') || log.result === 'PASS') className += ' log-success';
                    else if (log.result && (log.result.includes('FAILED') || log.result === 'REVOKED')) className += ' log-error';
                    else if (log.result && log.result.includes('PAUSED')) className += ' log-warning';
                    
                    return `
                        <div class="${className}">
                            <strong>[${new Date(log.timestamp).toLocaleString()}]</strong>
                            ${log.event_type.toUpperCase()} - ${log.result || 'N/A'}
                            ${log.user_id ? ` | User: ${log.user_id}` : ''}
                            ${log.gate_id ? ` | Gate: ${log.gate_id}` : ''}
                            ${log.pass_id ? ` | Pass: ${log.pass_id}` : ''}
                            ${log.details ? ` | ${log.details}` : ''}
                        </div>
                    `;
                }).join('');
            } catch (err) {
                console.error('Error loading audit logs:', err);
            }
        }
        
        async function approvePass(passId) {
            if (!confirm(`Approve pass ${passId}?`)) return;
            try {
                const res = await fetch(`${API_BASE}/admin/approve-pass/${passId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ expiry_hours: 24 })
                });
                const data = await res.json();
                alert(data.message);
                loadPendingPasses();
                loadDashboard();
            } catch (err) {
                alert('Error approving pass: ' + err.message);
            }
        }
        
        async function rejectPass(passId) {
            const reason = prompt('Reason for rejection:');
            if (!reason) return;
            try {
                const res = await fetch(`${API_BASE}/admin/reject-pass/${passId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ reason })
                });
                const data = await res.json();
                alert(data.message);
                loadPendingPasses();
                loadDashboard();
            } catch (err) {
                alert('Error rejecting pass: ' + err.message);
            }
        }
        
        async function revokePass(passId) {
            const reason = prompt('Reason for revocation:');
            if (!reason) return;
            try {
                const res = await fetch(`${API_BASE}/admin/revoke-pass/${passId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ reason })
                });
                const data = await res.json();
                alert(data.message);
                loadAllPasses();
                loadDashboard();
            } catch (err) {
                alert('Error revoking pass: ' + err.message);
            }
        }
        
        async function pauseSystem(paused) {
            if (!confirm(`${paused ? 'Pause' : 'Resume'} entire system?`)) return;
            try {
                const res = await fetch(`${API_BASE}/admin/pause-system`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ paused })
                });
                const data = await res.json();
                alert(data.message);
                loadDashboard();
            } catch (err) {
                alert('Error: ' + err.message);
            }
        }
        
        async function pauseSite(siteId, paused) {
            try {
                const res = await fetch(`${API_BASE}/admin/pause-site`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ site_id: siteId, paused })
                });
                const data = await res.json();
                alert(data.message);
                loadDashboard();
            } catch (err) {
                alert('Error: ' + err.message);
            }
        }
        
        async function registerGate(event) {
            event.preventDefault();
            const tabletId = document.getElementById('tablet-id').value;
            const gpsLocation = document.getElementById('gps-location').value;
            const siteId = document.getElementById('gate-site').value;
            
            try {
                const res = await fetch(`${API_BASE}/admin/register-gate`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ tablet_id: tabletId, gps_location: gpsLocation, site_id: siteId })
                });
                const data = await res.json();
                alert(data.message);
                document.getElementById('tablet-id').value = '';
                document.getElementById('gps-location').value = '';
            } catch (err) {
                alert('Error registering gate: ' + err.message);
            }
        }
        
        function refreshData() {
            const activeTab = document.querySelector('.tab.active').textContent;
            if (activeTab.includes('Dashboard')) loadDashboard();
            else if (activeTab.includes('Pending')) loadPendingPasses();
            else if (activeTab.includes('All Passes')) loadAllPasses();
            else if (activeTab.includes('Audit')) loadAuditLogs();
            else if (activeTab.includes('HSM')) loadSignatureLogs();
        }
        
        async function queryPublicKey() {
            const userId = document.getElementById('hsm-user-id').value.trim();
            if (!userId) {
                alert('Please enter a User ID');
                return;
            }
            
            try {
                // Query HSM for public key
                const res = await fetch(`${API_BASE}/admin/hsm/query-public-key/${userId}`);
                const data = await res.json();
                
                const resultDiv = document.getElementById('hsm-query-result');
                const contentDiv = document.getElementById('hsm-result-content');
                
                if (data.success) {
                    contentDiv.innerHTML = `
                        <div style="margin-bottom: 10px;"><strong>User ID:</strong> ${data.user_id}</div>
                        <div style="margin-bottom: 10px;"><strong>Algorithm:</strong> ${data.algorithm}</div>
                        <div style="margin-bottom: 10px;"><strong>Key Size:</strong> ${data.key_size} bits</div>
                        <div style="margin-bottom: 10px;"><strong>Created:</strong> ${new Date(data.created_at).toLocaleString()}</div>
                        <div style="margin-bottom: 10px;"><strong>Status:</strong> <span style="color: #48bb78; font-weight: 600;">✓ ACTIVE</span></div>
                        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #e2e8f0;">
                            <strong>Public Key (PEM):</strong>
                            <pre style="background: #2d3748; color: #48bb78; padding: 10px; border-radius: 4px; margin-top: 5px; overflow-x: auto;">${data.public_key}</pre>
                        </div>
                    `;
                    resultDiv.style.display = 'block';
                } else {
                    contentDiv.innerHTML = `<div style="color: #f56565;"><strong>Error:</strong> ${data.message || 'Public key not found'}</div>`;
                    resultDiv.style.display = 'block';
                }
            } catch (err) {
                alert('Error querying HSM: ' + err.message);
            }
        }
        
        async function loadSignatureLogs() {
            try {
                const filter = document.getElementById('log-filter').value;
                const res = await fetch(`${API_BASE}/admin/hsm/signature-logs?filter=${filter}`);
                const data = await res.json();
                
                const container = document.getElementById('signature-logs-container');
                
                if (data.logs && data.logs.length > 0) {
                    container.innerHTML = data.logs.map(log => {
                        const isSuccess = log.status === 'SUCCESS' || log.status === 'VERIFIED';
                        const isFailed = log.status === 'FAILED' || log.status === 'INVALID';
                        const logClass = isFailed ? 'signature-log failed' : 'signature-log';
                        
                        return `
                            <div class="${logClass}">
                                <div style="display: flex; justify-content: space-between; align-items: start;">
                                    <div style="flex: 1;">
                                        <div style="margin-bottom: 5px;">
                                            <span style="background: ${isSuccess ? '#48bb78' : '#f56565'}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.85em; font-weight: 600;">
                                                ${log.operation.toUpperCase()}
                                            </span>
                                            <span style="margin-left: 10px; color: #4DB8A8; font-weight: 600;">${isSuccess ? '✓' : '✗'} ${log.status}</span>
                                        </div>
                                        <div style="color: #4a5568; margin-bottom: 3px;">
                                            <strong>User:</strong> <span class="user-id">${log.user_id}</span>
                                            ${log.pass_id ? ` | <strong>Pass:</strong> ${log.pass_id}` : ''}
                                        </div>
                                        <div style="color: #718096; font-size: 0.85em;">
                                            ${log.details || 'No additional details'}
                                        </div>
                                    </div>
                                    <div class="timestamp">${new Date(log.timestamp).toLocaleString()}</div>
                                </div>
                            </div>
                        `;
                    }).join('');
                } else {
                    container.innerHTML = '<div style="text-align: center; color: #718096; padding: 20px;">No signature logs available</div>';
                }
            } catch (err) {
                console.error('Error loading signature logs:', err);
            }
        }
        
        // Initial load
        loadDashboard();
        
        // Auto-refresh every 10 seconds
        setInterval(refreshData, 10000);
    </script>
</body>
</html>
"""

def create_admin_app():
    """Create admin console Flask app"""
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return render_template_string(ADMIN_CONSOLE_HTML)
    
    return app

if __name__ == '__main__':
    app = create_admin_app()
    app.run(host='0.0.0.0', port=5001, debug=True)
