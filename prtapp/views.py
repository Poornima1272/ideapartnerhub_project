
import os
import random
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from .models import Idea, Student, Investor, ConnectionRequest, TeamFinder


def send_otp_email(to_email, user_name, otp):
    api_key = os.environ.get("BREVO_API_KEY", "").strip()
    if not api_key:
        return False, "BREVO_API_KEY is missing in Render Environment!"

    url = "https://brevo.com"

    headers = {
        "accept": "application/json",
        "api-key": os.environ.get("BREVO_API_KEY", "").strip(),
        "content-type": "application/json",
    }
    data = {
        "sender": {"name": "IdeaPartnerHub", "email": "annumishra4432@gmail.com"},
        "to": [{"email": to_email, "name": user_name}],
        "subject": "Your IdeaPartnerHub Verification OTP",
        "htmlContent": f"<h3>Hi {user_name},</h3><p>Your 6-digit OTP is: <strong style='font-size:22px; color:#4f46e5;'>{otp}</strong></p>",
    }
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        if response.status_code in (200, 201, 202):
            return True, "Sent"
        return False, f"Brevo Error ({response.status_code}): {response.text}"
    except Exception as e:
        return False, str(e)

        

def home(request):
    return render(request, "index.html", {
        "ideas_count": Idea.objects.count(),
        "investors_count": Investor.objects.count(),
        "students_count": Student.objects.count(),
    })


def signup(request):
    return render(request, "Signup.html")


def student_signup(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        college = request.POST.get("college", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        skill = request.POST.get("skill", "").strip()

        if not name or not phone or not college or not email or not password:
            messages.error(request, "Please fill all fields including Email for OTP verification.")
            return render(request, "Student signup.html")

        if email and User.objects.filter(username__iexact=email).exists():
            messages.error(request, "This email is already registered. Please log in.")
            return render(request, "Student signup.html")

        otp = str(random.randint(100000, 999999))
        request.session["signup_data"] = {
            "role": "student",
            "name": name,
            "phone": phone,
            "college": college,
            "email": email,
            "password": password,
            "skill": skill,
        }
        request.session["signup_otp"] = otp

        if send_otp_email(email, name, otp):
            messages.success(request, f"We have sent a 6-digit OTP to {email}.")
            return redirect("verify_otp")
        else:
            messages.error(request, "Could not send OTP email. Please check your email address and try again.")
            return render(request, "Student signup.html")

    return render(request, "Student signup.html")


def investor_signup(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        occupation = request.POST.get("occupation", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        interest_area = request.POST.get("interest_area", "").strip()

        if not name or not phone or not occupation or not email or not password:
            messages.error(request, "Please fill all fields including Email for OTP verification.")
            return render(request, "Investor signup.html")

        if email and User.objects.filter(username__iexact=email).exists():
            messages.error(request, "This email is already registered. Please log in.")
            return render(request, "Investor signup.html")

        otp = str(random.randint(100000, 999999))
        request.session["signup_data"] = {
            "role": "investor",
            "name": name,
            "phone": phone,
            "occupation": occupation,
            "email": email,
            "password": password,
            "interest_area": interest_area,
        }
        request.session["signup_otp"] = otp

        if send_otp_email(email, name, otp):
            messages.success(request, f"We have sent a 6-digit OTP to {email}.")
            return redirect("verify_otp")
        else:
            messages.error(request, "Could not send OTP email. Please check your email address and try again.")
            return render(request, "Investor signup.html")

    return render(request, "Investor signup.html")


def verify_otp(request):
    signup_data = request.session.get("signup_data")
    saved_otp = request.session.get("signup_otp")

    if not signup_data or not saved_otp:
        messages.error(request, "Session expired. Please sign up again.")
        return redirect("signup")

    if request.method == "POST":
        entered_otp = request.POST.get("otp", "").strip()

        if entered_otp == saved_otp:
            user = User.objects.create_user(
                username=signup_data["email"],
                email=signup_data["email"],
                password=signup_data["password"],
            )

            if signup_data["role"] == "student":
                student = Student.objects.create(
                    user=user,
                    name=signup_data["name"],
                    phone=signup_data["phone"],
                    email=signup_data["email"],
                    college=signup_data["college"],
                    skill=signup_data["skill"],
                )
                login(request, user)
                request.session["student_id"] = student.id
                del request.session["signup_data"]
                del request.session["signup_otp"]
                messages.success(request, f"Email verified! Welcome {student.name}.")
                return redirect("post_idea")

            elif signup_data["role"] == "investor":
                Investor.objects.create(
                    user=user,
                    name=signup_data["name"],
                    phone=signup_data["phone"],
                    email=signup_data["email"],
                    occupation=signup_data["occupation"],
                    interest_area=signup_data["interest_area"],
                )
                login(request, user)
                del request.session["signup_data"]
                del request.session["signup_otp"]
                messages.success(request, f"Email verified! Welcome {signup_data['name']}.")
                return redirect("dashboard")
        else:
            messages.error(request, "Invalid OTP. Please check your email and try again.")

    return render(request, "verify_otp.html", {"email": signup_data["email"]})


def post_idea(request):
    student = getattr(request.user, "student_profile", None) if request.user.is_authenticated else None
    if not student and request.session.get("student_id"):
        student = Student.objects.filter(id=request.session.get("student_id")).first()

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        name = request.POST.get("name", "").strip()
        contact = request.POST.get("contact", "").strip()

        if not title or not description or not name or not contact:
            messages.error(request, "Please fill in all the required fields.")
            return render(request, "Post-idea.html", {"student": student})

        help_tags = request.POST.getlist("help_needed")

        Idea.objects.create(
            student=student,
            title=title,
            description=description,
            stage=request.POST.get("stage", "idea"),
            category=request.POST.get("category", "tech"),
            help_needed=",".join(help_tags),
            name=name,
            college=student.college if student else request.POST.get("college", "").strip(),
            contact=contact,
        )
        messages.success(request, "Your idea has been posted successfully!")
        return redirect("post_idea")

    return render(request, "Post-idea.html", {"student": student})


def dashboard(request):
    ideas = Idea.objects.all()
    category = request.GET.get("category")
    stage = request.GET.get("stage")
    search = request.GET.get("search")

    if category:
        ideas = ideas.filter(category=category)
    if stage:
        ideas = ideas.filter(stage=stage)
    if search:
        ideas = ideas.filter(title__icontains=search)

    return render(request, "Dashboard.html", {
        "ideas": ideas,
        "stage_choices": Idea.STAGE_CHOICES,
        "category_choices": Idea.CATEGORY_CHOICES,
    })


def express_interest(request, idea_id):
    if request.method == "POST":
        idea = get_object_or_404(Idea, id=idea_id)
        investor = getattr(request.user, "investor_profile", None) if request.user.is_authenticated else Investor.objects.first()

        if not investor:
            messages.error(request, "No investor account found. Please sign up first.")
            return redirect("dashboard")

        already_requested = ConnectionRequest.objects.filter(investor=investor, idea=idea).exists()

        if already_requested:
            messages.warning(request, "You have already expressed interest for this idea.")
        else:
            ConnectionRequest.objects.create(
                investor=investor,
                idea=idea,
                message_by_investor="I am interested in this idea. Please arrange a meeting.",
                status="pending",
            )
            messages.success(request, "Thank you! Your interest has been saved. We will connect you soon.")

        return redirect("dashboard")

    return redirect("dashboard")


def find_team_register(request):
    return render(request, "Post-idea.html", {"student": student})


def dashboard(request):
    ideas = Idea.objects.all()
    category = request.GET.get("category")
    stage = request.GET.get("stage")
    search = request.GET.get("search")

    if category:
        ideas = ideas.filter(category=category)
    if stage:
        ideas = ideas.filter(stage=stage)
    if search:
        ideas = ideas.filter(title__icontains=search)

    return render(request, "Dashboard.html", {
        "ideas": ideas,
        "stage_choices": Idea.STAGE_CHOICES,
        "category_choices": Idea.CATEGORY_CHOICES,
    })


def express_interest(request, idea_id):
    if request.method == "POST":
        idea = get_object_or_404(Idea, id=idea_id)
        investor = getattr(request.user, "investor_profile", None) if request.user.is_authenticated else Investor.objects.first()

        if not investor:
            messages.error(request, "No investor account found. Please sign up first.")
            return redirect("dashboard")

        already_requested = ConnectionRequest.objects.filter(investor=investor, idea=idea).exists()

        if already_requested:
            messages.warning(request, "You have already expressed interest for this idea.")
        else:
            ConnectionRequest.objects.create(
                investor=investor,
                idea=idea,
                message_by_investor="I am interested in this idea. Please arrange a meeting.",
                status="pending",
            )
            messages.success(request, "Thank you! Your interest has been saved. We will connect you soon.")

        return redirect("dashboard")

    return redirect("dashboard")


def find_team_register(request):
    student = getattr(request.user, "student_profile", None) if request.user.is_authenticated else None
    if not student and request.session.get("student_id"):
        student = Student.objects.filter(id=request.session.get("student_id")).first()

    if not student:
        messages.error(request, "To find a teammate, please first do Student Signup/Login.")
        return redirect("student_signup")

    if request.method == "POST":
        hackathon_name = request.POST.get("hackathon_name", "").strip()
        my_role = request.POST.get("my_role", "").strip()
        looking_for = request.POST.get("looking_for", "").strip()
        project_description = request.POST.get("project_description", "").strip()

        if not hackathon_name or not my_role or not looking_for:
            messages.error(request, "Please fill in the hackathon name, your skill, and the teammate requirement.")
            return render(request, "Find-team.html", {"student": student})

        TeamFinder.objects.create(
            student=student,
            hackathon_name=hackathon_name,
            my_role=my_role,
            looking_for=looking_for,
            project_description=project_description,
            status="looking",
        )
        messages.success(request, "Your requirement has been saved successfully!")
        return redirect("home")

    return render(request, "Find-team.html", {"student": student})


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        if not email or not password:
            messages.error(request, "Please enter both email and password.")
            return render(request, "login.html")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Welcome back!")
            if hasattr(user, "student_profile"):
                request.session["student_id"] = user.student_profile.id
                return redirect("post_idea")
            elif hasattr(user, "investor_profile"):
                return redirect("dashboard")
            return redirect("home")
        else:
            messages.error(request, "Invalid email or password. Please try again.")
            return render(request, "login.html")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("home")


def my_profile(request):
    if not request.user.is_authenticated:
        messages.error(request, "Please log in first to view your profile.")
        return redirect("login")

    student = getattr(request.user, "student_profile", None)
    investor = getattr(request.user, "investor_profile", None)
    my_ideas = Idea.objects.filter(student=student) if student else []

    return render(request, "profile.html", {
        "student": student,
        "investor": investor,
        "my_ideas": my_ideas,
    })
