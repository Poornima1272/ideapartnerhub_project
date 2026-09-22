from django.db import models
from django.contrib.auth.models import User



class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name="student_profile")
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    college = models.CharField(max_length=150)
    skill = models.CharField(max_length=150, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.college})"

    class Meta:
        ordering = ["-created_at"]


class Investor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name="investor_profile")
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    occupation = models.CharField(max_length=150)
    interest_area = models.CharField(max_length=150, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.occupation})"

    class Meta:
        ordering = ["-created_at"]


class Idea(models.Model):
    STAGE_CHOICES = [
        ("idea", "Sirf idea hai"),
        ("prototype", "Prototype ban raha hai"),
        ("mvp", "MVP ready hai"),
        ("scaling", "Users hain, ab scale karna hai"),
    ]

    CATEGORY_CHOICES = [
        ("tech", "Tech / SaaS"),
        ("ecommerce", "E-commerce"),
        ("service", "Service / booking"),
        ("education", "Education"),
        ("health", "Health"),
        ("other", "Doosra"),
    ]

    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True, related_name="ideas")

    title = models.CharField(max_length=200, default="")
    description = models.TextField(default="")
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default="idea")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="tech")
    help_needed = models.CharField(max_length=200, blank=True)

    name = models.CharField(max_length=100, default="")
    college = models.CharField(max_length=150, blank=True)
    contact = models.CharField(max_length=150, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    def help_needed_list(self):
        return [h.strip() for h in self.help_needed.split(",") if h.strip()]

    def __str__(self):
        return f"{self.title} — {self.name}"

    class Meta:
        ordering = ["-created_at"]


        # Is model ko models.py ke bilkul niche add karein
class ConnectionRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending (Aapko check karna hai)"),
        ("connected", "Connected (Aapne milva diya)"),
        ("rejected", "Rejected (Aapne mana kar diya)"),
    ]

    investor = models.ForeignKey(Investor, on_delete=models.CASCADE, related_name="sent_requests")
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name="connection_requests")
    
    # Investor apna koi note ya message likhna chahe toh

    message_by_investor = models.TextField(blank=True)

    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.investor.name} wants to connect with {self.idea.title}"

    class Meta:
        ordering = ["-created_at"]

        # Is exact code ko check karein aur models.py ke bilkul niche daal kar save karein:

class TeamFinder(models.Model):
    TEAM_STATUS = [
        ("looking", "Looking for Teammate (Teammate dhoondh raha hai)"),
        ("matched", "Matched / Team Formed (Team ban gayi hai)"),
        ("closed", "Closed (Band ho gaya)"),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="team_profiles")
    hackathon_name = models.CharField(max_length=200)
    my_role = models.CharField(max_length=100)
    looking_for = models.CharField(max_length=200)
    project_description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=TEAM_STATUS, default="looking")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} — Looking for {self.looking_for}"

    class Meta:
        ordering = ["-created_at"]

