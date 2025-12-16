# Ansible Automation for Smart Attendance System

Complete automation solution for deploying, testing, and managing the Smart Attendance Management System microservices.

---

## 📋 Overview

This Ansible automation provides one-command deployment of 6 microservices with built-in testing, monitoring, and management capabilities. Designed for consistency, reliability, and ease of use.

### Key Features

✅ **One-Command Deployment** - Deploy all 6 services with a single command
✅ **Automated Testing** - Comprehensive health checks and functional tests
✅ **Idempotent** - Safe to run multiple times without side effects
✅ **Self-Documenting** - Clear YAML syntax with detailed comments
✅ **Production-Ready** - Used patterns from enterprise deployments
✅ **Cloud-Compatible** - Works with local and cloud deployments (Render.com)

---

## 🚀 Quick Start

### Prerequisites

```bash
# Install Ansible
pip3 install ansible

# Verify installation
ansible --version  # Should show 2.9+

# Verify Python
python3 --version  # Should show 3.8+
```

### Basic Usage

```bash
# Navigate to ansible directory
cd /path/to/smart-attendance-system/ansible

# Deploy all services
ansible-playbook playbooks/deploy-all-services.yml

# Test all services
ansible-playbook playbooks/test-services.yml

# Stop all services
ansible-playbook playbooks/stop-all-services.yml

# Keep Render.com services alive (prevent sleep)
ansible-playbook playbooks/keep-services-alive.yml
```

---

## 📁 Project Structure

```
ansible/
├── ansible.cfg                          # Ansible configuration
├── inventory/
│   └── hosts.yml                       # Server/service definitions
├── playbooks/
│   ├── deploy-all-services.yml         # Main deployment playbook
│   ├── deploy-single-service.yml       # Single service deployment tasks
│   ├── test-services.yml               # Automated testing suite
│   ├── stop-all-services.yml           # Service shutdown playbook
│   └── keep-services-alive.yml         # Render.com keep-alive (optional)
├── DEMO_SCRIPT.md                      # Step-by-step presentation guide
├── PRESENTATION_NOTES.md               # Q&A and technical reference
└── README.md                           # This file
```

---

## 🎯 Services Deployed

| # | Service | Port | Description |
|---|---------|------|-------------|
| 1 | auth-service | 5007 | JWT Authentication |
| 2 | service-registry | 5008 | Service Discovery |
| 3 | student-service | 5001 | Student Management + Excel Import |
| 4 | course-service | 5002 | Course & Enrollment Management |
| 5 | attendance-service | 5005 | Attendance Tracking |
| 6 | api-gateway | 5000 | Central API Gateway |

---

## 📖 Detailed Usage

### 1. Deploy All Services

```bash
ansible-playbook playbooks/deploy-all-services.yml
```

**What it does:**
1. Installs system dependencies (Python, pip, venv)
2. Creates project directory structure
3. Deploys all 6 services in order
4. Starts each service in the background
5. Verifies all services are running
6. Generates deployment summary report

**Output Location:**
- Deployment summary: `/opt/smart-attendance/DEPLOYMENT_SUMMARY.txt`
- Service logs: `/opt/smart-attendance/*/service.log`
- Deployment log: `/opt/smart-attendance/deployment.log`

**Expected Duration:** 2-3 minutes (local), 30 seconds (cloud verification)

---

### 2. Test All Services

```bash
ansible-playbook playbooks/test-services.yml
```

**What it does:**
1. **Port Tests** - Verifies each service port is listening
2. **HTTP Tests** - Tests health endpoints for each service
3. **Functional Tests** - Tests login, student list, course list, etc.
4. **Performance Tests** - Measures response times
5. **Reporting** - Generates detailed test report

**Test Report Location:** `/opt/smart-attendance/TEST_REPORT.txt`

**Expected Results:** 18/18 tests passing (100% success rate)

---

### 3. Stop All Services

```bash
ansible-playbook playbooks/stop-all-services.yml
```

**What it does:**
1. Identifies running services
2. Attempts graceful shutdown (SIGTERM)
3. Force kills if necessary (SIGKILL)
4. Verifies all ports are freed
5. Archives log files
6. Generates shutdown summary

**Shutdown Summary:** `/opt/smart-attendance/SHUTDOWN_SUMMARY.txt`

---

### 4. Keep Services Alive (Render.com)

```bash
# Run once
ansible-playbook playbooks/keep-services-alive.yml

# Run in background
nohup ansible-playbook playbooks/keep-services-alive.yml &

# Or as cron job (every 5 minutes)
*/5 * * * * cd /path/to/ansible && ansible-playbook playbooks/keep-services-alive.yml >> /var/log/keep-alive.log 2>&1
```

**What it does:**
- Pings all 6 Render.com service URLs
- Prevents services from sleeping after 15 minutes
- Logs ping results
- Can run as background job or cron

---

## 🔧 Advanced Usage

### Deploy Specific Services Only

```bash
# Deploy only student and course services
ansible-playbook playbooks/deploy-all-services.yml --tags deploy --limit core_services
```

### Run with Different Inventory

```bash
# Use custom inventory
ansible-playbook playbooks/deploy-all-services.yml -i custom-inventory.yml
```

### Dry Run (Check Mode)

```bash
# See what would change without making changes
ansible-playbook playbooks/deploy-all-services.yml --check
```

### Verbose Output

```bash
# Level 1: Basic verbose
ansible-playbook playbooks/deploy-all-services.yml -v

# Level 2: More verbose
ansible-playbook playbooks/deploy-all-services.yml -vv

# Level 3: Debug level
ansible-playbook playbooks/deploy-all-services.yml -vvv
```

### Syntax Check

```bash
# Verify playbook syntax before running
ansible-playbook playbooks/deploy-all-services.yml --syntax-check
```

---

## 🎓 For Demonstration / Presentation

### 1. Follow the Demo Script

```bash
# Read the detailed step-by-step guide
cat DEMO_SCRIPT.md
```

**DEMO_SCRIPT.md includes:**
- Pre-demo checklist
- Exact commands to run
- What to say at each step
- Expected output
- Troubleshooting tips
- Time management (20 min demo)

### 2. Review Presentation Notes

```bash
# Quick reference for answering questions
cat PRESENTATION_NOTES.md
```

**PRESENTATION_NOTES.md includes:**
- Key Ansible concepts
- Expected Q&A
- Technical depth
- Metrics and comparisons
- Real-world examples

---

## 🛠️ Troubleshooting

### Issue: "ansible: command not found"

```bash
# Install Ansible
pip3 install ansible

# Or on Ubuntu/Debian
sudo apt update
sudo apt install ansible
```

### Issue: "Permission denied"

```bash
# Option 1: Run with sudo
sudo ansible-playbook playbooks/deploy-all-services.yml

# Option 2: Configure passwordless sudo
sudo visudo
# Add line: your_username ALL=(ALL) NOPASSWD: ALL
```

### Issue: "Port already in use"

```bash
# Stop all services first
ansible-playbook playbooks/stop-all-services.yml

# Then deploy again
ansible-playbook playbooks/deploy-all-services.yml

# Or manually kill process
lsof -ti:5000 | xargs kill -9
```

### Issue: Service won't start

```bash
# Check logs
tail -f /opt/smart-attendance/*/service.log

# Check if port is available
lsof -i :5000-5008

# Check Python environment
/opt/smart-attendance/student-service/venv/bin/python --version

# Manually start service for debugging
cd /opt/smart-attendance/student-service
source venv/bin/activate
python app.py
```

### Issue: Health checks failing

```bash
# Test service manually
curl http://localhost:5001/

# Check if service is running
ps aux | grep python

# Check firewall
sudo ufw status
sudo ufw allow 5000:5008/tcp
```

---

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| Total Playbooks | 5 |
| Total Tasks | ~150 tasks across all playbooks |
| Lines of YAML | ~800 lines |
| Services Managed | 6 microservices |
| Deployment Time | 2-3 minutes (local) |
| Test Coverage | 18 automated tests |
| Success Rate | 100% (when properly configured) |

---

## 🔐 Security Considerations

### For Production Deployment

1. **Use Ansible Vault for Secrets**
   ```bash
   # Encrypt sensitive data
   ansible-vault encrypt_string 'secret_password' --name 'db_password'

   # Run with vault password
   ansible-playbook playbook.yml --ask-vault-pass
   ```

2. **SSH Key Authentication**
   ```yaml
   # In inventory
   ansible_ssh_private_key_file: ~/.ssh/production_key
   ansible_user: deploy_user
   ```

3. **Limit Sudo Access**
   ```yaml
   # Only specific tasks need sudo
   become: yes
   become_user: root
   ```

4. **Use Environment Variables**
   ```bash
   # Don't hardcode secrets
   export JWT_SECRET_KEY="your-secret-key"
   ansible-playbook playbook.yml
   ```

---

## 🌐 Deployment Targets

### Local Deployment (Development)

Current configuration deploys to `localhost` for testing and demonstration.

### Cloud Deployment (Production)

For Render.com or other cloud platforms:

1. Update inventory with cloud URLs:
   ```yaml
   production:
     hosts:
       prod-server:
         ansible_host: your-app.onrender.com
   ```

2. Deploy to specific environment:
   ```bash
   ansible-playbook playbooks/deploy-all-services.yml --limit production
   ```

---

## 📚 Learning Resources

### Official Documentation
- [Ansible Documentation](https://docs.ansible.com/)
- [Ansible Galaxy](https://galaxy.ansible.com/) - Community roles
- [Ansible Best Practices](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)

### Tutorials
- [Ansible for DevOps](https://www.ansiblefordevops.com/)
- [DigitalOcean Ansible Tutorial](https://www.digitalocean.com/community/tutorial_series/how-to-use-ansible-for-configuration-management)
- [Red Hat Ansible Training](https://www.redhat.com/en/services/training/do007-ansible-essentials-simplicity-automation-technical-overview)

---

## 🤝 Contributing

To add new services or improve automation:

1. **Add Service to Inventory**
   ```yaml
   # In inventory/hosts.yml
   all_services:
     - name: new-service
       port: 5009
       health_endpoint: "/health"
   ```

2. **Update Deployment Playbook**
   ```yaml
   # Services are automatically deployed from inventory
   # No changes needed if using standard structure
   ```

3. **Test Changes**
   ```bash
   ansible-playbook playbooks/deploy-all-services.yml --syntax-check
   ansible-playbook playbooks/deploy-all-services.yml --check
   ansible-playbook playbooks/deploy-all-services.yml
   ```

---

## 📝 License

This automation is part of the Smart Attendance Management System project.

---

## 👨‍💻 Author

Created for academic demonstration of DevOps automation principles using Ansible.

**Project:** Smart Attendance Management System
**Technology Stack:** Ansible, Python, Flask, Microservices
**Deployment Targets:** Local (development), Render.com (production)

---

## 🆘 Support

For issues or questions:

1. Check [DEMO_SCRIPT.md](DEMO_SCRIPT.md) for step-by-step guidance
2. Review [PRESENTATION_NOTES.md](PRESENTATION_NOTES.md) for Q&A
3. Check Ansible logs: `/var/log/ansible.log`
4. Review service logs: `/opt/smart-attendance/*/service.log`

---

## ✅ Quick Command Reference

```bash
# Deploy everything
ansible-playbook playbooks/deploy-all-services.yml

# Test everything
ansible-playbook playbooks/test-services.yml

# Stop everything
ansible-playbook playbooks/stop-all-services.yml

# Keep Render services alive
ansible-playbook playbooks/keep-services-alive.yml

# Check syntax
ansible-playbook playbooks/deploy-all-services.yml --syntax-check

# Dry run
ansible-playbook playbooks/deploy-all-services.yml --check

# Verbose output
ansible-playbook playbooks/deploy-all-services.yml -vvv

# List all tasks
ansible-playbook playbooks/deploy-all-services.yml --list-tasks

# List all hosts
ansible-playbook playbooks/deploy-all-services.yml --list-hosts
```

---

**Last Updated:** December 2024
**Version:** 1.0
**Status:** ✅ Production Ready
