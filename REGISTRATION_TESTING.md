# 🧪 Registration System Testing Checklist

## 🎯 **Testing Environment**
- **Local URL**: http://localhost:8501
- **Test Credentials**: 
  - **Tester Token**: `EvalTester2025`
  - **Admin Password**: `Root_Blamlez`

## ✅ **Registration Flow Testing**

### **1. Access Control Verification**
- [ ] **Unauthenticated users** cannot access Blind Evaluation
- [ ] **Tester login required** before registration
- [ ] **Admin can access** all pages including registration view

### **2. Registration Form Validation**

#### **2.1 Name Validation**
- [ ] **Empty name** → Error: "Name is required"
- [ ] **Single character** (e.g., "A") → Error: "Please enter a valid name"
- [ ] **Numbers only** (e.g., "123") → Error: "Please enter a valid name"
- [ ] **Too long** (101+ characters) → Error: "Please enter a valid name"
- [ ] **Invalid characters** (e.g., "@#$") → Error: "Please enter a valid name"
- [ ] **Valid names** pass:
  - [ ] "John Doe"
  - [ ] "Dr. Smith"
  - [ ] "Mary O'Connor"
  - [ ] "Jean-Pierre"

#### **2.2 Email Validation**
- [ ] **Empty email** → Error: "Email is required"
- [ ] **Invalid format** → Error: "Please enter a valid email"
  - [ ] "invalid"
  - [ ] "@domain.com"
  - [ ] "user@"
  - [ ] "user..name@domain.com"
- [ ] **Valid emails** pass:
  - [ ] "test@example.com"
  - [ ] "user.name@domain.org"
  - [ ] "admin+test@company.co.uk"

#### **2.3 Consent Validation**
- [ ] **No consent checkbox** → Error: "You must provide explicit consent"
- [ ] **No email confirmation** → Error: "You must confirm your email address"
- [ ] **Both checkboxes required** for successful submission

### **3. Email Uniqueness Testing**

#### **3.1 First Registration**
- [ ] **Valid data + consent** → Success: "✅ Registration completed successfully!"
- [ ] **Balloons animation** appears on success
- [ ] **Page redirects** to evaluation interface
- [ ] **Welcome message** shows registered name

#### **3.2 Duplicate Email Prevention**
- [ ] **Same email** → Error: "This email address is already registered"
- [ ] **Case variations** detected:
  - [ ] "test@example.com" vs "TEST@EXAMPLE.COM"
  - [ ] "test@example.com" vs " test@example.com " (with spaces)
- [ ] **Different email** → Registration succeeds

### **4. Registration Persistence**

#### **4.1 Session Management**
- [ ] **Logout and re-login** → Registration persists
- [ ] **Page navigation** → Registration status maintained
- [ ] **Browser refresh** → Registration status maintained (Streamlit behavior)

#### **4.2 Registration Details Display**
- [ ] **Welcome message** shows correct name
- [ ] **Registration details** expandable section shows:
  - [ ] Correct name
  - [ ] Correct email
  - [ ] Consent status: "✅ Yes"
  - [ ] Registration timestamp

### **5. Admin View Testing**

#### **5.1 Registration Statistics**
- [ ] **Metrics display correctly**:
  - [ ] Total Registrations
  - [ ] Consented Testers
  - [ ] Completed Evaluations
- [ ] **Statistics update** after new registrations

#### **5.2 Registration Management**
- [ ] **Registration table** shows all registered testers
- [ ] **Data columns** display correctly:
  - [ ] Name
  - [ ] Email
  - [ ] Consent (✅/❌)
  - [ ] Registration timestamp
  - [ ] Evaluation status
- [ ] **CSV download** works for registration data

### **6. Security Testing**

#### **6.1 Data Handling**
- [ ] **No PII exposed** in browser dev tools
- [ ] **No PII in URLs** or visible logs
- [ ] **Email normalization** works (lowercase conversion)
- [ ] **Input sanitization** prevents code injection

#### **6.2 Session Security**
- [ ] **Registration data cleared** on logout
- [ ] **Admin cannot see** individual user's auth tokens
- [ ] **Testers cannot access** admin functions

### **7. Edge Cases Testing**

#### **7.1 Special Characters**
- [ ] **Names with apostrophes**: "O'Connor"
- [ ] **Names with hyphens**: "Mary-Jane"
- [ ] **Names with dots**: "Dr. Smith"
- [ ] **Emails with plus**: "user+test@domain.com"

#### **7.2 Input Limits**
- [ ] **Maximum name length** (100 characters)
- [ ] **Maximum email length** (254 characters)
- [ ] **Whitespace handling** (leading/trailing spaces removed)

#### **7.3 Network Issues**
- [ ] **Slow connection** doesn't cause double submission
- [ ] **Form resubmission** after error shows appropriate messages

## 🔧 **Manual Testing Steps**

### **Step 1: Basic Registration Flow**
1. Open Streamlit app
2. Login as tester: `EvalTester2025` + any email
3. Go to "Blind Evaluation"
4. Complete registration form:
   - **Name**: "Test User"
   - **Email**: "test@example.com"
   - **Check both checkboxes**
5. Submit → Should succeed with balloons

### **Step 2: Duplicate Prevention**
1. Logout and login again
2. Try to register with same email
3. Should get error: "This email address is already registered"

### **Step 3: Admin Verification**
1. Logout, login as admin: `Root_Blamlez`
2. Go to "Admin Panel"
3. Check registration statistics
4. Expand "Registration Management"
5. Verify data shows correctly

### **Step 4: Validation Testing**
1. Try various invalid inputs
2. Verify appropriate error messages
3. Test edge cases and special characters

## 🚨 **Common Issues to Watch For**

1. **Form state not clearing** after submission
2. **Duplicate submissions** causing errors
3. **Session state conflicts** between different users
4. **Email case sensitivity** bugs
5. **Registration data not persisting** across sessions
6. **Admin panel not updating** statistics
7. **Consent validation** not working properly

## ✅ **Success Criteria**

- [ ] All validation rules work correctly
- [ ] Email uniqueness is enforced
- [ ] Consent is properly collected and stored
- [ ] Registration data persists across sessions
- [ ] Admin can view and manage registrations
- [ ] No security vulnerabilities detected
- [ ] UI provides clear feedback for all scenarios
- [ ] Error messages are helpful and specific

## 🎉 **Testing Complete When...**

- [ ] All registration flows work correctly
- [ ] Email uniqueness is properly enforced
- [ ] Consent collection is bulletproof
- [ ] Admin management functions work
- [ ] Security testing passes
- [ ] Edge cases handled gracefully
- [ ] No critical bugs found

**Once all tests pass, the registration system is ready for production use!** 