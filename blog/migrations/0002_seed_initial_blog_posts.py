from django.db import migrations
from django.utils import timezone


def seed_initial_categories_and_posts(apps, schema_editor):
    BlogCategory = apps.get_model("blog", "BlogCategory")
    BlogPost = apps.get_model("blog", "BlogPost")
    User = apps.get_model("auth", "User")

    # Fetch admin user or first available user as author
    author = User.objects.filter(is_superuser=True).first() or User.objects.first()

    categories_data = [
        {
            "name": "Exam Preparation",
            "slug": "exam-preparation",
            "description": "Essential study strategies, past questions guide, and expert advice for WAEC, JAMB (UTME), NECO, and IGCSE exams.",
            "icon": "fa-graduation-cap"
        },
        {
            "name": "Tutoring & Learning Tips",
            "slug": "tutoring-learning-tips",
            "description": "Actionable advice for parents and students on maximizing private tutoring sessions and building solid study habits.",
            "icon": "fa-chalkboard-user"
        },
        {
            "name": "Parenting & Education in Nigeria",
            "slug": "parenting-education-nigeria",
            "description": "Insights for Nigerian parents navigating academic excellence, school selection, and home lesson planning.",
            "icon": "fa-people-roof"
        },
        {
            "name": "STEM & Future Skills",
            "slug": "stem-future-skills",
            "description": "Guidance on Mathematics, Sciences, Coding, and digital literacy skills for young learners.",
            "icon": "fa-code"
        }
    ]

    created_cats = {}
    for cat_data in categories_data:
        cat, _ = BlogCategory.objects.get_or_create(
            slug=cat_data["slug"],
            defaults=cat_data
        )
        created_cats[cat.slug] = cat

    if BlogPost.objects.count() == 0:
        posts_data = [
            {
                "title": "How to Score 300+ in JAMB UTME & Ace WAEC in One Sitting (2026 Comprehensive Guide)",
                "slug": "how-to-score-300-in-jamb-utme-and-ace-waec",
                "category": created_cats.get("exam-preparation"),
                "is_featured": True,
                "image_url": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&w=1200&q=80",
                "excerpt": "Discover proven study schedules, CBT test techniques, and subject-specific hacks used by top 1% Nigerian students to crush JAMB and secure straight A's in WAEC.",
                "content": """
<h2>Why Early Preparation Matters for WAEC & JAMB</h2>
<p>Every year, over 1.8 million candidates sit for the Joint Admissions and Matriculation Board (JAMB) UTME and the West African Senior School Certificate Examination (WAEC). While the competition for top university courses like Medicine, Law, Software Engineering, and Accounting in Nigeria is fierce, scoring above 300 in JAMB and bagging 7+ A1 distinctions in WAEC is very achievable with the right strategy.</p>

<h3>1. Master the Official JAMB & WAEC Syllabus</h3>
<p>Never read blindly without consulting the official exam syllabus. The syllabus outlines exact topics, recommended textbooks, and key sub-areas where questions are frequently drawn.</p>
<ul>
  <li><strong>Highlight High-Yield Topics:</strong> In Mathematics, topics like Calculus, Matrices, Trigonometry, and Statistics appear consistently. In Physics, Mechanics, Waves, and Current Electricity carry heavy weights.</li>
  <li><strong>Cover Gaps Early:</strong> Do not skip difficult topics. Instead, seek help from a qualified home lesson teacher or subject specialist.</li>
</ul>

<h3>2. Practice with Timed CBT Past Questions</h3>
<p>JAMB is a speed and accuracy test. You have only 2 hours to answer 180 questions across 4 subjects. Practicing with timer-based CBT software builds your confidence and trains you to allocate roughly 35-40 seconds per question.</p>

<h3>3. The Power of 1-on-1 Personalized Tutoring</h3>
<p>Group classes in crowded tutorial centers often move too fast or too slow for individual learning curves. A vetted, private tutor assesses your specific weak spots, tailors explanations to your learning style, and holds you accountable weekly.</p>
<blockquote>
  <p>"Personalized tutoring bridges the gap between passive reading and deep understanding, resulting in a 40% average boost in student test scores."</p>
</blockquote>

<h3>Key Takeaways for Exam Success:</h3>
<ol>
  <li>Start full-scale revision at least 4-6 months before the exam date.</li>
  <li>Solve past questions from the last 15 years to identify repeating question patterns.</li>
  <li>Book a verified private tutor on MyteacherConnect to tackle stubborn topics in Math, English, Chemistry, and Physics.</li>
</ol>
                """,
                "meta_title": "How to Score 300+ in JAMB & Ace WAEC (2026 Guide) | MyteacherConnect",
                "meta_description": "Comprehensive guide for Nigerian students on how to score 300+ in JAMB UTME and pass WAEC with distinctions. Study hacks, CBT tips, and private tutoring insights.",
                "meta_keywords": "score 300 in jamb, pass waec in one sitting, jamb utme tips 2026, waec past questions, private jamb tutor lagos, port harcourt waec teacher",
                "status": "published",
                "estimated_read_time": 5,
                "published_at": timezone.now(),
            },
            {
                "title": "7 Big Advantages of Hiring a Verified Home Tutor in Lagos, Port Harcourt & Abuja",
                "slug": "advantages-of-hiring-verified-home-tutor-nigeria",
                "category": created_cats.get("tutoring-learning-tips"),
                "is_featured": False,
                "image_url": "https://images.unsplash.com/photo-1577896851231-70ef18881754?auto=format&fit=crop&w=1200&q=80",
                "excerpt": "From personalized pacing to safe background-checked educators, explore why Nigerian parents are increasingly switching to AI-matched home tutoring.",
                "content": """
<h2>Why Nigerian Parents Choose Private Home Tutoring</h2>
<p>As classroom sizes in private and public schools expand, teachers rarely have the luxury of giving individualized attention to 30 or 40 pupils at once. For parents residing in bustling metropolitan cities like Lagos (Lekki, Ikeja, Surulere), Port Harcourt (GRA, Peter Odili, Woji), and Abuja (Maitama, Gwarinpa), hiring a dedicated private home tutor is the ultimate investment in their child's academic confidence.</p>

<h3>1. Custom Paced Learning</h3>
<p>Every child grasps concepts differently. In a 1-on-1 setting, if a student struggles with algebraic equations or French grammar, the tutor can spend extra sessions explaining with real-world analogies until mastery is achieved.</p>

<h3>2. Safety and Background Verification</h3>
<p>Inviting an educator into your residence requires utmost trust. On platforms like <strong>MyteacherConnect</strong>, all tutors undergo strict identity verification, academic credential checks, and address verification before being deployed to client homes.</p>

<h3>3. Flexible Scheduling in the Comfort of Home</h3>
<p>Eliminate stressful after-school traffic commutes. Your child learns in a relaxed, familiar home environment during convenient weekday evenings or weekend mornings.</p>

<h3>4. Regular Feedback and Measurable Progress Tracking</h3>
<p>Private tutors provide parents with continuous feedback after every lesson milestone, making it easy to see measurable grade improvements in term exams and continuous assessments.</p>
                """,
                "meta_title": "7 Advantages of Hiring a Home Tutor in Lagos & PH | MyteacherConnect",
                "meta_description": "Learn the 7 major benefits of private home lesson tutors in Nigeria. Background-checked educators in Port Harcourt, Lagos, and Abuja for primary and secondary students.",
                "meta_keywords": "home tutor lagos, private lesson teacher port harcourt, hire tutor abuja, best home lesson teacher, vetted private tutor nigeria",
                "status": "published",
                "estimated_read_time": 4,
                "published_at": timezone.now(),
            },
            {
                "title": "How Smart AI Matching is Revolutionizing Private Education in Nigeria",
                "slug": "how-ai-matching-is-revolutionizing-private-education-nigeria",
                "category": created_cats.get("stem-future-skills"),
                "is_featured": False,
                "image_url": "https://images.unsplash.com/photo-1509062522246-3755977927d7?auto=format&fit=crop&w=1200&q=80",
                "excerpt": "Learn how MyteacherConnect uses intelligent AI matching algorithms to pair students with their ideal subject tutors based on location, curriculum, and learning needs.",
                "content": """
<h2>Moving Beyond Word-of-Mouth Tutor Hiring</h2>
<p>Historically, finding a reliable home lesson teacher in Nigeria relied on informal word-of-mouth recommendations or unverified agency boards. Often, the matched tutor lacked the specific subject expertise (such as British Curriculum, IGCSE, or Advanced Python Coding) or lived too far away to maintain punctuality.</p>

<h3>How AI-Powered Matching Works</h3>
<p>At <strong>MyteacherConnect</strong>, our intelligent recommendation engine analyzes multiple data points in real time:</p>
<ul>
  <li><strong>Curriculum Fit:</strong> Matches students strictly with tutors experienced in Nigerian National Curriculum, British/Cambridge, or American syllabi.</li>
  <li><strong>Geo-Proximity:</strong> Recommends top-rated tutors situated within your city zone (e.g. Port Harcourt, Ikeja, Lekki, Abuja Central) to guarantee consistency.</li>
  <li><strong>Learning Style Alignment:</strong> Pairs visual, auditory, and kinesthetic learners with teaching styles that spark genuine passion for STEM and humanities.</li>
</ul>

<h3>Try It Today</h3>
<p>Whether you need a tutor for Primary common entrance, Junior WAEC, Senior Secondary Sciences, or coding languages like Scratch & Python, our platform connects you with the perfect educator in under 60 seconds.</p>
                """,
                "meta_title": "How AI Matching Connects Parents with Best Tutors | MyteacherConnect",
                "meta_description": "Discover how AI-driven matching connects Nigerian parents and students with vetted, top-tier private tutors for WAEC, JAMB, Coding, and British Curriculum.",
                "meta_keywords": "ai tutor matching nigeria, find private teacher, online tutor lagos, port harcourt lesson teacher, edtech nigeria",
                "status": "published",
                "estimated_read_time": 4,
                "published_at": timezone.now(),
            }
        ]

        for post_data in posts_data:
            BlogPost.objects.create(
                author=author,
                **post_data
            )


def rollback_seed(apps, schema_editor):
    BlogPost = apps.get_model("blog", "BlogPost")
    BlogCategory = apps.get_model("blog", "BlogCategory")
    BlogPost.objects.all().delete()
    BlogCategory.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_initial_categories_and_posts, rollback_seed),
    ]
