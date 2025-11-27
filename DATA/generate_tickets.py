import csv
import random
from datetime import datetime, timedelta

def generate_it_tickets_csv(filename='it_tickets_1000.csv'):
    # Data configurations
    ticket_types = ['hardware', 'software', 'network', 'email', 'access', 'security', 'backup', 'database']
    severity_levels = ['Low', 'Medium', 'High']
    status_options = ['Open', 'In Progress', 'Closed', 'Resolved']
    
    domains = ['company.com', 'enterprise.org', 'business.net', 'corp.io', 'tech.org']
    departments = ['sales', 'marketing', 'engineering', 'finance', 'hr', 'operations', 'support', 'research']
    
    first_names = ['john', 'jane', 'mike', 'sarah', 'david', 'lisa', 'robert', 'emily', 'chris', 'amanda', 
                  'james', 'michelle', 'steven', 'rebecca', 'kevin', 'jennifer', 'thomas', 'natalie', 'eric', 'susan']
    last_names = ['smith', 'johnson', 'williams', 'brown', 'jones', 'miller', 'davis', 'garcia', 'rodriguez', 
                 'wilson', 'martinez', 'anderson', 'taylor', 'thomas', 'moore', 'jackson', 'white', 'harris']

    descriptions = {
        'hardware': [
            'Laptop overheating and shutting down randomly during presentations',
            'Desktop computer not powering on - no lights or sounds',
            'Monitor displaying distorted colors and flickering lines',
            'Keyboard keys not responding consistently during typing',
            'Printer paper jam error despite clear paper path',
            'Server disk space critically low at 98% capacity',
            'Workstation blue screen errors occurring multiple times daily',
            'Laptop battery not holding charge, lasts only 15 minutes',
            'Docking station not recognizing external monitors',
            'Server hardware failure detected in RAID controller'
        ],
        'software': [
            'Application crashing on startup with memory access violation',
            'Software license activation failed - invalid license key',
            'Program running extremely slow when processing large files',
            'Update installation stuck at 50% for over 2 hours',
            'Compatibility issues with new operating system update',
            'Plugin not loading correctly in design application',
            'Software freezing during use, requires force quit',
            'Installation package corrupted during download',
            'Application throwing database connection errors',
            'Software configuration reset after system reboot'
        ],
        'network': [
            'Intermittent internet connectivity in entire north building',
            'VPN connection timeout issues for remote team members',
            'WiFi signal weak in third floor conference room',
            'Network drive inaccessible with permission denied errors',
            'Slow file transfer speeds between departments',
            'DNS resolution failures for internal applications',
            'Port configuration required for new security system',
            'Network latency spikes during peak business hours',
            'Switch port malfunctioning in server room rack 4B',
            'Wireless access point firmware needs urgent update'
        ],
        'email': [
            'Outlook not syncing with Exchange server - connection timeout',
            'Legitimate emails being marked as spam by filter system',
            'Large attachments failing to send with size limit errors',
            'Calendar sync failed between mobile and desktop clients',
            'Email rules not executing automatically as configured',
            'Global address list not updating with new employees',
            'Email search functionality returning incomplete results',
            'Automatic replies not triggering during scheduled times',
            'Email client crashing when opening specific messages',
            'Signature formatting broken after recent update'
        ],
        'access': [
            'New employee needs access to project management software',
            'User account locked due to multiple failed login attempts',
            'Folder permissions need updating for quarterly project',
            'Database access required for financial reporting team',
            'VPN credentials not working for overseas contractor',
            'Application-specific roles need configuration',
            'Terminated employee access revocation incomplete',
            'Shared mailbox permissions need review and cleanup',
            'Multi-factor authentication device replacement needed',
            'Security group membership requires quarterly audit'
        ],
        'security': [
            'Critical Windows security patches need immediate deployment',
            'Firewall rules blocking legitimate application traffic',
            'Antivirus detection of potential malware in shared drive',
            'Security audit reveals compliance violations in user accounts',
            'Intrusion detection system generating false positives',
            'Password policy enforcement not working for service accounts',
            'Security certificate expiring for customer portal',
            'Data encryption required for sensitive client information',
            'Access logs showing suspicious login patterns',
            'Security training completion tracking implementation'
        ],
        'backup': [
            'Nightly backup failed due to insufficient storage space',
            'Backup verification process taking longer than expected',
            'Cloud backup synchronization stalled at 80% complete',
            'Backup restore test failed for critical database',
            'Backup retention policy needs configuration review',
            'Tape drive hardware failure in backup system',
            'Backup encryption key rotation required per policy',
            'Backup job scheduling conflict with maintenance window',
            'Incremental backup corruption detected during verification',
            'Backup storage capacity planning for next quarter'
        ],
        'database': [
            'Database performance degradation during peak hours',
            'SQL query timeout errors in reporting application',
            'Database connection pool exhaustion under load',
            'Index fragmentation causing slow query performance',
            'Database backup verification failed checksum test',
            'Table space running low, requires immediate attention',
            'Database replication lag between primary and secondary',
            'Stored procedure optimization needed for billing system',
            'Database log file growth exceeding allocated space',
            'Database version upgrade planning and testing'
        ]
    }

    data_fields = {
        'hardware': ['Performance metrics', 'Hardware diagnostics', 'System logs', 'Temperature readings', 'Power consumption data'],
        'software': ['Application logs', 'Installation records', 'Error reports', 'Performance analytics', 'Usage statistics'],
        'network': ['Connectivity logs', 'Packet capture data', 'Network statistics', 'Bandwidth usage', 'Latency measurements'],
        'email': ['Configuration data', 'SMTP logs', 'Mail queue data', 'Spam filter results', 'Delivery reports'],
        'access': ['Audit logs', 'Permission records', 'Access control lists', 'Login attempts', 'Security group data'],
        'security': ['Security logs', 'Firewall rules', 'Threat detection data', 'Virus scan results', 'Compliance reports'],
        'backup': ['Backup logs', 'Verification reports', 'Storage metrics', 'Recovery test results', 'Capacity planning data'],
        'database': ['Query performance', 'Backup records', 'Connection logs', 'Table statistics', 'Index usage data']
    }

    print(f"Generating {filename} with 1000 records...")
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow(['id', 'data', 'tickets_type', 'severity', 'status', 'description', 'reported_by', 'created_at'])
        
        start_date = datetime(2024, 1, 1)
        
        for ticket_id in range(1, 1001):
            ticket_type = random.choice(ticket_types)
            severity = random.choice(severity_levels)
            status = random.choice(status_options)
            
            # Generate description
            description = random.choice(descriptions[ticket_type])
            
            # Generate reporter email
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            department = random.choice(departments)
            domain = random.choice(domains)
            reporter = f"{first_name}.{last_name}.{department}@{domain}"
            
            # Generate data field
            data_field = random.choice(data_fields[ticket_type])
            
            # Generate random timestamp within the last 90 days
            days_ago = random.randint(0, 90)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            created_at = start_date + timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
            
            writer.writerow([
                ticket_id,
                data_field,
                ticket_type,
                severity,
                status,
                description,
                reporter,
                created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
    
    print(f"Successfully generated {filename} with 1000 IT tickets!")
    print("File columns: id, data, tickets_type, severity, status, description, reported_by, created_at")
    return filename

# Generate the CSV file
if __name__ == "__main__":
    generate_it_tickets_csv()