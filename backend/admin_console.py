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
            bottom: 80px;
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
            z-index: 100;
        }
        .refresh-btn:hover {
            transform: scale(1.1) rotate(180deg);
        }
        .footer-bar {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background: rgba(29, 44, 42, 0.5);
            backdrop-filter: blur(10px);
            color: white;
            text-align: center;
            padding: 15px 20px;
            font-size: 0.9em;
            z-index: 99;
            border-top: 1px solid rgba(77, 184, 168, 0.3);
        }
        .footer-bar p {
            margin: 0;
            opacity: 0.9;
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
        .hsm-grid {
            display: flex;
            flex-direction: column;
            gap: 20px;
            margin-top: 20px;
        }
        .hsm-logs-panel {
            background: #f7fafc;
            border: 2px solid #4DB8A8;
            border-radius: 10px;
            padding: 15px;
            display: flex;
            flex-direction: column;
        }
        .hsm-qr-panel {
            background: #f7fafc;
            border: 2px solid #4DB8A8;
            border-radius: 10px;
            padding: 15px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .algorithm-selector {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            padding: 10px;
            background: white;
            border-radius: 8px;
            flex-wrap: wrap;
            justify-content: center;
        }
        .algorithm-tag {
            padding: 12px 24px;
            border: 3px solid #e2e8f0;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 600;
            font-size: 1em;
            background: linear-gradient(145deg, #ffffff, #f0f0f0);
            color: #4a5568;
            box-shadow: 3px 3px 6px rgba(0, 0, 0, 0.1), -3px -3px 6px rgba(255, 255, 255, 0.8);
            position: relative;
        }
        .algorithm-tag:hover {
            transform: translateY(-1px);
            box-shadow: 4px 4px 8px rgba(0, 0, 0, 0.15), -4px -4px 8px rgba(255, 255, 255, 0.9);
        }
        .algorithm-tag:active {
            transform: translateY(1px);
            box-shadow: inset 2px 2px 4px rgba(0, 0, 0, 0.2), inset -2px -2px 4px rgba(255, 255, 255, 0.7);
        }
        .algorithm-tag.active {
            background: linear-gradient(145deg, #34c759, #28a745);
            color: white;
            border-color: #34c759;
            box-shadow: 0 0 20px rgba(52, 199, 89, 0.6), inset 0 2px 4px rgba(255, 255, 255, 0.3);
            transform: translateY(1px);
        }
        .algorithm-tag.active::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 90%;
            height: 90%;
            border-radius: 20px;
            background: radial-gradient(circle, rgba(255, 255, 255, 0.3) 0%, transparent 70%);
            pointer-events: none;
        }
        .algorithm-tag.pqc {
            background: linear-gradient(145deg, #f0f0f0, #e0e0e0);
            color: #4a5568;
            border-color: #e2e8f0;
        }
        .algorithm-tag.pqc.active {
            background: linear-gradient(145deg, #8b5cf6, #7c3aed);
            color: white;
            border-color: #8b5cf6;
            box-shadow: 0 0 20px rgba(139, 92, 246, 0.6), inset 0 2px 4px rgba(255, 255, 255, 0.3);
        }
        .algorithm-info {
            background: #f7fafc;
            padding: 12px;
            border-radius: 8px;
            margin-top: 15px;
            width: 100%;
            border-left: 4px solid #4DB8A8;
        }
        .algorithm-info.dummy {
            border-left-color: #f59e0b;
            background: #fffbeb;
        }
        .payload-log-item {
            background: white;
            padding: 12px;
            margin: 8px 0;
            border-radius: 6px;
            cursor: pointer;
            border: 2px solid transparent;
            transition: all 0.2s;
        }
        .payload-log-item:hover {
            border-color: #4DB8A8;
            box-shadow: 0 2px 8px rgba(77, 184, 168, 0.2);
        }
        .payload-log-item.selected {
            border-color: #4DB8A8;
            background: #e6fffa;
        }
        .payload-scroll {
            max-height: 400px;
            overflow-y: auto;
            padding-right: 10px;
        }
        .payload-scroll::-webkit-scrollbar {
            width: 8px;
        }
        .payload-scroll::-webkit-scrollbar-track {
            background: #e2e8f0;
            border-radius: 4px;
        }
        .payload-scroll::-webkit-scrollbar-thumb {
            background: #4DB8A8;
            border-radius: 4px;
        }
        .payload-scroll::-webkit-scrollbar-thumb:hover {
            background: #3a9d8f;
        }
        .qr-display-area {
            background: white;
            padding: 20px;
            border-radius: 10px;
            min-height: 300px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            width: 100%;
        }
        .qr-placeholder {
            color: #a0aec0;
            text-align: center;
            font-size: 1em;
        }
        #hsm-qr-code {
            margin: 15px 0;
            padding: 15px;
            border-radius: 12px;
        }
        #hsm-qr-code.rsa-qr {
            border: 4px solid #34c759;
            box-shadow: 0 0 15px rgba(52, 199, 89, 0.3);
        }
        #hsm-qr-code.pqc-qr {
            border: 4px solid #8b5cf6;
            box-shadow: 0 0 15px rgba(139, 92, 246, 0.3);
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
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
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
                
                <div class="hsm-grid">
                    <!-- Top Section: JSON Payload Logs -->
                    <div class="hsm-logs-panel">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                            <h3 style="margin: 0;">
                                <span style="background: #4DB8A8; color: white; padding: 5px 10px; border-radius: 5px; font-size: 0.8em;">LOGS</span>
                                QR Payloads History
                            </h3>
                            <button class="btn btn-success" onclick="loadQRPayloads()" style="padding: 8px 15px; font-size: 0.85em;">
                                🔄 Refresh
                            </button>
                        </div>
                        <p style="color: #718096; margin-bottom: 15px; font-size: 0.9em;">
                            All historical QR payloads from database - Select to display QR code
                        </p>
                        
                        <div class="payload-scroll" id="payload-logs-container">
                            <!-- Payload logs will be loaded here -->
                            <div style="text-align: center; color: #a0aec0; padding: 40px 20px;">
                                <div style="font-size: 2em; margin-bottom: 10px;">📦</div>
                                <div>Loading historical QR payloads...</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Bottom Section: QR Code Display -->
                    <div class="hsm-qr-panel">
                        <h3 style="margin-bottom: 15px;">
                            <span style="background: #48bb78; color: white; padding: 5px 10px; border-radius: 5px; font-size: 0.8em;">QR CODE</span>
                            Visual Display
                        </h3>
                        
                        <!-- Algorithm Selector -->
                        <div class="algorithm-selector">
                            <div class="algorithm-tag active" onclick="selectAlgorithm('RSA')" id="algo-RSA">
                                🔒 RSA-2048
                            </div>
                            <div class="algorithm-tag pqc" onclick="selectAlgorithm('FALCON')" id="algo-FALCON">
                                🦅 FALCON-512
                            </div>
                            <div class="algorithm-tag pqc" onclick="selectAlgorithm('DILITHIUM')" id="algo-DILITHIUM">
                                💎 Dilithium2
                            </div>
                            <div class="algorithm-tag pqc" onclick="selectAlgorithm('SPHINCS')" id="algo-SPHINCS">
                                🌳 SPHINCS+-128s
                            </div>
                        </div>
                        
                        <div class="qr-display-area">
                            <div id="hsm-qr-placeholder" class="qr-placeholder">
                                <div style="font-size: 3em; margin-bottom: 15px;">📱</div>
                                <div style="font-size: 1.1em; font-weight: 600;">Select a payload to view QR code</div>
                                <div style="margin-top: 8px; font-size: 0.9em;">Click on any log entry on the left</div>
                            </div>
                            <div id="hsm-qr-code" style="display: none;"></div>
                            <div id="hsm-algorithm-info" style="display: none;"></div>
                            <div id="hsm-qr-details" style="display: none; margin-top: 20px; width: 100%; text-align: left;">
                                <div style="background: #f7fafc; padding: 15px; border-radius: 8px; border-left: 4px solid #4DB8A8;">
                                    <div style="margin-bottom: 10px; font-weight: 600; color: #2d3748;">Payload Details:</div>
                                    <div style="font-family: 'Courier New', monospace; font-size: 0.85em; color: #4a5568;">
                                        <div style="margin-bottom: 5px;"><strong>Pass ID:</strong> <span id="qr-detail-pass"></span></div>
                                        <div style="margin-bottom: 5px;"><strong>Timestamp:</strong> <span id="qr-detail-timestamp"></span></div>
                                        <div style="margin-bottom: 5px; word-break: break-all;"><strong>Signature:</strong> <span id="qr-detail-signature"></span></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <button class="refresh-btn" onclick="refreshData()" title="Refresh Data">↻</button>
    
    <div class="footer-bar">
        <p>© 2025-2026 Real Matter Technology Limited.</p>
    </div>
    
    <script>
        const API_BASE = 'https://iamsmartgate-poc.onrender.com';
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
            if (tabName === 'hsm') loadQRPayloads();
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
            else if (activeTab.includes('HSM')) loadQRPayloads();
        }
        
        let selectedPayload = null;
        let qrCodeInstance = null;
        let selectedAlgorithm = 'RSA';
        
        const algorithmSpecs = {
            'RSA': {
                name: 'RSA-2048 with PSS Padding',
                shortName: 'RSA-2048 PSS',
                signatureSize: 256,
                payloadSize: 430,
                qrVersion: 10,
                qrBlocks: 57,
                totalDots: 3249,
                description: 'Classical RSA signature (current implementation)',
                isPQC: false,
                canFitInQR: true
            },
            'FALCON': {
                name: 'FALCON-512',
                shortName: 'FALCON-512',
                signatureSize: 666,
                payloadSize: 950,
                qrVersion: 21,
                qrBlocks: 101,
                totalDots: 10201,
                description: 'NIST PQC - Compact lattice-based signature',
                isPQC: true,
                canFitInQR: true,
                warning: 'Large QR code - may be difficult to scan'
            },
            'DILITHIUM': {
                name: 'CRYSTALS-Dilithium2',
                shortName: 'Dilithium2',
                signatureSize: 2420,
                payloadSize: 3290,
                qrVersion: '40+',
                qrBlocks: 177,
                totalDots: 31329,
                description: 'NIST PQC - Module-lattice based signature',
                isPQC: true,
                canFitInQR: false,
                warning: '❌ EXCEEDS QR CAPACITY - Cannot fit in standard QR code (max ~2,953 bytes)'
            },
            'SPHINCS': {
                name: 'SPHINCS+-128s',
                shortName: 'SPHINCS+-128s',
                signatureSize: 7856,
                payloadSize: 10540,
                qrVersion: 'N/A',
                qrBlocks: 0,
                totalDots: 0,
                description: 'NIST PQC - Hash-based stateless signature',
                isPQC: true,
                canFitInQR: false,
                warning: '❌ FAR EXCEEDS QR CAPACITY - Needs >10KB (3.5× maximum QR capacity)'
            }
        };
        
        function selectAlgorithm(algo) {
            selectedAlgorithm = algo;
            
            // Update active state
            document.querySelectorAll('.algorithm-tag').forEach(tag => {
                tag.classList.remove('active');
            });
            document.getElementById('algo-' + algo).classList.add('active');
            
            // Re-display QR code with new algorithm if a payload is selected
            if (selectedPayload) {
                displayQRCode(selectedPayload, selectedPayload.p, selectedPayload.t, selectedPayload.s);
            }
        }
        
        async function loadQRPayloads() {
            try {
                // Always fetch all passes from database for historical data
                const res = await fetch(`${API_BASE}/admin/all-passes`);
                const data = await res.json();
                
                const container = document.getElementById('payload-logs-container');
                
                if (data.passes && data.passes.length > 0) {
                    // Show ALL passes that are approved or used
                    // This includes all historical records from the database
                    const passesWithQR = data.passes.filter(pass => {
                        // Show if status is 'Pass', 'Used', or has been used
                        return (pass.status === 'Pass' || pass.status === 'Used' || pass.used_flag === true);
                    });
                    
                    if (passesWithQR.length > 0) {
                        container.innerHTML = passesWithQR.map((pass, index) => {
                            // Use actual timestamp data from database
                            const timestamp = pass.approved_timestamp || pass.created_timestamp || new Date().toISOString();
                            const signature = pass.qr_signature || 'No signature generated yet';
                            const hasSignature = pass.qr_signature && pass.qr_signature !== null;
                            const statusBadge = pass.used_flag ? '✓ USED' : pass.status;
                            const statusColor = pass.used_flag ? '#48bb78' : '#4DB8A8';
                            
                            return `
                                <div class="payload-log-item" onclick="selectPayload('${pass.pass_id}', '${timestamp}', \`${signature}\`, ${index})">
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                        <div style="font-weight: 600; color: #2d3748;">
                                            #${index + 1} - ${pass.pass_id}
                                        </div>
                                        <div style="font-size: 0.85em; color: #718096;">
                                            ${new Date(timestamp).toLocaleString()}
                                        </div>
                                    </div>
                                    <div style="font-family: 'Courier New', monospace; font-size: 0.8em; color: #4a5568; margin-bottom: 5px;">
                                        <strong>Pass ID:</strong> ${pass.pass_id}
                                    </div>
                                    <div style="font-family: 'Courier New', monospace; font-size: 0.8em; color: #4a5568; margin-bottom: 5px;">
                                        <strong>Timestamp:</strong> ${timestamp}
                                    </div>
                                    <div style="font-family: 'Courier New', monospace; font-size: 0.75em; color: ${hasSignature ? '#718096' : '#f56565'}; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                                        <strong>Signature:</strong> ${hasSignature ? signature.substring(0, 50) + '...' : '⚠️ ' + signature}
                                    </div>
                                    <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center;">
                                        <span style="background: #4DB8A8; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.75em;">
                                            ${pass.iamsmart_id || 'Unknown User'}
                                        </span>
                                        <span style="background: ${statusColor}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.75em;">
                                            ${statusBadge}
                                        </span>
                                    </div>
                                </div>
                            `;
                        }).join('');
                    } else {
                        container.innerHTML = `
                            <div style="text-align: center; color: #a0aec0; padding: 40px 20px;">
                                <div style="font-size: 2em; margin-bottom: 10px;">📭</div>
                                <div>No QR payloads in database</div>
                                <div style="font-size: 0.85em; margin-top: 5px;">Historical QR signatures will appear here</div>
                            </div>
                        `;
                    }
                } else {
                    container.innerHTML = `
                        <div style="text-align: center; color: #a0aec0; padding: 40px 20px;">
                            <div style="font-size: 2em; margin-bottom: 10px;">📭</div>
                            <div>No passes available in database</div>
                        </div>
                    `;
                }
            } catch (err) {
                console.error('Error loading QR payloads:', err);
                document.getElementById('payload-logs-container').innerHTML = `
                    <div style="text-align: center; color: #f56565; padding: 40px 20px;">
                        <div style="font-size: 2em; margin-bottom: 10px;">⚠️</div>
                        <div>Error loading payloads from database</div>
                        <div style="font-size: 0.85em; margin-top: 5px;">${err.message}</div>
                    </div>
                `;
            }
        }
        
        function selectPayload(passId, timestamp, signature, index) {
            // Remove previous selection
            document.querySelectorAll('.payload-log-item').forEach(item => {
                item.classList.remove('selected');
            });
            
            // Add selection to clicked item
            document.querySelectorAll('.payload-log-item')[index].classList.add('selected');
            
            // Store selected payload
            selectedPayload = {
                p: passId,
                t: timestamp,
                s: signature
            };
            
            // Display QR code
            displayQRCode(selectedPayload, passId, timestamp, signature);
        }
        
        function displayQRCode(payload, passId, timestamp, signature) {
            // Hide placeholder, show QR code
            document.getElementById('hsm-qr-placeholder').style.display = 'none';
            document.getElementById('hsm-qr-code').style.display = 'block';
            document.getElementById('hsm-qr-details').style.display = 'block';
            document.getElementById('hsm-algorithm-info').style.display = 'block';
            
            // Clear previous QR code
            const qrContainer = document.getElementById('hsm-qr-code');
            qrContainer.innerHTML = '';
            
            // Check if signature exists
            const hasSignature = signature && signature !== 'No signature generated yet';
            
            if (!hasSignature) {
                // Show message if no signature
                qrContainer.innerHTML = `
                    <div style="color: #f59e0b; text-align: center; padding: 40px;">
                        <div style="font-size: 3em; margin-bottom: 15px;">⚠️</div>
                        <div style="font-size: 1.1em; font-weight: 600; margin-bottom: 10px;">No QR Signature Available</div>
                        <div style="font-size: 0.9em; color: #718096;">This pass was approved but QR code was never generated by the user</div>
                    </div>
                `;
                
                // Update details
                document.getElementById('qr-detail-pass').textContent = passId;
                document.getElementById('qr-detail-timestamp').textContent = timestamp;
                document.getElementById('qr-detail-signature').textContent = '⚠️ Not generated';
                document.getElementById('hsm-algorithm-info').innerHTML = '';
                return;
            }
            
            const algo = algorithmSpecs[selectedAlgorithm];
            let actualSignature;
            
            // Set border style based on algorithm type (after algo is defined)
            qrContainer.className = algo.isPQC ? 'pqc-qr' : 'rsa-qr';
            
            if (selectedAlgorithm === 'RSA') {
                // Use real signature for RSA - optimize for smallest QR code
                // Convert hex signature to base64 for 32% size reduction
                actualSignature = hexToBase64(signature);
                
                // Use compact JSON with single-char keys
                const qrPayload = JSON.stringify({
                    p: passId,
                    t: timestamp,
                    s: actualSignature
                });
                
                // Generate optimized QR code for RSA with Low error correction
                try {
                    new QRCode(qrContainer, {
                        text: qrPayload,
                        width: 300,
                        height: 300,
                        colorDark: "#000000",
                        colorLight: "#ffffff",
                        correctLevel: QRCode.CorrectLevel.L  // Low (7%) - smallest QR code
                    });
                    // Green border is applied via CSS class 'rsa-qr'
                } catch (error) {
                    console.error('QR generation error:', error);
                    qrContainer.innerHTML = `
                        <div style="color: #f56565; text-align: center; padding: 20px;">
                            <div style="font-size: 2em; margin-bottom: 10px;">⚠️</div>
                            <div>Failed to generate QR code</div>
                            <div style="font-size: 0.85em; margin-top: 5px;">${error.message}</div>
                        </div>
                    `;
                }
            } else {
                // Generate dummy signature for PQC algorithms
                actualSignature = generateDummySignature(algo.signatureSize);
                
                // Check if algorithm can fit in QR code
                if (!algo.canFitInQR) {
                    // Show error message for algorithms that can't fit
                    qrContainer.innerHTML = `
                        <div style="color: #f56565; text-align: center; padding: 40px; max-width: 500px;">
                            <div style="font-size: 3em; margin-bottom: 15px;">⚠️</div>
                            <div style="font-size: 1.2em; font-weight: 600; margin-bottom: 10px; color: #dc2626;">Cannot Generate QR Code</div>
                            <div style="font-size: 0.95em; color: #4a5568; line-height: 1.6;">${algo.warning}</div>
                            <div style="margin-top: 20px; padding: 15px; background: #fee2e2; border-radius: 8px; font-size: 0.85em; text-align: left;">
                                <strong>Technical Details:</strong><br>
                                • Signature size: ${algo.signatureSize} bytes<br>
                                • Estimated payload: ~${algo.payloadSize} bytes<br>
                                • QR Version 40 max capacity: ~2,953 bytes (Low error correction)<br>
                                • This algorithm requires ${(algo.payloadSize / 2953).toFixed(1)}× the maximum QR capacity
                            </div>
                        </div>
                    `;
                } else {
                    // Create scaled dummy QR code for PQC algorithms that CAN fit
                    // Use accurate block counts based on actual QR versions
                    const scaledBlocks = algo.qrBlocks;
                    
                    // Determine canvas size and block size
                    let canvasSize, blockSize;
                    if (selectedAlgorithm === 'FALCON') {
                        // Version 21: 101×101 blocks
                        canvasSize = 600;
                        blockSize = Math.floor(canvasSize / scaledBlocks);
                    } else if (selectedAlgorithm === 'DILITHIUM') {
                        // Exceeds Version 40: 177×177 blocks (theoretical)
                        canvasSize = 700;
                        blockSize = Math.floor(canvasSize / scaledBlocks);
                    }
                    
                    const canvas = document.createElement('canvas');
                    canvas.width = canvasSize;
                    canvas.height = canvasSize;
                    const ctx = canvas.getContext('2d');
                    
                    // White background
                    ctx.fillStyle = '#ffffff';
                    ctx.fillRect(0, 0, canvasSize, canvasSize);
                    
                    // Generate QR-like pattern with accurate block counts
                    for (let y = 0; y < scaledBlocks; y++) {
                        for (let x = 0; x < scaledBlocks; x++) {
                            if (Math.random() > 0.5) {
                                ctx.fillStyle = '#000000';
                                ctx.fillRect(x * blockSize, y * blockSize, blockSize, blockSize);
                            }
                        }
                    }
                    
                    // Add corner markers (scaled appropriately)
                    const markerSize = Math.max(5, Math.floor(7 * blockSize / 12));
                    const drawCornerMarker = (x, y) => {
                        ctx.fillStyle = '#000000';
                        ctx.fillRect(x * blockSize, y * blockSize, markerSize * blockSize, markerSize * blockSize);
                        ctx.fillStyle = '#ffffff';
                        ctx.fillRect((x + 1) * blockSize, (y + 1) * blockSize, (markerSize - 2) * blockSize, (markerSize - 2) * blockSize);
                        ctx.fillStyle = '#000000';
                        ctx.fillRect((x + 2) * blockSize, (y + 2) * blockSize, (markerSize - 4) * blockSize, (markerSize - 4) * blockSize);
                    };
                    
                    drawCornerMarker(0, 0);
                    drawCornerMarker(scaledBlocks - markerSize, 0);
                    drawCornerMarker(0, scaledBlocks - markerSize);
                    
                    // Add border color based on algorithm type
                    ctx.strokeStyle = '#8b5cf6'; // Purple for PQC
                    ctx.lineWidth = 4;
                    ctx.strokeRect(0, 0, canvasSize, canvasSize);
                    
                    qrContainer.appendChild(canvas);
                }
            }
            
            // Show algorithm info with prominent size indicator
            const isDummy = selectedAlgorithm !== 'RSA';
            const infoClass = isDummy ? 'algorithm-info dummy' : 'algorithm-info';
            const sizeMultiplier = (algo.signatureSize / 256).toFixed(2);
            const sizeColor = isDummy ? '#f59e0b' : '#4DB8A8';
            
            const warningColor = !algo.canFitInQR ? '#dc2626' : (algo.warning ? '#f59e0b' : sizeColor);
            const statusIcon = !algo.canFitInQR ? '❌' : (algo.warning ? '⚠️' : (isDummy ? '⚠️' : '✓'));
            
            document.getElementById('hsm-algorithm-info').innerHTML = `
                <div class="${infoClass}">
                    ${!algo.canFitInQR ? `<div style="color: #dc2626; font-weight: 600; margin-bottom: 8px;">${statusIcon} CANNOT FIT IN QR CODE</div>` : (isDummy ? `<div style="color: #f59e0b; font-weight: 600; margin-bottom: 8px;">${statusIcon} DEMONSTRATION - Simulated PQC Signature</div>` : '<div style="color: #4DB8A8; font-weight: 600; margin-bottom: 8px;">✓ OPTIMIZED - Base64 encoding + Low error correction</div>')}
                    <div style="font-weight: 600; color: #2d3748; margin-bottom: 5px;">Algorithm: ${algo.name}</div>
                    <div style="font-size: 0.9em; color: #4a5568; margin-bottom: 10px;">${algo.description}</div>
                    
                    <!-- Signature Size and QR Capacity Display -->
                    <div style="border: 3px solid ${warningColor}; border-radius: 8px; padding: 12px; background: white; margin: 10px 0;">
                        <div style="text-align: center;">
                            <div style="font-size: 1.2em; color: #718096; margin-bottom: 5px; font-weight: 600; letter-spacing: 1px;">SIGNATURE SIZE</div>
                            <div style="font-size: 1.8em; font-weight: bold; color: ${warningColor}; margin-bottom: 5px;">
                                ${algo.signatureSize} bytes
                            </div>
                            <div style="font-size: 1.2em; font-weight: 600; color: #4a5568;">
                                ${sizeMultiplier}× RSA-2048 (256 bytes)
                            </div>
                        </div>
                        ${algo.canFitInQR ? `
                        <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #e2e8f0;">
                            <div style="font-size: 0.85em; color: #4a5568; text-align: center;">
                                <div><strong>QR Code:</strong> Version ${algo.qrVersion} | ${algo.qrBlocks}×${algo.qrBlocks} (${algo.totalDots.toLocaleString()} dots)</div>
                                <div style="margin-top: 4px;"><strong>Payload:</strong> ~${algo.payloadSize} bytes | <strong>Error correction:</strong> L (7%)</div>
                                ${algo.warning ? `<div style="margin-top: 8px; color: #f59e0b; font-weight: 600;">${algo.warning}</div>` : ''}
                            </div>
                        </div>
                        ` : `
                        <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #e2e8f0;">
                            <div style="font-size: 0.85em; color: #dc2626; text-align: center; font-weight: 600;">
                                ${algo.warning}
                            </div>
                        </div>
                        `}
                    </div>
                    
                    ${isDummy && algo.canFitInQR ? '<div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #e2e8f0; font-size: 0.85em; color: #718096;"><strong>Note:</strong> This is a visual representation scaled to show relative QR code size. </div>' : ''}
                    ${!isDummy ? '<div style="font-size: 0.85em; color: #4a5568; margin-top: 5px;">✓ Actual signature from database - Optimized for smallest QR code (~40% size reduction vs High error correction + hex encoding)</div>' : ''}
                </div>
            `;
            
            // Update details
            document.getElementById('qr-detail-pass').textContent = passId;
            document.getElementById('qr-detail-timestamp').textContent = timestamp;
            const sigDisplay = actualSignature.length > 100 ? actualSignature.substring(0, 100) + '...' : actualSignature;
            document.getElementById('qr-detail-signature').textContent = sigDisplay;
        }
        
        function hexToBase64(hexString) {
            // Convert hex string to base64 for more compact encoding
            // Hex: 2 chars per byte, Base64: ~1.33 chars per byte = 32% smaller
            const bytes = [];
            for (let i = 0; i < hexString.length; i += 2) {
                bytes.push(parseInt(hexString.substr(i, 2), 16));
            }
            // Convert byte array to base64
            const binString = String.fromCharCode(...bytes);
            return btoa(binString);
        }
        
        function generateDummySignature(sizeInBytes) {
            // Generate a hex string of the specified size
            const hexChars = '0123456789abcdef';
            let signature = '';
            for (let i = 0; i < sizeInBytes * 2; i++) {
                signature += hexChars[Math.floor(Math.random() * 16)];
            }
            return signature;
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

# Create app instance for gunicorn
app = create_admin_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
