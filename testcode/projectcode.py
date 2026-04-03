"""
Project Management System - User Module
This module handles user authentication and profile management
"""
# 這是用來自己測試的code，與專案無關
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional


class User:
    """Represents a user in the project management system"""
    
    def __init__(self, user_id: int, email: str, name: str, password: str):
        """Initialize a new user
        
        Args:
            user_id: Unique identifier for the user
            email: User's email address
            name: User's display name
            password: User's password (should be hashed)
        """
        self.user_id = user_id
        self.email = email
        self.name = name
        self.password = self._hash_password(password)
        self.created_at = datetime.now()
        self.projects = []
        self.is_active = True
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256 algorithm
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password as hexadecimal string
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """Verify if provided password matches stored password
        
        Args:
            password: Password to verify
            
        Returns:
            True if password matches, False otherwise
        """
        return self.password == self._hash_password(password)
    
    def add_project(self, project: 'Project') -> None:
        """Add a project to user's project list
        
        Args:
            project: Project object to add
        """
        if project not in self.projects:
            self.projects.append(project)
    
    def get_user_info(self) -> Dict:
        """Get user information as dictionary
        
        Returns:
            Dictionary containing user information
        """
        return {
            'id': self.user_id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'project_count': len(self.projects),
            'is_active': self.is_active
        }


class Project:
    """Represents a project in the system"""
    
    def __init__(self, project_id: int, name: str, owner: User):
        """Initialize a new project
        
        Args:
            project_id: Unique identifier for the project
            name: Project name
            owner: User object who owns the project
        """
        self.project_id = project_id
        self.name = name
        self.owner = owner
        self.members = [owner]
        self.created_at = datetime.now()
        self.description = ""
        self.files = []
    
    def add_member(self, user: User) -> bool:
        """Add a member to the project
        
        Args:
            user: User object to add
            
        Returns:
            True if successfully added, False if already a member
        """
        if user not in self.members:
            self.members.append(user)
            user.add_project(self)
            return True
        return False
    
    def remove_member(self, user: User) -> bool:
        """Remove a member from the project
        
        Args:
            user: User object to remove
            
        Returns:
            True if successfully removed, False if not a member
        """
        if user in self.members and user != self.owner:
            self.members.remove(user)
            return True
        return False
    
    def upload_file(self, filename: str, content: str) -> Dict:
        """Upload a file to the project
        
        Args:
            filename: Name of the file
            content: Content of the file
            
        Returns:
            Dictionary with file information
        """
        file_obj = {
            'id': len(self.files) + 1,
            'name': filename,
            'content': content,
            'uploaded_at': datetime.now().isoformat(),
            'size': len(content)
        }
        self.files.append(file_obj)
        return file_obj
    
    def get_project_info(self) -> Dict:
        """Get project information
        
        Returns:
            Dictionary containing project information
        """
        return {
            'id': self.project_id,
            'name': self.name,
            'owner': self.owner.name,
            'member_count': len(self.members),
            'file_count': len(self.files),
            'created_at': self.created_at.isoformat(),
            'description': self.description
        }


class CodeReview:
    """Handles code review functionality"""
    
    def __init__(self):
        """Initialize code review system"""
        self.comments = []
        self.reviews = []
    
    def add_comment(self, file_id: int, line_number: int, author: User, text: str) -> Dict:
        """Add a comment to a specific line in a file
        
        Args:
            file_id: ID of the file
            line_number: Line number to comment on
            author: User making the comment
            text: Comment text
            
        Returns:
            Dictionary with comment information
        """
        comment = {
            'id': len(self.comments) + 1,
            'file_id': file_id,
            'line_number': line_number,
            'author': author.name,
            'text': text,
            'created_at': datetime.now().isoformat(),
            'status': 'open'
        }
        self.comments.append(comment)
        return comment
    
    def get_file_comments(self, file_id: int) -> List[Dict]:
        """Get all comments for a specific file
        
        Args:
            file_id: ID of the file
            
        Returns:
            List of comments for the file
        """
        return [c for c in self.comments if c['file_id'] == file_id]
    
    def resolve_comment(self, comment_id: int) -> bool:
        """Mark a comment as resolved
        
        Args:
            comment_id: ID of the comment to resolve
            
        Returns:
            True if successfully resolved, False otherwise
        """
        for comment in self.comments:
            if comment['id'] == comment_id:
                comment['status'] = 'resolved'
                return True
        return False


def main():
    """Main function to demonstrate the system"""
    
    # Create test users
    user1 = User(1, 'alice@example.com', 'Alice', 'password123')
    user2 = User(2, 'bob@example.com', 'Bob', 'password456')
    
    # Create a project
    project = Project(1, 'Test Project', user1)
    project.description = "A test project for demonstrating the system"
    
    # Add team members
    project.add_member(user2)
    
    # Upload test files
    code_content = """def calculate_sum(numbers):
    \"\"\"Calculate sum of numbers\"\"\"
    total = 0
    for num in numbers:
        total += num
    return total

def calculate_average(numbers):
    \"\"\"Calculate average of numbers\"\"\"
    if len(numbers) == 0:
        return 0
    return calculate_sum(numbers) / len(numbers)

# Test the functions
test_data = [1, 2, 3, 4, 5]
print(f"Sum: {calculate_sum(test_data)}")
print(f"Average: {calculate_average(test_data)}")
"""
    
    project.upload_file('calculator.py', code_content)
    
    # Perform code review
    review = CodeReview()
    review.add_comment(1, 5, user2, "Consider using sum() built-in function")
    review.add_comment(1, 11, user1, "Good implementation! Consider adding error handling")
    
    # Print project information
    print("Project Information:")
    print(json.dumps(project.get_project_info(), indent=2))
    
    print("\nUser Information:")
    print(json.dumps(user1.get_user_info(), indent=2))
    
    print("\nFile Comments:")
    for comment in review.get_file_comments(1):
        print(f"  Line {comment['line_number']} - {comment['author']}: {comment['text']}")


if __name__ == "__main__":
    main()
    print("\nTest code execution completed successfully!")
