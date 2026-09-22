

# Create your views here.

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Idea, Student, Investor

from django.shortcuts import get_object_or_404
from .models import ConnectionRequest, Idea, Investor , TeamFinder

from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout


template_name = "registration/signup.html"

def home(request):
    return render(request, "index.html")


def signup(request):
    return render(request, "Signup.html")


def student_signup(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        college = request.POST.get("college", "").strip()

        if not name or not phone or not college:
            messages.error(request, "Kripya naam, phone aur college bharo.")
            return render(request, "Student signup.html")

        student = Student.objects.create(
            name=name,
            phone=phone,
            email=request.POST.get("email", "").strip(),
            college=college,
            skill=request.POST.get("skill", "").strip(),
        )
        request.session["student_id"] = student.id
        messages.success(request, f"Welcome {student.name}! Ab apni idea post karo.")
        return redirect("post_idea")

    return render(request, "Student signup.html")


def investor_signup(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        occupation = request.POST.get("occupation", "").strip()

        if not name or not phone or not occupation:
            messages.error(request, "Kripya naam, phone aur occupation bharo.")
            return render(request, "Investor signup.html")

        Investor.objects.create(
            name=name,
            phone=phone,
            email=request.POST.get("email", "").strip(),
            occupation=occupation,
            interest_area=request.POST.get("interest_area", "").strip(),
        )
        messages.success(request, f"Welcome {name}! Ab ideas browse karo.")
        return redirect("dashboard")

    return render(request, "Investor signup.html")


def post_idea(request):
    student = None
    student_id = request.session.get("student_id")
    if student_id:
        student = Student.objects.filter(id=student_id).first()

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        name = request.POST.get("name", "").strip()
        contact = request.POST.get("contact", "").strip()

        if not title or not description or not name or not contact:
            messages.error(request, "Kripya saare zaroori fields bharo.")
            return render(request, "prtapp/post-idea.html", {"student": student})

        help_tags = request.POST.getlist("help_needed")

        Idea.objects.create(
            student=student,
            title=title,
            description=description,
            stage=request.POST.get("stage", "idea"),
            category=request.POST.get("category", "tech"),
            help_needed=",".join(help_tags),
            name=name,
            college=request.POST.get("college", "").strip(),
            contact=contact,
        )
        messages.success(request, "Tumhari idea successfully post ho gayi!")
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
        # 1. Jis idea par click hua hai use database se nikaalein
        idea = get_object_or_404(Idea, id=idea_id)
        
        # 2. Abhi ke liye hum dummy investor_id session se le rahe hain ya direct pehla investor utha rahe hain.
        # (Jab hum real login system banayenge tab request.user se real investor milega)
        investor = Investor.objects.first() 
        
        if not investor:
            messages.error(request, "Koi investor account nahi mila. Kripya pehle sign up karein.")
            return redirect("dashboard")
            
        # 3. Check karein ki is investor ne pehle se request toh nahi bheji hai
        already_requested = ConnectionRequest.objects.filter(investor=investor, idea=idea).exists()
        
        if already_requested:
            messages.warning(request, "Aapne is idea ke liye pehle hi interest express kar diya hai.")
        else:
            # 4. Naya request database mein save karein jiska status 'pending' hoga
            ConnectionRequest.objects.create(
                investor=investor,
                idea=idea,
                message_by_investor="I am interested in this idea. Please arrange a meeting.",
                status="pending"
            )
            messages.success(request, f"Thank you! Aapka interest hamare paas save ho gaya hai. Hum jald hi aapse aur student se connect karenge.")
            
        return redirect("dashboard")
        
    return redirect("dashboard")

# Is function ko views.py ke bilkul niche add karein (agar pehle se nahi hai)
def find_team_register(request):
    student_id = request.session.get("student_id")
    student = None
    if student_id:
        student = Student.objects.filter(id=student_id).first()

    if request.method == "POST":
        hackathon_name = request.POST.get("hackathon_name", "").strip()
        my_role = request.POST.get("my_role", "").strip()
        looking_for = request.POST.get("looking_for", "").strip()
        project_description = request.POST.get("project_description", "").strip()

        if not hackathon_name or not my_role or not looking_for:
            messages.error(request, "Kripya Hackathon ka naam, apni skill, aur teammate ki requirement zaroor bharein.")
            return render(request, "Find-team.html", {"student": student})

        if not student:
            student = Student.objects.first() # Testing ke liye pehla student utha rahe hain

        if not student:
            messages.error(request, "Koi student account nahi mila. Kripya pehle student register karein.")
            return redirect("signup")

        # Database (MySQL) mein save karna
        TeamFinder.objects.create(
            student=student,
            hackathon_name=hackathon_name,
            my_role=my_role,
            looking_for=looking_for,
            project_description=project_description,
            status="looking"
        )
        messages.success(request, "Aapki requirement save ho gayi hai! Hub Admin jald hi aapke liye sahi teammate dhoondh kar connect karega.")
        return redirect("home")

    return render(request, "Find-team.html", {"student": student})


def student_signup(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        college = request.POST.get("college", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "") # Naya password field

        if not name or not phone or not college or not password:
            messages.error(request, "Please enter your name, phone, college, and password.")
            return render(request, "Student signup.html")

        # 1. Pehle Django ka main secure User banayein (username email hi rakh rahe hain)
        if User.objects.filter(username=email).exists():
            messages.error(request, "This email is already registered. Please login.")
            return render(request, "Student signup.html")
            
        user = User.objects.create_user(username=email, email=email, password=password)
        
        # 2. Ab student profile banayein aur use is user se link kar dein
        student = Student.objects.create(
            user=user,
            name=name,
            phone=phone,
            email=email,
            college=college,
            skill=request.POST.get("skill", "").strip(),
        )
        
        # 3. User ko automatic login karwa dein
        login(request, user)
        
        request.session["student_id"] = student.id
        messages.success(request, f"Welcome {student.name}! Your account is created. Post your idea now.")
        return redirect("post_idea")

    return render(request, "Student signup.html")


def investor_signup(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        occupation = request.POST.get("occupation", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "") # Naya password field

        if not name or not phone or not occupation or not password:
            messages.error(request, "Please enter your name, phone, occupation, and password.")
            return render(request, "Investor signup.html")

        # 1. Pehle Django ka main secure User banayein
        if User.objects.filter(username=email).exists():
            messages.error(request, "This email is already registered. Please login.")
            return render(request, "Investor signup.html")
            
        user = User.objects.create_user(username=email, email=email, password=password)

        # 2. Investor profile banayein aur use is user se link karein
        investor = Investor.objects.create(
            user=user,
            name=name,
            phone=phone,
            email=email,
            occupation=occupation,
            interest_area=request.POST.get("interest_area", "").strip(),
        )
        
        # 3. User ko automatic login karwa dein
        login(request, user)
        
        messages.success(request, f"Welcome {name}! Your account is created. Browse ideas now.")
        return redirect("dashboard")

    return render(request, "Investor signup.html")


# Add this at the bottom of your views.py

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        if not email or not password:
            messages.error(request, "Please enter both email and password.")
            return render(request, "login.html")

        # Django authenticates using the username field (which we set as email during signup)
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back!")
            
            # Redirect based on user profile type
            if hasattr(user, 'student_profile'):
                request.session["student_id"] = user.student_profile.id
                return redirect("post_idea")
            elif hasattr(user, 'investor_profile'):
                return redirect("dashboard")
            else:
                return redirect("home")
        else:
            messages.error(request, "Invalid email or password. Please try again.")
            return render(request, "login.html")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("home")
