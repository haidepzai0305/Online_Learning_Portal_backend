import json
from django.core.management.base import BaseCommand
from myproject.auth_service.app.models.users import User
from myproject.auth_service.app.models.roles import Roles
from myproject.auth_service.app.models.user_roles import UserRoles
from myproject.auth_service.app.models.user_credentials import UserCredentials
from myproject.courses_service.app.models.courses import Course
from myproject.auth_service.app.utils.auth_middleware import jwt_required # Just to ensure path
from django.db import transaction

from myproject.courses_service.app.models.materials import Material, MaterialType

class Command(BaseCommand):
    help = 'Seed database with frontend mock data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")
        
        with transaction.atomic():
            # 1. Ensure Roles exist
            prof_role, _ = Roles.objects.get_or_create(name='professor')
            student_role, _ = Roles.objects.get_or_create(name='student')

            # 2. Extract Instructors from Mock Data
            instructors = [
                "Nguyễn Văn A", "Trần Minh B", "Lê Thị C", "Phạm Văn D", 
                "Hoàng Văn E", "Ngô Thị F", "Vũ Minh G", "Đinh Văn H"
            ]
            
            prof_map = {}
            for name in instructors:
                email = f"{name.replace(' ', '').lower()}@example.com"
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={'username': name}
                )
                if created:
                    UserRoles.objects.get_or_create(user=user, role=prof_role)
                    # Use a default password 'password123'
                    from myproject.auth_service.app.utils.security import get_password_hash
                    UserCredentials.objects.create(user=user, password_hash=get_password_hash("password123"))
                prof_map[name] = user

            # 3. Create Courses
            mock_courses = [
                {
                    "title": "Python từ Zero đến Hero",
                    "instructor": "Nguyễn Văn A",
                    "thumbnail": "https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=400&h=300&fit=crop",
                    "rating": 4.8,
                    "reviewCount": 2543,
                    "duration": "42h 30m",
                    "students": 15420,
                    "price": 499000,
                    "originalPrice": 1299000,
                    "level": "Beginner",
                    "category": "dev",
                    "outcomes": "Python Basics\nAdvanced OOP\nData Scripting",
                    "lessons": [
                        {"title": "Cài đặt môi trường", "video": "https://www.youtube.com/embed/6i3S88uH2I4"},
                        {"title": "Cú pháp cơ bản", "video": "https://www.youtube.com/embed/W0P9Cofv0y0"},
                        {"title": "Biến và kiểu dữ liệu", "video": "https://www.youtube.com/embed/SgqxK0eG7vU"}
                    ]
                },
                {
                    "title": "Ethical Hacking cơ bản",
                    "instructor": "Trần Minh B",
                    "thumbnail": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=400&h=300&fit=crop",
                    "rating": 4.9,
                    "reviewCount": 1876,
                    "duration": "56h 15m",
                    "students": 8932,
                    "price": 799000,
                    "originalPrice": 1899000,
                    "level": "Advanced",
                    "category": "security",
                    "outcomes": "Penetration Testing\nNetwork Security\nExploit Dev",
                    "lessons": [
                        {"title": "Giới thiệu về Cybersecurity", "video": "https://www.youtube.com/embed/Z6691w9c68A"},
                        {"title": "Cài đặt Kali Linux", "video": "https://www.youtube.com/embed/iN_JmXGvmdM"}
                    ]
                },
                {
                    "title": "React & Node.js Full Stack",
                    "instructor": "Lê Thị C",
                    "thumbnail": "https://images.unsplash.com/photo-1627398242454-45a1465c2479?w=400&h=300&fit=crop",
                    "rating": 4.7,
                    "reviewCount": 3421,
                    "duration": "68h 45m",
                    "students": 21543,
                    "price": 699000,
                    "originalPrice": 1599000,
                    "level": "Intermediate",
                    "category": "dev",
                    "outcomes": "React Hooks\nExpress.js API\nDeployment",
                    "lessons": [
                        {"title": "ReactJS Component", "video": "https://www.youtube.com/embed/f79GiYshsv8"},
                        {"title": "State & Props", "video": "https://www.youtube.com/embed/f79GiYshsv8"}
                    ]
                },
                {
                    "title": "Machine Learning với Python",
                    "instructor": "Phạm Văn D",
                    "thumbnail": "https://images.unsplash.com/photo-1555255707-c07966088b7b?w=800&q=80",
                    "rating": 4.9,
                    "reviewCount": 950,
                    "duration": "45h 20m",
                    "students": 5400,
                    "price": 899000,
                    "originalPrice": 1999000,
                    "level": "Advanced",
                    "category": "ai",
                    "outcomes": "Scikit-learn\nNeural Networks\nData Preprocessing",
                    "lessons": [
                        {"title": "Linear Regression", "video": ""},
                        {"title": "Decision Trees", "video": ""}
                    ]
                },
                {
                    "title": "iOS Development với Swift",
                    "instructor": "Hoàng Văn E",
                    "thumbnail": "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=800&q=80",
                    "rating": 4.8,
                    "reviewCount": 1200,
                    "duration": "50h 10m",
                    "students": 7200,
                    "price": 999000,
                    "originalPrice": 2200000,
                    "level": "Intermediate",
                    "category": "mobile",
                    "outcomes": "SwiftUI\nUIKit\niOS Architecture",
                    "lessons": [
                        {"title": "SwiftUI Basics", "video": ""},
                        {"title": "List & Navigation", "video": ""}
                    ]
                },
                {
                    "title": "Trí tuệ nhân tạo (AI) cho người mới bắt đầu",
                    "instructor": "Ngô Thị F",
                    "thumbnail": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=800&q=80",
                    "rating": 4.9,
                    "reviewCount": 4200,
                    "duration": "20h 30m",
                    "students": 32000,
                    "price": 399000,
                    "originalPrice": 999000,
                    "level": "Beginner",
                    "category": "ai",
                    "outcomes": "AI Fundamentals\nGenerative AI\nEthics in AI",
                    "lessons": [
                        {"title": "AI là gì?", "video": ""}
                    ]
                },
                {
                    "title": "ChatGPT & Prompt Engineering Masterclass",
                    "instructor": "Vũ Minh G",
                    "thumbnail": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&q=80",
                    "rating": 4.7,
                    "reviewCount": 8500,
                    "duration": "12h 15m",
                    "students": 56000,
                    "price": 299000,
                    "originalPrice": 799000,
                    "level": "Beginner",
                    "category": "ai",
                    "outcomes": "Advanced Prompts\nAutomation with AI\nAPI Integration",
                    "lessons": [
                        {"title": "Kỹ thuật Prompt", "video": ""}
                    ]
                },
                {
                    "title": "[MỚI] Khóa học toàn diện AWS Certified Cloud Practitioner",
                    "instructor": "Đinh Văn H",
                    "thumbnail": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&q=80",
                    "rating": 4.8,
                    "reviewCount": 21572,
                    "duration": "14h 30m",
                    "students": 128541,
                    "price": 50000,
                    "originalPrice": 699000,
                    "level": "Beginner",
                    "category": "devops",
                    "outcomes": "AWS Services\nCloud Computing\nExam Prep",
                    "lessons": [
                        {"title": "Giới thiệu AWS", "video": ""}
                    ]
                },
                {
                    "title": "Docker & Kubernetes Thực Chiến",
                    "instructor": "Trần Minh B",
                    "thumbnail": "https://images.unsplash.com/photo-1605745341112-8590d221ab9b?w=800&q=80",
                    "rating": 4.9,
                    "reviewCount": 3400,
                    "duration": "35h 00m",
                    "students": 18000,
                    "price": 899000,
                    "originalPrice": 1899000,
                    "level": "Intermediate",
                    "category": "devops",
                    "outcomes": "Containerization\nMicroservices\nK8s Deployment",
                    "lessons": [
                        {"title": "Docker Basics", "video": ""}
                    ]
                },
                {
                    "title": "Khoá Học Toàn Diện Về Phát Triển Web Full-Stack",
                    "instructor": "Nguyễn Văn A",
                    "thumbnail": "https://images.unsplash.com/photo-1547658719-da2b51169166?w=800&q=80",
                    "rating": 4.7,
                    "reviewCount": 465257,
                    "duration": "60h 00m",
                    "students": 1536870,
                    "price": 50000,
                    "originalPrice": 349000,
                    "level": "Beginner",
                    "category": "dev",
                    "outcomes": "HTML/CSS/JS\nReact\nNode.js & MongoDB",
                    "lessons": [
                        {"title": "Javascript ES6", "video": ""}
                    ]
                },
                {
                    "title": "Hướng dẫn Java cho người mới bắt đầu hoàn toàn",
                    "instructor": "Lê Thị C",
                    "thumbnail": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=800&q=80",
                    "rating": 4.4,
                    "reviewCount": 102964,
                    "duration": "28h 15m",
                    "students": 1947586,
                    "price": 50000,
                    "originalPrice": 349000,
                    "level": "Beginner",
                    "category": "dev",
                    "outcomes": "Java Syntax\nOOP in Java\nData Structures",
                    "lessons": [
                        {"title": "Hello World trong Java", "video": ""}
                    ]
                },
                {
                    "title": "Ethical Hacking: Web Application Penetration Testing",
                    "instructor": "Trần Minh B",
                    "thumbnail": "https://images.unsplash.com/photo-1542831371-29b0f74f9713?w=800&q=80",
                    "rating": 4.9,
                    "reviewCount": 1500,
                    "duration": "25h 30m",
                    "students": 12000,
                    "price": 599000,
                    "originalPrice": 1499000,
                    "level": "Advanced",
                    "category": "security",
                    "outcomes": "Web Vulnerabilities\nSQL Injection\nXSS Attacks",
                    "lessons": [{"title": "Web Security 101", "video": ""}]
                },
                {
                    "title": "Network Defense Professional",
                    "instructor": "Đinh Văn H",
                    "thumbnail": "https://images.unsplash.com/photo-1551288560-12961f00a5ce?w=800&q=80",
                    "rating": 4.8,
                    "reviewCount": 980,
                    "duration": "30h 00m",
                    "students": 8500,
                    "price": 699000,
                    "originalPrice": 1599000,
                    "level": "Intermediate",
                    "category": "security",
                    "outcomes": "Firewall Config\nIDS/IPS\nNetwork Hardening",
                    "lessons": [{"title": "Network Security Ops", "video": ""}]
                },
                {
                    "title": "Cyber Security cho người bắt đầu",
                    "instructor": "Vũ Minh G",
                    "thumbnail": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&q=80",
                    "rating": 4.7,
                    "reviewCount": 5600,
                    "duration": "15h 45m",
                    "students": 45000,
                    "price": 0,
                    "originalPrice": 499000,
                    "level": "Beginner",
                    "category": "security",
                    "outcomes": "Identity Management\nBasic Cryptography\nSafety Online",
                    "lessons": [{"title": "Introduction to Cyber", "video": ""}]
                },
                {
                    "title": "Jenkins CI/CD Pipeline Masterclass",
                    "instructor": "Trần Minh B",
                    "thumbnail": "https://images.unsplash.com/photo-1618401471353-b98aadebc25a?w=800&q=80",
                    "rating": 4.8,
                    "reviewCount": 2200,
                    "duration": "18h 20m",
                    "students": 15000,
                    "price": 499000,
                    "originalPrice": 1299000,
                    "level": "Intermediate",
                    "category": "devops",
                    "outcomes": "Build Automation\nPipeline as Code\nCloud Deployments",
                    "lessons": [{"title": "Jenkins Pipelines", "video": ""}]
                },
                {
                    "title": "Quản trị Linux cho DevOps",
                    "instructor": "Hoàng Văn E",
                    "thumbnail": "https://images.unsplash.com/photo-1629654273894-f458e237302c?w=800&q=80",
                    "rating": 4.9,
                    "reviewCount": 1800,
                    "duration": "22h 10m",
                    "students": 11000,
                    "price": 399000,
                    "originalPrice": 999000,
                    "level": "Beginner",
                    "category": "devops",
                    "outcomes": "Bash Scripting\nServer Management\nSSH & Networking",
                    "lessons": [{"title": "Linux Kernel Basics", "video": ""}]
                },
                {
                    "title": "Deep Learning với PyTorch",
                    "instructor": "Phạm Văn D",
                    "thumbnail": "https://images.unsplash.com/photo-1511376777868-611b54f68947?w=800&q=80",
                    "rating": 4.9,
                    "reviewCount": 750,
                    "duration": "40h 00m",
                    "students": 4800,
                    "price": 899000,
                    "originalPrice": 1999000,
                    "level": "Advanced",
                    "category": "ai",
                    "outcomes": "Tensors\nNeural Networks\nComputer Vision",
                    "lessons": [{"title": "Intro to PyTorch", "video": ""}]
                }
            ]

            for c_data in mock_courses:
                course, _ = Course.objects.update_or_create(
                    title=c_data["title"],
                    defaults={
                        "description": f"Full course documentation for {c_data['title']}",
                        "professor": prof_map[c_data["instructor"]],
                        "price": c_data["price"],
                        "original_price": c_data["originalPrice"],
                        "duration": c_data["duration"],
                        "level": c_data["level"],
                        "thumbnail_url": c_data["thumbnail"],
                        "rating": c_data["rating"],
                        "review_count": c_data["reviewCount"],
                        "learning_outcomes": c_data["outcomes"],
                        "category": c_data["category"]
                    }
                )
                
                # Create lessons (Materials)
                for i, lesson in enumerate(c_data["lessons"]):
                    Material.objects.update_or_create(
                        course=course,
                        title=lesson["title"],
                        defaults={
                            "material_type": MaterialType.VIDEO,
                            "video_url": lesson["video"],
                            "content": f"Chào mừng bạn đến với bài học '{lesson['title']}'. Trong bài này, chúng ta sẽ đi sâu vào các khái niệm chính và thực hành các kỹ thuật quan trọng của {c_data['title']}. Hy vọng bạn sẽ có một buổi học thú vị và bổ ích!"
                        }
                    )

            # 4. Generate Courses for all sub-categories to ensure "Danh mục" is populated
            sub_categories_config = {
                "dev": [
                    "Front-end (React, Vue, Next.js)", "Back-end (Node.js, Java, Python)",
                    "Mobile Development (Flutter, iOS)", "Full-stack Web Development",
                    "Game Development (Unity, Unreal)", "Data Science & Analytics"
                ],
                "security": [
                    "Ethical Hacking (White Hat)", "Web Application Security", 
                    "Network Defense & Firewall", "SOC Analyst & Incident Response"
                ],
                "devops": [
                    "Cloud Computing (AWS/Azure/GCP)", "Containers & Docker",
                    "Kubernetes & Orchestration", "CI/CD Automation (Jenkins/GitLab)"
                ],
                "ai": [
                    "Machine Learning Engineering", "Deep Learning Foundations",
                    "Natural Language Processing (NLP)", "Generative AI & LLM (GPT)"
                ]
            }

            for cat_id, sub_list in sub_categories_config.items():
                for sub_name in sub_list:
                    course, _ = Course.objects.update_or_create(
                        title=f"Lộ trình {sub_name} chuyên sâu",
                        defaults={
                            "description": f"Khóa học chuyên sâu về {sub_name}. Bao gồm tài liệu, video và bài tập thực hành.",
                            "professor": prof_map["Nguyễn Văn A"],
                            "price": 499000,
                            "original_price": 999000,
                            "duration": "20h 30m",
                            "level": "Intermediate",
                            "thumbnail_url": f"https://images.unsplash.com/photo-1516116216624-53e697fedbea?w=800&q=80",
                            "rating": 4.8,
                            "review_count": 120,
                            "learning_outcomes": f"Master {sub_name}\nProject Implementation\nBest Practices",
                            "category": cat_id
                        }
                    )
                    
                    # Add distinct materials for each course
                    Material.objects.get_or_create(
                        course=course,
                        title=f"Video bài giảng: {sub_name} cơ bản",
                        defaults={
                            "material_type": MaterialType.VIDEO,
                            "video_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
                            "order": 0
                        }
                    )
                    Material.objects.get_or_create(
                        course=course,
                        title=f"Tài liệu PDF: Hướng dẫn {sub_name}",
                        defaults={
                            "material_type": MaterialType.PDF,
                            "content": f"Đây là nội dung đọc cho khóa học {sub_name}.",
                            "order": 1
                        }
                    )
                    Material.objects.get_or_create(
                        course=course,
                        title=f"Lab thực hành: {sub_name}",
                        defaults={
                            "material_type": MaterialType.OTHER,
                            "content": "Link repo thực hành: https://github.com/studyvn/labs",
                            "order": 2
                        }
                    )

            self.stdout.write(self.style.SUCCESS("Successfully seeded all sub-category courses and materials"))

        self.stdout.write(self.style.SUCCESS("Successfully seeded courses and video lessons!"))

        self.stdout.write(self.style.SUCCESS("Successfully seeded data from mock files!"))
