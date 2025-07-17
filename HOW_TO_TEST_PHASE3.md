# 🧪 How to Test Phase 3: Registration & Consent System

## 📍 Quick Navigation to Phase 3 Features

### **STEP 1: Start Application**
```bash
# Your app is already running at:
http://localhost:8501
```

### **STEP 2: Navigate to Registration System**

**Path to Registration:**
```
Home Page → Sidebar: "Blind Evaluation" → Tester Login → Registration Form
```

**Visual Navigation Flow:**
```
🏠 HOME PAGE
├── 📋 Sidebar Navigation
│   ├── Home
│   ├── Blind Evaluation ← CLICK HERE
│   ├── System Status
│   └── [More options appear after login]
```

### **STEP 3: Tester Authentication**
```
🔐 AUTHENTICATION REQUIRED
├── Access Token: "EvalTester2025"
└── Click: "Access Evaluation"
```

### **STEP 4: Registration Form Appears**
```
👤 REGISTRATION FORM (Phase 3 Implementation)
├── 📝 Name Input (2-100 characters)
├── 📧 Email Input (format validation)
├── ☑️ Consent Checkboxes (all required):
│   ├── "I consent to participate in this evaluation"
│   ├── "I understand my responses will be recorded"
│   ├── "I agree to the data usage terms"
│   └── "I confirm I am 18+ years old"
└── 🚀 Submit Registration
```

## 🎯 **Phase 3 Features to Test**

### **✅ Email Validation**
- Try invalid emails: `test`, `test@`, `@test.com`
- Try valid emails: `john.doe@test.com`

### **✅ Name Validation** 
- Try empty names, single characters
- Try very long names (100+ characters)
- Try names with special characters

### **✅ Consent Management**
- Try submitting without checking all boxes
- Verify all consent checkboxes are required

### **✅ Duplicate Prevention**
- Register with an email
- Try registering again with the same email
- Should be blocked with error message

### **✅ Admin View**
- Logout from tester account
- Login as admin (password: "Root_Blamlez")
- Navigate to "Admin Panel"
- View registration statistics and user table

## 🔍 **Expected Results**

**After Successful Registration:**
```
✅ Registration Complete!
├── Welcome message with your name
├── Registration details in expandable section
├── Evaluation interface becomes available
└── Admin panel shows your registration data
```

**Registration Statistics (Admin Panel):**
```
📊 ADMIN DASHBOARD
├── Total Registrations: [count]
├── Consented Testers: [count]  
├── Completed Evaluations: [count]
└── 📥 Download CSV functionality
```

## 🎪 **Demo Test Data**

Use these for testing:

**Test Registration 1:**
- Name: `John Doe`
- Email: `john.doe@test.com`

**Test Registration 2:**
- Name: `Jane Smith`  
- Email: `jane.smith@test.com`

**Test Registration 3:**
- Name: `Bob Wilson`
- Email: `bob.wilson@test.com`

## 🐛 **Troubleshooting**

**If Registration Form Doesn't Appear:**
1. Make sure you're authenticated as a tester first
2. Check you're on the "Blind Evaluation" page
3. Clear browser cache and try again

**If You See "Evaluation Interface" Instead:**
- You're already registered!
- Look for "Reset Registration (Testing Only)" button
- Or use admin panel to clear registration data

## 📱 **Testing Checklist**

- [ ] Navigate to Blind Evaluation page
- [ ] Authenticate as tester
- [ ] See registration form
- [ ] Test email validation
- [ ] Test name validation  
- [ ] Test consent requirements
- [ ] Complete valid registration
- [ ] Verify duplicate prevention
- [ ] Check admin panel statistics
- [ ] Test logout and re-login
- [ ] Verify registration persists

---

**🎉 Phase 3 is fully implemented and ready for testing!** 