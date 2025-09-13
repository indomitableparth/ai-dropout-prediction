// AI-based Drop-out Prediction and Counseling System
// Smart India Hackathon 2025

class EduPredictApp {
    constructor() {
        this.currentUser = null;
        this.students = [];
        this.riskThresholds = {
            attendance_threshold: 75,
            failed_subjects_threshold: 2,
            fee_payment_threshold: 80
        };
        this.filteredStudents = [];
        this.currentView = 'dashboard';
        this.selectedStudent = null;
        
        this.init();
    }

    init() {
        this.loadSampleData();
        this.setupEventListeners();
        // Ensure loading screen is hidden and login page is shown
        this.hideLoading();
        this.showLoginPage();
    }

    loadSampleData() {
        // Sample student data from the provided JSON
        this.students = [
            {
                student_id: 1,
                student_name: "Rahul Sharma",
                total_classes: 50,
                classes_attended: 35,
                attendance_percentage: 70,
                subjects: [
                    {subject: "Math", marks_obtained: 42, max_marks: 100, status: "fail"},
                    {subject: "Physics", marks_obtained: 78, max_marks: 100, status: "pass"},
                    {subject: "Chemistry", marks_obtained: 35, max_marks: 100, status: "fail"}
                ],
                total_fees: 50000,
                fees_paid: 30000,
                fees_percentage: 60,
                risk_level: "red",
                risk_score: 0.85,
                risk_factors: ["Low Attendance (70%)", "Failed 2 subjects", "Fee overdue (40% pending)"]
            },
            {
                student_id: 2,
                student_name: "Priya Patel",
                total_classes: 48,
                classes_attended: 40,
                attendance_percentage: 83,
                subjects: [
                    {subject: "Math", marks_obtained: 65, max_marks: 100, status: "pass"},
                    {subject: "Physics", marks_obtained: 58, max_marks: 100, status: "pass"},
                    {subject: "Chemistry", marks_obtained: 72, max_marks: 100, status: "pass"}
                ],
                total_fees: 50000,
                fees_paid: 45000,
                fees_percentage: 90,
                risk_level: "yellow",
                risk_score: 0.35,
                risk_factors: ["Borderline performance in Physics"]
            },
            {
                student_id: 3,
                student_name: "Arjun Kumar",
                total_classes: 52,
                classes_attended: 48,
                attendance_percentage: 92,
                subjects: [
                    {subject: "Math", marks_obtained: 88, max_marks: 100, status: "pass"},
                    {subject: "Physics", marks_obtained: 85, max_marks: 100, status: "pass"},
                    {subject: "Chemistry", marks_obtained: 90, max_marks: 100, status: "pass"}
                ],
                total_fees: 50000,
                fees_paid: 50000,
                fees_percentage: 100,
                risk_level: "green",
                risk_score: 0.12,
                risk_factors: []
            },
            {
                student_id: 4,
                student_name: "Sneha Gupta",
                total_classes: 45,
                classes_attended: 30,
                attendance_percentage: 67,
                subjects: [
                    {subject: "Math", marks_obtained: 38, max_marks: 100, status: "fail"},
                    {subject: "Physics", marks_obtained: 45, max_marks: 100, status: "fail"},
                    {subject: "Chemistry", marks_obtained: 52, max_marks: 100, status: "pass"}
                ],
                total_fees: 50000,
                fees_paid: 25000,
                fees_percentage: 50,
                risk_level: "red",
                risk_score: 0.92,
                risk_factors: ["Very low attendance (67%)", "Failed 2 subjects", "Significant fee overdue (50% pending)"]
            },
            {
                student_id: 5,
                student_name: "Vikash Singh",
                total_classes: 50,
                classes_attended: 42,
                attendance_percentage: 84,
                subjects: [
                    {subject: "Math", marks_obtained: 75, max_marks: 100, status: "pass"},
                    {subject: "Physics", marks_obtained: 68, max_marks: 100, status: "pass"},
                    {subject: "Chemistry", marks_obtained: 80, max_marks: 100, status: "pass"}
                ],
                total_fees: 50000,
                fees_paid: 48000,
                fees_percentage: 96,
                risk_level: "green",
                risk_score: 0.18,
                risk_factors: []
            }
        ];
        
        this.filteredStudents = [...this.students];
    }

    setupEventListeners() {
        // Login form
        document.getElementById('login-form').addEventListener('submit', (e) => this.handleLogin(e));
        
        // Logout
        document.getElementById('logout-btn').addEventListener('click', () => this.handleLogout());
        
        // Navigation
        document.getElementById('back-to-dashboard').addEventListener('click', () => this.showDashboard());
        
        // Action buttons
        document.getElementById('upload-data-btn').addEventListener('click', () => this.showUploadModal());
        document.getElementById('configure-thresholds-btn').addEventListener('click', () => this.showThresholdsModal());
        document.getElementById('send-notifications-btn').addEventListener('click', () => this.showNotificationsModal());
        
        // Modal controls
        document.getElementById('close-upload-modal').addEventListener('click', () => this.hideModal('upload-modal'));
        document.getElementById('close-thresholds-modal').addEventListener('click', () => this.hideModal('thresholds-modal'));
        document.getElementById('close-notifications-modal').addEventListener('click', () => this.hideModal('notifications-modal'));
        
        // Upload actions
        document.getElementById('use-sample-data').addEventListener('click', () => this.useSampleData());
        document.getElementById('process-upload').addEventListener('click', () => this.processUpload());
        
        // Threshold actions
        document.getElementById('save-thresholds').addEventListener('click', () => this.saveThresholds());
        
        // Notification actions
        document.getElementById('send-notifications').addEventListener('click', () => this.sendNotifications());
        
        // Search and filter
        document.getElementById('search-students').addEventListener('input', (e) => this.filterStudents());
        document.getElementById('filter-risk').addEventListener('change', (e) => this.filterStudents());
        
        // Message close
        document.getElementById('close-message').addEventListener('click', () => this.hideMessage());
        
        // Modal backdrop clicks
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideModal(modal.id);
                }
            });
        });

        // Setup notification checkboxes
        const notifyHighRisk = document.getElementById('notify-high-risk');
        const notifyMediumRisk = document.getElementById('notify-medium-risk');
        
        if (notifyHighRisk) {
            notifyHighRisk.addEventListener('change', () => this.updateNotificationPreview());
        }
        
        if (notifyMediumRisk) {
            notifyMediumRisk.addEventListener('change', () => this.updateNotificationPreview());
        }
    }

    handleLogin(e) {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const role = document.getElementById('role').value;
        
        // Simple authentication (demo purposes)
        const validCredentials = [
            { email: 'admin@edupredict.com', password: 'admin123', role: 'Admin', name: 'Admin User' },
            { email: 'mentor@edupredict.com', password: 'mentor123', role: 'Mentor', name: 'Mentor User' }
        ];
        
        const user = validCredentials.find(cred => 
            cred.email === email && cred.password === password && cred.role === role
        );
        
        if (user) {
            this.currentUser = user;
            this.showMainApp();
        } else {
            this.showMessage('Invalid credentials. Please check your email, password, and role.', 'error');
        }
    }

    handleLogout() {
        this.currentUser = null;
        this.showLoginPage();
    }

    showLoginPage() {
        document.getElementById('login-page').classList.remove('hidden');
        document.getElementById('main-app').classList.add('hidden');
        document.getElementById('login-form').reset();
    }

    showMainApp() {
        document.getElementById('login-page').classList.add('hidden');
        document.getElementById('main-app').classList.remove('hidden');
        
        // Update user info
        document.getElementById('user-name').textContent = `Welcome, ${this.currentUser.name}`;
        document.getElementById('user-role-badge').textContent = this.currentUser.role;
        
        // Hide admin-only features for mentors
        if (this.currentUser.role === 'Mentor') {
            document.getElementById('upload-data-btn').style.display = 'none';
            document.getElementById('configure-thresholds-btn').style.display = 'none';
        } else {
            document.getElementById('upload-data-btn').style.display = 'inline-flex';
            document.getElementById('configure-thresholds-btn').style.display = 'inline-flex';
        }
        
        this.showDashboard();
    }

    showDashboard() {
        document.getElementById('dashboard-view').classList.remove('hidden');
        document.getElementById('student-detail-view').classList.add('hidden');
        
        this.updateDashboardStats();
        this.renderStudentsTable();
        this.currentView = 'dashboard';
    }

    updateDashboardStats() {
        const total = this.students.length;
        const highRisk = this.students.filter(s => s.risk_level === 'red').length;
        const mediumRisk = this.students.filter(s => s.risk_level === 'yellow').length;
        const lowRisk = this.students.filter(s => s.risk_level === 'green').length;
        
        document.getElementById('total-students').textContent = total;
        document.getElementById('high-risk-students').textContent = highRisk;
        document.getElementById('medium-risk-students').textContent = mediumRisk;
        document.getElementById('low-risk-students').textContent = lowRisk;
    }

    renderStudentsTable() {
        const tbody = document.getElementById('students-table-body');
        tbody.innerHTML = '';
        
        if (this.filteredStudents.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="empty-state">
                        <i class="fas fa-users"></i>
                        <h3>No Students Found</h3>
                        <p>No students match your current filters.</p>
                    </td>
                </tr>
            `;
            return;
        }
        
        this.filteredStudents.forEach(student => {
            const failedSubjects = student.subjects.filter(s => s.status === 'fail').length;
            const avgMarks = student.subjects.reduce((sum, s) => sum + (s.marks_obtained / s.max_marks * 100), 0) / student.subjects.length;
            
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${student.student_id}</td>
                <td class="font-semibold">${student.student_name}</td>
                <td>
                    <div class="flex items-center gap-8">
                        <span>${student.attendance_percentage}%</span>
                        <div class="progress-bar" style="width: 60px;">
                            <div class="progress-fill ${this.getProgressClass(student.attendance_percentage)}" 
                                 style="width: ${student.attendance_percentage}%"></div>
                        </div>
                    </div>
                </td>
                <td>
                    <div class="flex flex-col gap-4">
                        <span>${avgMarks.toFixed(1)}% avg</span>
                        <small class="text-sm">${failedSubjects > 0 ? `${failedSubjects} failed` : 'All passed'}</small>
                    </div>
                </td>
                <td>
                    <div class="flex items-center gap-8">
                        <span>${student.fees_percentage}%</span>
                        <div class="progress-bar" style="width: 60px;">
                            <div class="progress-fill ${this.getProgressClass(student.fees_percentage)}" 
                                 style="width: ${student.fees_percentage}%"></div>
                        </div>
                    </div>
                </td>
                <td><span class="risk-badge risk-badge--${student.risk_level}">${this.getRiskLabel(student.risk_level)}</span></td>
                <td><span class="risk-score">${(student.risk_score * 100).toFixed(1)}%</span></td>
                <td>
                    <button class="btn btn--outline btn--sm" onclick="app.showStudentDetail(${student.student_id})">
                        <i class="fas fa-eye"></i> View Details
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    showStudentDetail(studentId) {
        this.selectedStudent = this.students.find(s => s.student_id === studentId);
        if (!this.selectedStudent) return;
        
        document.getElementById('dashboard-view').classList.add('hidden');
        document.getElementById('student-detail-view').classList.remove('hidden');
        
        // Update student name in header
        document.getElementById('student-detail-name').textContent = this.selectedStudent.student_name;
        
        // Render student details
        this.renderStudentBasicInfo();
        this.renderStudentAttendance();
        this.renderStudentPerformance();
        this.renderStudentFees();
        this.renderStudentRisk();
        
        this.currentView = 'detail';
    }

    renderStudentBasicInfo() {
        const container = document.getElementById('student-basic-info');
        container.innerHTML = `
            <div class="info-item">
                <span class="info-label">Student ID</span>
                <span class="info-value">${this.selectedStudent.student_id}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Name</span>
                <span class="info-value">${this.selectedStudent.student_name}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Risk Level</span>
                <span class="info-value">
                    <span class="risk-badge risk-badge--${this.selectedStudent.risk_level}">
                        ${this.getRiskLabel(this.selectedStudent.risk_level)}
                    </span>
                </span>
            </div>
            <div class="info-item">
                <span class="info-label">ML Risk Score</span>
                <span class="info-value risk-score">${(this.selectedStudent.risk_score * 100).toFixed(1)}%</span>
            </div>
        `;
    }

    renderStudentAttendance() {
        const container = document.getElementById('student-attendance-info');
        container.innerHTML = `
            <div class="info-item">
                <span class="info-label">Total Classes</span>
                <span class="info-value">${this.selectedStudent.total_classes}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Classes Attended</span>
                <span class="info-value">${this.selectedStudent.classes_attended}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Attendance Percentage</span>
                <span class="info-value">${this.selectedStudent.attendance_percentage}%</span>
            </div>
            <div class="progress-bar mt-16">
                <div class="progress-fill ${this.getProgressClass(this.selectedStudent.attendance_percentage)}" 
                     style="width: ${this.selectedStudent.attendance_percentage}%"></div>
            </div>
        `;
    }

    renderStudentPerformance() {
        const container = document.getElementById('student-performance-info');
        const subjects = this.selectedStudent.subjects;
        const avgMarks = subjects.reduce((sum, s) => sum + (s.marks_obtained / s.max_marks * 100), 0) / subjects.length;
        
        let subjectsHtml = subjects.map(subject => `
            <div class="subject-grade">
                <span>${subject.subject}</span>
                <span class="${subject.status === 'pass' ? 'grade-pass' : 'grade-fail'}">
                    ${subject.marks_obtained}/${subject.max_marks} (${(subject.marks_obtained / subject.max_marks * 100).toFixed(1)}%)
                </span>
            </div>
        `).join('');
        
        container.innerHTML = `
            <div class="info-item">
                <span class="info-label">Average Score</span>
                <span class="info-value">${avgMarks.toFixed(1)}%</span>
            </div>
            <div class="info-item">
                <span class="info-label">Subjects Passed</span>
                <span class="info-value">${subjects.filter(s => s.status === 'pass').length}/${subjects.length}</span>
            </div>
            <div class="mt-16">
                <h4 class="mb-8">Subject Breakdown</h4>
                ${subjectsHtml}
            </div>
        `;
    }

    renderStudentFees() {
        const container = document.getElementById('student-fee-info');
        const pending = this.selectedStudent.total_fees - this.selectedStudent.fees_paid;
        
        container.innerHTML = `
            <div class="info-item">
                <span class="info-label">Total Fees</span>
                <span class="info-value">₹${this.selectedStudent.total_fees.toLocaleString()}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Fees Paid</span>
                <span class="info-value">₹${this.selectedStudent.fees_paid.toLocaleString()}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Pending</span>
                <span class="info-value">₹${pending.toLocaleString()}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Payment Percentage</span>
                <span class="info-value">${this.selectedStudent.fees_percentage}%</span>
            </div>
            <div class="progress-bar mt-16">
                <div class="progress-fill ${this.getProgressClass(this.selectedStudent.fees_percentage)}" 
                     style="width: ${this.selectedStudent.fees_percentage}%"></div>
            </div>
        `;
    }

    renderStudentRisk() {
        const container = document.getElementById('student-risk-info');
        
        let riskFactorsHtml = '';
        if (this.selectedStudent.risk_factors.length > 0) {
            riskFactorsHtml = `
                <h4 class="mb-8">Risk Factors</h4>
                <ul class="risk-factors">
                    ${this.selectedStudent.risk_factors.map(factor => `<li>${factor}</li>`).join('')}
                </ul>
            `;
        } else {
            riskFactorsHtml = `
                <div class="text-center">
                    <i class="fas fa-check-circle" style="color: var(--color-success); font-size: var(--font-size-2xl); margin-bottom: var(--space-8);"></i>
                    <p>No risk factors identified. Student is performing well.</p>
                </div>
            `;
        }
        
        container.innerHTML = riskFactorsHtml;
    }

    filterStudents() {
        const searchTerm = document.getElementById('search-students').value.toLowerCase();
        const riskFilter = document.getElementById('filter-risk').value;
        
        this.filteredStudents = this.students.filter(student => {
            const matchesSearch = student.student_name.toLowerCase().includes(searchTerm) ||
                                student.student_id.toString().includes(searchTerm);
            const matchesRisk = !riskFilter || student.risk_level === riskFilter;
            
            return matchesSearch && matchesRisk;
        });
        
        this.renderStudentsTable();
    }

    showUploadModal() {
        this.showModal('upload-modal');
    }

    showThresholdsModal() {
        // Populate current thresholds
        document.getElementById('attendance-threshold').value = this.riskThresholds.attendance_threshold;
        document.getElementById('failed-subjects-threshold').value = this.riskThresholds.failed_subjects_threshold;
        document.getElementById('fee-threshold').value = this.riskThresholds.fee_payment_threshold;
        
        this.showModal('thresholds-modal');
    }

    showNotificationsModal() {
        this.updateNotificationPreview();
        this.showModal('notifications-modal');
    }

    updateNotificationPreview() {
        const container = document.getElementById('notification-preview');
        const highRisk = document.getElementById('notify-high-risk').checked;
        const mediumRisk = document.getElementById('notify-medium-risk').checked;
        
        let studentsToNotify = [];
        if (highRisk) studentsToNotify.push(...this.students.filter(s => s.risk_level === 'red'));
        if (mediumRisk) studentsToNotify.push(...this.students.filter(s => s.risk_level === 'yellow'));
        
        if (studentsToNotify.length === 0) {
            container.innerHTML = '<p>No students selected for notifications.</p>';
            return;
        }
        
        container.innerHTML = `
            <h4>Students to be notified (${studentsToNotify.length})</h4>
            ${studentsToNotify.map(student => `
                <div class="notification-item">
                    <strong>${student.student_name}</strong> (ID: ${student.student_id})
                    <br>
                    <small>Risk Level: ${this.getRiskLabel(student.risk_level)} | Risk Score: ${(student.risk_score * 100).toFixed(1)}%</small>
                </div>
            `).join('')}
        `;
    }

    useSampleData() {
        this.loadSampleData();
        this.showLoading('Loading sample data...');
        
        setTimeout(() => {
            this.hideLoading();
            this.hideModal('upload-modal');
            this.recalculateRiskScores();
            this.updateDashboardStats();
            this.renderStudentsTable();
            this.showMessage('Sample data loaded successfully!', 'success');
        }, 1500);
    }

    processUpload() {
        const attendanceFile = document.getElementById('attendance-file').files[0];
        const marksFile = document.getElementById('marks-file').files[0];
        const feesFile = document.getElementById('fees-file').files[0];
        
        if (!attendanceFile || !marksFile || !feesFile) {
            this.showMessage('Please select all three CSV files.', 'error');
            return;
        }
        
        this.showLoading('Processing uploaded files...');
        
        // Simulate file processing
        setTimeout(() => {
            this.hideLoading();
            this.hideModal('upload-modal');
            this.showMessage('Files processed successfully! Data has been updated.', 'success');
        }, 2000);
    }

    saveThresholds() {
        this.riskThresholds.attendance_threshold = parseInt(document.getElementById('attendance-threshold').value);
        this.riskThresholds.failed_subjects_threshold = parseInt(document.getElementById('failed-subjects-threshold').value);
        this.riskThresholds.fee_payment_threshold = parseInt(document.getElementById('fee-threshold').value);
        
        this.recalculateRiskScores();
        this.hideModal('thresholds-modal');
        this.showMessage('Risk thresholds updated successfully!', 'success');
        this.updateDashboardStats();
        this.renderStudentsTable();
    }

    recalculateRiskScores() {
        this.students.forEach(student => {
            const failedSubjects = student.subjects.filter(s => s.status === 'fail').length;
            let riskFactors = [];
            let riskScore = 0;
            
            // Attendance risk
            if (student.attendance_percentage < this.riskThresholds.attendance_threshold) {
                riskFactors.push(`Low Attendance (${student.attendance_percentage}%)`);
                riskScore += 0.4;
            }
            
            // Academic performance risk
            if (failedSubjects >= this.riskThresholds.failed_subjects_threshold) {
                riskFactors.push(`Failed ${failedSubjects} subjects`);
                riskScore += 0.4;
            }
            
            // Fee payment risk
            if (student.fees_percentage < this.riskThresholds.fee_payment_threshold) {
                const pending = 100 - student.fees_percentage;
                riskFactors.push(`Fee overdue (${pending}% pending)`);
                riskScore += 0.3;
            }
            
            // Determine risk level
            if (riskScore >= 0.7) {
                student.risk_level = 'red';
            } else if (riskScore >= 0.3) {
                student.risk_level = 'yellow';
            } else {
                student.risk_level = 'green';
            }
            
            student.risk_score = Math.min(riskScore, 1);
            student.risk_factors = riskFactors;
        });
        
        this.filteredStudents = [...this.students];
    }

    sendNotifications() {
        const highRisk = document.getElementById('notify-high-risk').checked;
        const mediumRisk = document.getElementById('notify-medium-risk').checked;
        
        let studentsToNotify = [];
        if (highRisk) studentsToNotify.push(...this.students.filter(s => s.risk_level === 'red'));
        if (mediumRisk) studentsToNotify.push(...this.students.filter(s => s.risk_level === 'yellow'));
        
        if (studentsToNotify.length === 0) {
            this.showMessage('No students selected for notifications.', 'warning');
            return;
        }
        
        this.showLoading('Sending notifications...');
        
        // Simulate sending notifications
        setTimeout(() => {
            this.hideLoading();
            this.hideModal('notifications-modal');
            this.showMessage(`Notifications sent successfully to ${studentsToNotify.length} students!`, 'success');
        }, 2000);
    }

    showModal(modalId) {
        document.getElementById(modalId).classList.remove('hidden');
    }

    hideModal(modalId) {
        document.getElementById(modalId).classList.add('hidden');
    }

    showLoading(message) {
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            loadingScreen.querySelector('p').textContent = message || 'Loading...';
            loadingScreen.classList.remove('hidden');
        }
    }

    hideLoading() {
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            loadingScreen.classList.add('hidden');
        }
    }

    showMessage(text, type = 'success') {
        const container = document.getElementById('message-container');
        const message = document.getElementById('message');
        
        message.className = `message message--${type}`;
        document.getElementById('message-text').textContent = text;
        container.classList.remove('hidden');
        
        // Auto hide after 5 seconds
        setTimeout(() => this.hideMessage(), 5000);
    }

    hideMessage() {
        document.getElementById('message-container').classList.add('hidden');
    }

    getRiskLabel(riskLevel) {
        const labels = {
            'red': 'High Risk',
            'yellow': 'Medium Risk',
            'green': 'Low Risk'
        };
        return labels[riskLevel] || 'Unknown';
    }

    getProgressClass(percentage) {
        if (percentage >= 80) return 'progress-fill--high';
        if (percentage >= 60) return 'progress-fill--medium';
        return 'progress-fill--low';
    }
}

// Initialize the application
const app = new EduPredictApp();

// Expose app globally for onclick handlers
window.app = app;