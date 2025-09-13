import pandas as pd
import csv

# Create sample attendance data
attendance_data = [
    [1, "Rahul Sharma", 50, 35],
    [2, "Priya Patel", 48, 40], 
    [3, "Arjun Kumar", 52, 48],
    [4, "Sneha Gupta", 45, 30],
    [5, "Vikash Singh", 50, 42],
    [6, "Anita Rao", 46, 38],
    [7, "Deepak Joshi", 51, 47],
    [8, "Kavya Nair", 49, 32],
    [9, "Rohit Agarwal", 53, 51],
    [10, "Meera Shah", 47, 35],
    [11, "Amit Verma", 52, 45],
    [12, "Pooja Kumar", 48, 25],
    [13, "Suresh Reddy", 50, 49],
    [14, "Divya Sharma", 46, 40],
    [15, "Karan Malhotra", 49, 28]
]

attendance_df = pd.DataFrame(attendance_data, columns=["student_id", "student_name", "total_classes", "classes_attended"])
attendance_df.to_csv("sample_attendance.csv", index=False)

# Create sample marks data  
marks_data = []
subjects = ["Mathematics", "Physics", "Chemistry", "Biology", "English"]

for student_id in range(1, 16):
    student_names = {
        1: "Rahul Sharma", 2: "Priya Patel", 3: "Arjun Kumar", 4: "Sneha Gupta", 5: "Vikash Singh",
        6: "Anita Rao", 7: "Deepak Joshi", 8: "Kavya Nair", 9: "Rohit Agarwal", 10: "Meera Shah",
        11: "Amit Verma", 12: "Pooja Kumar", 13: "Suresh Reddy", 14: "Divya Sharma", 15: "Karan Malhotra"
    }
    
    student_name = student_names[student_id]
    
    # Generate marks based on risk profile
    if student_id in [1, 4, 8, 12, 15]:  # High risk students
        base_marks = [42, 35, 38, 28, 45]  # Lower marks
    elif student_id in [2, 6, 10, 14]:  # Medium risk students  
        base_marks = [65, 58, 62, 55, 70]  # Average marks
    else:  # Low risk students
        base_marks = [88, 85, 90, 82, 87]  # High marks
    
    for i, subject in enumerate(subjects):
        marks_data.append([student_id, student_name, subject, base_marks[i], 100])

marks_df = pd.DataFrame(marks_data, columns=["student_id", "student_name", "subject", "marks_obtained", "max_marks"])
marks_df.to_csv("sample_marks.csv", index=False)

# Create sample fees data
fees_data = [
    [1, "Rahul Sharma", 50000, 30000],
    [2, "Priya Patel", 50000, 45000],
    [3, "Arjun Kumar", 50000, 50000],
    [4, "Sneha Gupta", 50000, 25000], 
    [5, "Vikash Singh", 50000, 48000],
    [6, "Anita Rao", 50000, 42000],
    [7, "Deepak Joshi", 50000, 50000],
    [8, "Kavya Nair", 50000, 22000],
    [9, "Rohit Agarwal", 50000, 50000],
    [10, "Meera Shah", 50000, 35000],
    [11, "Amit Verma", 50000, 47000],
    [12, "Pooja Kumar", 50000, 18000],
    [13, "Suresh Reddy", 50000, 50000],
    [14, "Divya Sharma", 50000, 43000],
    [15, "Karan Malhotra", 50000, 20000]
]

fees_df = pd.DataFrame(fees_data, columns=["student_id", "student_name", "total_fees", "fees_paid"])
fees_df.to_csv("sample_fees.csv", index=False)

print("Sample CSV files created successfully!")
print(f"Attendance data: {len(attendance_df)} students")
print(f"Marks data: {len(marks_df)} records across {len(subjects)} subjects") 
print(f"Fees data: {len(fees_df)} students")

# Display sample data
print("\n--- Sample Attendance Data ---")
print(attendance_df.head())
print("\n--- Sample Marks Data ---")
print(marks_df.head(10))
print("\n--- Sample Fees Data ---")
print(fees_df.head())